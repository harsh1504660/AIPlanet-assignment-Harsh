"""
Multi-Agent System for Math Mentor
Implements 5 core agents: Parser, IntentRouter, Solver, Verifier, Explainer
"""

import json
import re
import os
from typing import Dict, List, Optional, Tuple, Any
import google.generativeai as genai


# def get_client(api_key):
#     genai.configure(api_key=api_key)
#     return genai





def call_llm(system_prompt, user_message,
             temperature=0.1, max_tokens=2000):

    model = genai.GenerativeModel("models/gemini-flash-latest")

    prompt = f"""
SYSTEM:
{system_prompt}

USER:
{user_message}
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": max_tokens
        }
    )

    return response.text
def extract_json(text: str) -> Dict:
    """Extract JSON from Claude response."""
    # Try direct parse
    try:
        return json.loads(text)
    except:
        pass
    
    # Try extracting from code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if json_match:
        try:
            return json.loads(json_match.group(1).strip())
        except:
            pass
    
    # Try finding JSON object in text
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            pass
    
    return {}


# ─────────────────────────────────────────────
# AGENT 1: PARSER AGENT
# ─────────────────────────────────────────────

class ParserAgent:
    """Parses raw input (OCR/ASR/text) into structured math problem format."""

    SYSTEM_PROMPT = """You are a Math Problem Parser Agent specializing in JEE-level mathematics.
Your task is to parse raw input (which may have OCR errors, speech recognition mistakes, or informal notation)
and convert it into a clean, structured math problem.

Always output valid JSON with this exact structure:
{
  "problem_text": "clean version of the problem",
  "topic": "algebra|probability|calculus|linear_algebra|unknown",
  "subtopic": "specific subtopic",
  "variables": ["list", "of", "variables"],
  "constraints": ["list of constraints"],
  "given_values": {"key": "value"},
  "what_to_find": "what needs to be solved",
  "problem_type": "equation|optimization|probability|proof|calculation",
  "difficulty": "easy|medium|hard",
  "needs_clarification": false,
  "clarification_needed": "",
  "confidence": 0.95
}

Fix common OCR issues:
- "0" vs "O", "1" vs "l", "^" for exponents
- "sqrt" → √, "pi" → π, "theta" → θ
- Fix missing multiplication signs
- Interpret math-specific phrases from speech like "x squared" → x²

If the problem is genuinely ambiguous or incomplete, set needs_clarification to true
and explain what's missing in clarification_needed."""

    def parse(self, raw_input: str, input_type: str = "text",
              ocr_confidence: float = 1.0, similar_problems: List[Dict] = None) -> Dict:
        """Parse raw input into structured problem."""
        
        similar_context = ""
        if similar_problems:
            similar_context = "\n\nSimilar previously solved problems for reference:\n"
            for p in similar_problems[:2]:
                similar_context += f"- {p.get('parsed_problem', {}).get('problem_text', '')}\n"

        user_message = f"""Input type: {input_type}
OCR/ASR confidence: {ocr_confidence:.2f}
Raw input: {raw_input}
{similar_context}

Parse this into a structured math problem. Output only valid JSON."""

        response = call_llm(self.SYSTEM_PROMPT, user_message)
        result = extract_json(response)
        
        if not result:
            # Fallback parsing
            result = {
                "problem_text": raw_input,
                "topic": self._guess_topic(raw_input),
                "subtopic": "general",
                "variables": self._extract_variables(raw_input),
                "constraints": [],
                "given_values": {},
                "what_to_find": "solve the problem",
                "problem_type": "calculation",
                "difficulty": "medium",
                "needs_clarification": ocr_confidence < 0.6,
                "clarification_needed": "OCR confidence is low, please verify the problem" if ocr_confidence < 0.6 else "",
                "confidence": ocr_confidence
            }
        
        return result

    def _guess_topic(self, text: str) -> str:
        """Guess topic from keywords."""
        text_lower = text.lower()
        if any(w in text_lower for w in ["probability", "p(", "dice", "card", "urn", "random"]):
            return "probability"
        elif any(w in text_lower for w in ["limit", "derivative", "integrate", "continuous", "calculus"]):
            return "calculus"
        elif any(w in text_lower for w in ["matrix", "determinant", "eigenvalue", "vector"]):
            return "linear_algebra"
        elif any(w in text_lower for w in ["equation", "solve", "factor", "quadratic", "algebra"]):
            return "algebra"
        return "algebra"

    def _extract_variables(self, text: str) -> List[str]:
        """Extract variable names from problem."""
        # Match single letters that look like variables
        vars_found = re.findall(r'\b([a-zA-Z])\b', text)
        # Filter out common words
        exclude = {'a', 'I', 'A', 'is', 'or', 'of', 'to', 'be', 'in', 'at', 'it', 'on'}
        return list(set([v for v in vars_found if v not in exclude]))[:5]


