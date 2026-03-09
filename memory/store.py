"""
Memory & Self-Learning Module for Math Mentor
Stores solved problems, user feedback, and correction patterns
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any


class MathMemory:
    """Persistent memory store for Math Mentor application."""

    def __init__(self, db_path: str = "./memory/math_memory.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.memory = self._load()

    def _load(self) -> Dict:
        """Load memory from disk."""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "solved_problems": [],
            "correction_rules": [],
            "ocr_corrections": {},
            "topic_stats": {},
            "session_count": 0
        }

    def _save(self):
        """Persist memory to disk."""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.memory, f, indent=2, default=str)
        except Exception as e:
            print(f"Memory save error: {e}")

    def _hash_problem(self, problem_text: str) -> str:
        """Create a hash for a problem for deduplication."""
        normalized = " ".join(problem_text.lower().split())
        return hashlib.md5(normalized.encode()).hexdigest()[:12]

    def store_solution(self, 
                       input_type: str,
                       original_input: str,
                       parsed_problem: Dict,
                       retrieved_context: List[Dict],
                       solution: str,
                       explanation: str,
                       verifier_result: Dict,
                       confidence: float) -> str:
        """Store a solved problem in memory."""
        problem_id = self._hash_problem(parsed_problem.get("problem_text", original_input))
        timestamp = datetime.now().isoformat()
        
        entry = {
            "id": problem_id,
            "timestamp": timestamp,
            "input_type": input_type,
            "original_input": original_input[:500],  # Truncate long inputs
            "parsed_problem": parsed_problem,
            "topic": parsed_problem.get("topic", "unknown"),
            "solution": solution,
            "explanation": explanation,
            "verifier_result": verifier_result,
            "confidence": confidence,
            "user_feedback": None,
            "user_correction": None,
            "sources_used": [r.get("source", "unknown") for r in retrieved_context]
        }
        
        # Update or append
        existing_ids = [p["id"] for p in self.memory["solved_problems"]]
        if problem_id in existing_ids:
            idx = existing_ids.index(problem_id)
            self.memory["solved_problems"][idx] = entry
        else:
            self.memory["solved_problems"].append(entry)
        
        # Update topic stats
        topic = parsed_problem.get("topic", "unknown")
        if topic not in self.memory["topic_stats"]:
            self.memory["topic_stats"][topic] = {"solved": 0, "correct": 0, "incorrect": 0}
        self.memory["topic_stats"][topic]["solved"] += 1
        
        self._save()
        return problem_id

    def update_feedback(self, problem_id: str, feedback: str, correction: Optional[str] = None):
        """Update user feedback for a solved problem."""
        for problem in self.memory["solved_problems"]:
            if problem["id"] == problem_id:
                problem["user_feedback"] = feedback
                problem["user_correction"] = correction
                
                # Update topic stats
                topic = problem.get("topic", "unknown")
                if topic in self.memory["topic_stats"]:
                    if feedback == "correct":
                        self.memory["topic_stats"][topic]["correct"] += 1
                    elif feedback == "incorrect":
                        self.memory["topic_stats"][topic]["incorrect"] += 1
                
                # If correction provided, store as correction rule
                if correction and feedback == "incorrect":
                    self._store_correction_rule(problem, correction)
                
                break
        
        self._save()

    def _store_correction_rule(self, problem: Dict, correction: str):
        """Store a correction as a learning pattern."""
        rule = {
            "topic": problem.get("topic", "unknown"),
            "problem_type": problem.get("parsed_problem", {}).get("problem_type", "unknown"),
            "original_solution": problem.get("solution", ""),
            "correction": correction,
            "timestamp": datetime.now().isoformat()
        }
        self.memory["correction_rules"].append(rule)

    def store_ocr_correction(self, original_ocr: str, corrected_text: str):
        """Store OCR correction pattern for future use."""
        self.memory["ocr_corrections"][original_ocr[:50]] = corrected_text[:50]
        self._save()

    def find_similar_problems(self, query_problem: str, topic: str = None, top_k: int = 3) -> List[Dict]:
        """Find similar solved problems from memory."""
        if not self.memory["solved_problems"]:
            return []
        
        query_words = set(query_problem.lower().split())
        scored = []
        
        for problem in self.memory["solved_problems"]:
            # Skip problems without feedback or with negative feedback
            if problem.get("user_feedback") == "incorrect":
                continue
            
            problem_text = problem.get("parsed_problem", {}).get("problem_text", "")
            if not problem_text:
                continue
            
            # Topic filter
            if topic and problem.get("topic") != topic:
                continue
            
            # Keyword similarity
            prob_words = set(problem_text.lower().split())
            if not prob_words:
                continue
            
            overlap = len(query_words & prob_words)
            score = overlap / max(len(query_words), 1)
            
            if score > 0.2:  # Minimum similarity threshold
                scored.append({
                    "problem": problem,
                    "similarity": score
                })
        
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return [item["problem"] for item in scored[:top_k]]

    def get_correction_rules(self, topic: str) -> List[Dict]:
        """Get correction rules for a specific topic."""
        return [r for r in self.memory["correction_rules"] if r.get("topic") == topic]

    def get_topic_stats(self) -> Dict:
        """Get statistics per topic."""
        return self.memory["topic_stats"]

    def get_all_problems(self) -> List[Dict]:
        """Get all stored problems."""
        return self.memory["solved_problems"]

    def get_problem_by_id(self, problem_id: str) -> Optional[Dict]:
        """Get a specific problem by ID."""
        for problem in self.memory["solved_problems"]:
            if problem["id"] == problem_id:
                return problem
        return None

    def increment_session(self):
        """Increment session counter."""
        self.memory["session_count"] = self.memory.get("session_count", 0) + 1
        self._save()

    def get_stats(self) -> Dict:
        """Get overall memory statistics."""
        problems = self.memory["solved_problems"]
        with_feedback = [p for p in problems if p.get("user_feedback")]
        correct = [p for p in with_feedback if p.get("user_feedback") == "correct"]
        
        return {
            "total_problems": len(problems),
            "with_feedback": len(with_feedback),
            "correct": len(correct),
            "accuracy": len(correct) / max(len(with_feedback), 1),
            "sessions": self.memory.get("session_count", 0),
            "correction_rules": len(self.memory.get("correction_rules", [])),
            "topics": list(self.memory.get("topic_stats", {}).keys())
        }