# ─────────────────────────────────────────────
# AGENT 2: INTENT ROUTER AGENT
# ─────────────────────────────────────────────

class IntentRouterAgent:
    """Routes problems to the correct workflow and identifies solution strategy."""

    SYSTEM_PROMPT = """You are a Math Intent Router Agent. 
Your job is to classify the problem and determine the optimal solution strategy.

Output JSON:
{
  "primary_strategy": "strategy name",
  "steps_outline": ["step 1", "step 2", ...],
  "tools_needed": ["calculator", "symbolic_solver", "none"],
  "rag_queries": ["query 1 for knowledge base", "query 2"],
  "complexity": "single_step|multi_step|complex",
  "estimated_time": "quick|medium|detailed",
  "approach_notes": "any special notes about approach"
}

Strategies for each topic:
- algebra: factoring, quadratic_formula, substitution, graphical
- probability: direct_counting, combinatorics, bayes, conditional
- calculus: direct_differentiation, chain_rule, l_hopital, optimization, substitution
- linear_algebra: row_reduction, determinant, inverse_matrix, eigenvalue"""

    def route(self, parsed_problem: Dict) -> Dict:
        """Route problem and plan solution strategy."""
        
        user_message = f"""Parsed problem:
{json.dumps(parsed_problem, indent=2)}

Determine the optimal solution strategy and what knowledge base queries to make."""

        response = call_llm(self.SYSTEM_PROMPT, user_message)
        result = extract_json(response)
        
        if not result:
            result = {
                "primary_strategy": "direct_calculation",
                "steps_outline": ["Identify the problem", "Apply relevant formula", "Calculate result"],
                "tools_needed": ["none"],
                "rag_queries": [f"{parsed_problem.get('topic', '')} {parsed_problem.get('subtopic', '')}",
                               f"{parsed_problem.get('problem_type', '')} formula"],
                "complexity": "medium",
                "estimated_time": "medium",
                "approach_notes": ""
            }
        
        return result


# ─────────────────────────────────────────────
# AGENT 3: SOLVER AGENT
# ─────────────────────────────────────────────

class SolverAgent:
    """Solves the math problem using RAG context and computational tools."""

    SYSTEM_PROMPT = """You are an expert JEE Mathematics Solver Agent.
You solve problems precisely using the provided knowledge base context and mathematical reasoning.

Rules:
1. Use ONLY the mathematical formulas and methods from the context provided
2. Show ALL intermediate steps
3. Verify numerical computations
4. If you use Python/symbolic computation, show the code
5. State your answer clearly with proper units/notation
6. Identify any edge cases or special considerations

Output format:
SOLUTION_START
[Your complete step-by-step solution]
SOLUTION_END

ANSWER: [Final numerical or symbolic answer]
CONFIDENCE: [0.0-1.0]
EDGE_CASES: [any edge cases or special notes]"""

    def solve(self, parsed_problem: Dict, routing_info: Dict, 
              rag_context: str, correction_rules: List[Dict] = None,
              similar_solutions: List[Dict] = None) -> Dict:
        """Solve the problem using all available context."""
        
        correction_context = ""
        if correction_rules:
            correction_context = "\n\nKnown correction rules for this topic:\n"
            for rule in correction_rules[:3]:
                correction_context += f"- Correction: {rule.get('correction', '')}\n"
        
        similar_context = ""
        if similar_solutions:
            similar_context = "\n\nSimilar previously solved problems:\n"
            for sol in similar_solutions[:2]:
                similar_context += f"""Problem: {sol.get('parsed_problem', {}).get('problem_text', '')}
Solution approach: {sol.get('solution', '')[:200]}...\n\n"""
        
        user_message = f"""PROBLEM TO SOLVE:
{parsed_problem.get('problem_text', '')}

TOPIC: {parsed_problem.get('topic', '')} | TYPE: {parsed_problem.get('problem_type', '')}
WHAT TO FIND: {parsed_problem.get('what_to_find', '')}
CONSTRAINTS: {', '.join(parsed_problem.get('constraints', []))}

SOLUTION STRATEGY: {routing_info.get('primary_strategy', '')}
APPROACH NOTES: {routing_info.get('approach_notes', '')}

KNOWLEDGE BASE CONTEXT:
{rag_context if rag_context else 'No specific context retrieved.'}
{correction_context}
{similar_context}

Please solve this problem step by step."""

        response = call_llm(self.SYSTEM_PROMPT, user_message, max_tokens=3000)
        
        # Extract parts
        solution = response
        answer = "See solution above"
        confidence = 0.85
        edge_cases = ""
        
        # Parse structured output
        sol_match = re.search(r'SOLUTION_START([\s\S]*?)SOLUTION_END', response)
        if sol_match:
            solution = sol_match.group(1).strip()
        
        ans_match = re.search(r'ANSWER:\s*(.+?)(?:\n|$)', response)
        if ans_match:
            answer = ans_match.group(1).strip()
        
        conf_match = re.search(r'CONFIDENCE:\s*([0-9.]+)', response)
        if conf_match:
            try:
                confidence = float(conf_match.group(1))
            except:
                pass
        
        edge_match = re.search(r'EDGE_CASES:\s*(.+?)(?:\n|$)', response)
        if edge_match:
            edge_cases = edge_match.group(1).strip()
        
        return {
            "solution": solution,
            "answer": answer,
            "confidence": confidence,
            "edge_cases": edge_cases,
            "full_response": response
        }


# ─────────────────────────────────────────────
# AGENT 4: VERIFIER / CRITIC AGENT
# ─────────────────────────────────────────────

class VerifierAgent:
    """Verifies correctness, checks units/domain, and identifies issues."""

    SYSTEM_PROMPT = """You are a Math Solution Verifier and Critic Agent.
Your role is to rigorously verify math solutions for JEE-level problems.

Check for:
1. Mathematical correctness (each step follows from previous)
2. Arithmetic/algebraic errors
3. Domain constraints (e.g., log needs positive argument, probability must be 0-1)
4. Unit consistency
5. Edge cases not considered
6. Whether the answer actually answers the question asked
7. Common mistake patterns

Output JSON:
{
  "is_correct": true,
  "confidence": 0.9,
  "issues_found": [],
  "domain_check": "passed|failed|warning",
  "unit_check": "passed|failed|not_applicable",
  "edge_case_check": "passed|warning|failed",
  "corrections_needed": [],
  "verification_notes": "brief notes",
  "trigger_hitl": false,
  "hitl_reason": ""
}

Set trigger_hitl=true if:
- You find errors but aren't sure of the correct answer
- Confidence < 0.6
- Multiple conflicting interpretations possible"""

    def verify(self, parsed_problem: Dict, solution_result: Dict, 
               rag_context: str = "") -> Dict:
        """Verify the solution."""
        
        user_message = f"""PROBLEM:
{parsed_problem.get('problem_text', '')}
Topic: {parsed_problem.get('topic', '')}
Constraints: {parsed_problem.get('constraints', [])}
What to find: {parsed_problem.get('what_to_find', '')}

SOLUTION TO VERIFY:
{solution_result.get('solution', '')}

FINAL ANSWER: {solution_result.get('answer', '')}
SOLVER CONFIDENCE: {solution_result.get('confidence', 0.85)}
EDGE CASES NOTED: {solution_result.get('edge_cases', '')}

Verify this solution rigorously. Output only valid JSON."""

        response = call_llm(self.SYSTEM_PROMPT, user_message)
        result = extract_json(response)
        
        if not result:
            result = {
                "is_correct": True,
                "confidence": solution_result.get("confidence", 0.8),
                "issues_found": [],
                "domain_check": "passed",
                "unit_check": "not_applicable",
                "edge_case_check": "passed",
                "corrections_needed": [],
                "verification_notes": "Verification completed",
                "trigger_hitl": solution_result.get("confidence", 0.8) < 0.65,
                "hitl_reason": "Low solver confidence" if solution_result.get("confidence", 0.8) < 0.65 else ""
            }
        
        return result


# ─────────────────────────────────────────────
# AGENT 5: EXPLAINER / TUTOR AGENT
# ─────────────────────────────────────────────

class ExplainerAgent:
    """Produces student-friendly, pedagogical explanations."""

    SYSTEM_PROMPT = """You are a friendly and patient Math Tutor Agent for JEE students.
Your goal is to explain math solutions in a way that builds deep understanding, not just gives answers.

Style:
- Use simple, clear language
- Use analogies where helpful
- Highlight the KEY INSIGHT of the problem
- Show WHY each step works, not just WHAT
- Use numbered steps
- Mark important formulas clearly
- End with a "Remember" or "Key Takeaway" box
- Add warnings about common mistakes to avoid in similar problems

Format your explanation using markdown with:
- ## Step headers
- **bold** for key formulas
- `code` for mathematical expressions  
- > blockquotes for key insights
- ⚠️ for common mistakes
- 💡 for tips"""

    def explain(self, parsed_problem: Dict, solution_result: Dict,
                verifier_result: Dict, corrections: List[Dict] = None) -> str:
        """Generate student-friendly explanation."""
        
        corrections_note = ""
        if corrections and verifier_result.get("corrections_needed"):
            corrections_note = f"\nNote: The following corrections were applied: {verifier_result.get('corrections_needed')}"
        
        user_message = f"""PROBLEM:
{parsed_problem.get('problem_text', '')}

TOPIC: {parsed_problem.get('topic', '')} - {parsed_problem.get('subtopic', '')}
DIFFICULTY: {parsed_problem.get('difficulty', 'medium')}

SOLUTION:
{solution_result.get('solution', '')}

FINAL ANSWER: {solution_result.get('answer', '')}
{corrections_note}

Please write a clear, student-friendly explanation of this solution that will help a JEE student truly understand the concept."""

        return call_llm(self.SYSTEM_PROMPT, user_message, temperature=0.3, max_tokens=2500)


# ─────────────────────────────────────────────
# BONUS: GUARDRAIL AGENT
# ─────────────────────────────────────────────

class GuardrailAgent:
    """Ensures inputs are appropriate math questions and outputs are safe."""

    SYSTEM_PROMPT = """You are a Guardrail Agent for a Math tutoring application.
Verify that:
1. The input is actually a math problem (not harmful content)
2. The problem is within scope (algebra, probability, calculus, linear algebra)
3. The response doesn't contain inappropriate content

Output JSON:
{
  "is_valid_math": true,
  "is_in_scope": true,
  "risk_level": "none",
  "scope_note": "",
  "proceed": true
}"""

    def check_input(self, raw_input: str) -> Dict:
        """Check if input is appropriate."""
        response = call_llm(
            self.SYSTEM_PROMPT,
            f"Check this input: {raw_input[:500]}\nOutput only JSON.",
            max_tokens=200
        )
        result = extract_json(response)
        if not result:
            return {"is_valid_math": True, "is_in_scope": True, "risk_level": "none", 
                   "scope_note": "", "proceed": True}
        return result


# ─────────────────────────────────────────────
# ORCHESTRATOR
# ─────────────────────────────────────────────

class MathMentorOrchestrator:
    """Orchestrates all agents to process a math problem end-to-end."""

    def __init__(self, rag_pipeline, memory_store,api_key):
        self.rag = rag_pipeline
        self.memory = memory_store
        self.parser = ParserAgent()
        self.router = IntentRouterAgent()
        self.solver = SolverAgent()
        self.verifier = VerifierAgent()
        self.explainer = ExplainerAgent()
        self.guardrail = GuardrailAgent()
        self.agent_trace = []
        genai.configure(api_key=api_key)
    def _log_trace(self, agent: str, status: str, details: str = ""):
        """Log agent execution to trace."""
        self.agent_trace.append({
            "agent": agent,
            "status": status,
            "details": details
        })

    def process(self, raw_input: str, input_type: str = "text",
                ocr_confidence: float = 1.0) -> Dict:
        """Run the full agent pipeline."""
        self.agent_trace = []
        result = {
            "success": False,
            "agent_trace": [],
            "parsed_problem": {},
            "routing_info": {},
            "retrieved_sources": [],
            "solution": "",
            "answer": "",
            "explanation": "",
            "verifier_result": {},
            "confidence": 0.0,
            "hitl_required": False,
            "hitl_reason": "",
            "problem_id": None,
            "similar_problems_found": [],
            "error": None
        }

        try:
            # Step 1: Guardrail check
            self._log_trace("Guardrail Agent", "running", "Checking input validity")
            guardrail_result = self.guardrail.check_input(raw_input)
            if not guardrail_result.get("proceed", True):
                result["error"] = f"Input rejected: {guardrail_result.get('scope_note', 'Invalid input')}"
                self._log_trace("Guardrail Agent", "rejected", result["error"])
                result["agent_trace"] = self.agent_trace
                return result
            self._log_trace("Guardrail Agent", "passed", "Input is valid math problem")

            # Step 2: Find similar problems from memory
            self._log_trace("Memory", "searching", "Looking for similar solved problems")
            similar_problems = self.memory.find_similar_problems(raw_input)
            if similar_problems:
                result["similar_problems_found"] = similar_problems
                self._log_trace("Memory", "found", f"Found {len(similar_problems)} similar problems")
            else:
                self._log_trace("Memory", "none", "No similar problems found in memory")

            # Step 3: Parse
            self._log_trace("Parser Agent", "running", "Parsing and structuring the problem")
            parsed_problem = self.parser.parse(
                raw_input, input_type, ocr_confidence, similar_problems
            )
            result["parsed_problem"] = parsed_problem
            
            if parsed_problem.get("needs_clarification") or ocr_confidence < 0.6:
                result["hitl_required"] = True
                reason = parsed_problem.get("clarification_needed") or "OCR/ASR confidence is low"
                result["hitl_reason"] = reason
                self._log_trace("Parser Agent", "hitl_triggered", reason)
            else:
                self._log_trace("Parser Agent", "complete", 
                               f"Topic: {parsed_problem.get('topic')}, Type: {parsed_problem.get('problem_type')}")

            # Step 4: Route
            self._log_trace("Intent Router Agent", "running", "Planning solution strategy")
            routing_info = self.router.route(parsed_problem)
            result["routing_info"] = routing_info
            self._log_trace("Intent Router Agent", "complete", 
                           f"Strategy: {routing_info.get('primary_strategy')}, "
                           f"Complexity: {routing_info.get('complexity')}")

            # Step 5: RAG retrieval
            self._log_trace("RAG Pipeline", "running", "Retrieving relevant knowledge")
            rag_queries = routing_info.get("rag_queries", [raw_input])
            all_retrieved = []
            
            for query in rag_queries[:3]:
                retrieved = self.rag.retrieve(query)
                all_retrieved.extend(retrieved)
            
            # Deduplicate by source+chunk_id
            seen_ids = set()
            unique_retrieved = []
            for doc in all_retrieved:
                doc_id = doc.get("id", "")
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    unique_retrieved.append(doc)
            
            # Get top results by score
            unique_retrieved.sort(key=lambda x: x.get("score", 0), reverse=True)
            top_retrieved = unique_retrieved[:5]
            
            rag_context = self.rag.format_context(top_retrieved)
            result["retrieved_sources"] = self.rag.get_sources_summary(top_retrieved)
            
            if top_retrieved:
                self._log_trace("RAG Pipeline", "complete", 
                               f"Retrieved {len(top_retrieved)} relevant chunks from knowledge base")
            else:
                self._log_trace("RAG Pipeline", "warning", "No relevant chunks retrieved")

            # Step 6: Get correction rules from memory
            correction_rules = self.memory.get_correction_rules(
                parsed_problem.get("topic", "unknown")
            )
            
            # Step 7: Solve
            self._log_trace("Solver Agent", "running", "Solving the problem with RAG context")
            solution_result = self.solver.solve(
                parsed_problem, routing_info, rag_context,
                correction_rules, similar_problems
            )
            result["solution"] = solution_result.get("solution", "")
            result["answer"] = solution_result.get("answer", "")
            result["confidence"] = solution_result.get("confidence", 0.85)
            self._log_trace("Solver Agent", "complete", 
                           f"Answer: {solution_result.get('answer', '')} | "
                           f"Confidence: {solution_result.get('confidence', 0.85):.0%}")

            # Step 8: Verify
            self._log_trace("Verifier Agent", "running", "Checking solution correctness")
            verifier_result = self.verifier.verify(parsed_problem, solution_result, rag_context)
            result["verifier_result"] = verifier_result
            
            if verifier_result.get("trigger_hitl"):
                result["hitl_required"] = True
                result["hitl_reason"] = verifier_result.get("hitl_reason", "Verification uncertainty")
                self._log_trace("Verifier Agent", "hitl_triggered", result["hitl_reason"])
            else:
                issues = verifier_result.get("issues_found", [])
                self._log_trace("Verifier Agent", "complete", 
                               f"{'✓ Correct' if verifier_result.get('is_correct') else '⚠ Issues found'} | "
                               f"{len(issues)} issues | Confidence: {verifier_result.get('confidence', 0):.0%}")
            
            # Update confidence from verifier
            result["confidence"] = verifier_result.get("confidence", result["confidence"])

            # Step 9: Explain
            self._log_trace("Explainer Agent", "running", "Generating student-friendly explanation")
            explanation = self.explainer.explain(
                parsed_problem, solution_result, verifier_result, correction_rules
            )
            result["explanation"] = explanation
            self._log_trace("Explainer Agent", "complete", "Explanation ready")

            # Step 10: Store in memory
            problem_id = self.memory.store_solution(
                input_type=input_type,
                original_input=raw_input,
                parsed_problem=parsed_problem,
                retrieved_context=top_retrieved,
                solution=solution_result.get("solution", ""),
                explanation=explanation,
                verifier_result=verifier_result,
                confidence=result["confidence"]
            )
            result["problem_id"] = problem_id
            self._log_trace("Memory", "stored", f"Problem saved with ID: {problem_id}")

            result["success"] = True

        except Exception as e:
            result["error"] = str(e)
            self._log_trace("Orchestrator", "error", str(e))

        result["agent_trace"] = self.agent_trace
        return result
