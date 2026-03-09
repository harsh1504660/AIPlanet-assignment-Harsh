"""
Quick test script to verify Math Mentor components work correctly.
Run: python test_system.py
"""

import os
import sys
import json
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def test_rag():
    """Test the RAG pipeline."""
    print("\n📚 Testing RAG Pipeline...")
    from rag.pipeline import MathRAGPipeline
    
    rag = MathRAGPipeline(
        knowledge_base_path="./knowledge_base",
        vector_store_path="./rag/vector_store"
    )
    success = rag.build_index()
    print(f"  Index built: {success}")
    print(f"  Documents loaded: {len(rag.documents)}")
    
    # Test retrieval
    results = rag.retrieve("quadratic formula discriminant", top_k=3)
    print(f"  Retrieval test: {len(results)} results")
    if results:
        print(f"  Top result source: {results[0].get('source', 'N/A')}")
        print(f"  Top result score: {results[0].get('score', 0):.3f}")
    
    return len(rag.documents) > 0


def test_memory():
    """Test the memory store."""
    print("\n💾 Testing Memory Store...")
    from memory.store import MathMemory
    
    mem = MathMemory(db_path="./memory/test_memory.json")
    
    # Store a test solution
    problem_id = mem.store_solution(
        input_type="text",
        original_input="Find roots of x^2 - 5x + 6 = 0",
        parsed_problem={
            "problem_text": "Find roots of x² - 5x + 6 = 0",
            "topic": "algebra",
            "variables": ["x"]
        },
        retrieved_context=[{"source": "algebra", "text": "quadratic formula..."}],
        solution="Using factoring: (x-2)(x-3) = 0, so x = 2 or x = 3",
        explanation="Step 1: Factor the quadratic...",
        verifier_result={"is_correct": True, "confidence": 0.95},
        confidence=0.95
    )
    print(f"  Stored problem ID: {problem_id}")
    
    # Update feedback
    mem.update_feedback(problem_id, "correct")
    print("  Feedback updated: correct")
    
    # Find similar
    similar = mem.find_similar_problems("solve x^2 - 4x + 3 = 0")
    print(f"  Similar problems found: {len(similar)}")
    
    # Stats
    stats = mem.get_stats()
    print(f"  Stats: {stats}")
    
    # Cleanup test file
    try:
        os.remove("./memory/test_memory.json")
    except:
        pass
    
    return True


def test_agents():
    """Test individual agents."""
    print("\n🤖 Testing Agents (requires ANTHROPIC_API_KEY)...")
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("  ⚠️  ANTHROPIC_API_KEY not set. Skipping agent tests.")
        return True
    
    from agents.orchestrator import ParserAgent, GuardrailAgent
    
    # Test Guardrail
    print("  Testing Guardrail Agent...")
    guardrail = GuardrailAgent()
    result = guardrail.check_input("Solve x^2 - 5x + 6 = 0")
    print(f"  Guardrail result: proceed={result.get('proceed', True)}")
    
    # Test Parser
    print("  Testing Parser Agent...")
    parser = ParserAgent()
    parsed = parser.parse("Find the probability when two dice sum to 7")
    print(f"  Topic: {parsed.get('topic')}")
    print(f"  Variables: {parsed.get('variables')}")
    print(f"  Needs clarification: {parsed.get('needs_clarification')}")
    
    return True


def test_full_pipeline():
    """Test the full orchestrator pipeline."""
    print("\n🚀 Testing Full Pipeline (requires ANTHROPIC_API_KEY)...")
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("  ⚠️  ANTHROPIC_API_KEY not set. Skipping full pipeline test.")
        return True
    
    from rag.pipeline import MathRAGPipeline
    from memory.store import MathMemory
    from agents.orchestrator import MathMentorOrchestrator
    
    rag = MathRAGPipeline(knowledge_base_path="./knowledge_base")
    rag.build_index()
    
    mem = MathMemory(db_path="./memory/test_pipeline_memory.json")
    orch = MathMentorOrchestrator(rag, mem)
    
    test_problem = "Solve the quadratic equation: x² - 5x + 6 = 0"
    print(f"  Problem: {test_problem}")
    
    result = orch.process(test_problem, "text", 1.0)
    
    print(f"  Success: {result['success']}")
    print(f"  Answer: {result.get('answer', 'N/A')}")
    print(f"  Confidence: {result.get('confidence', 0):.2f}")
    print(f"  Topic: {result.get('parsed_problem', {}).get('topic', 'N/A')}")
    print(f"  Agent steps: {len(result.get('agent_trace', []))}")
    print(f"  Sources retrieved: {len(result.get('retrieved_sources', []))}")
    print(f"  HITL required: {result.get('hitl_required', False)}")
    
    # Cleanup
    try:
        os.remove("./memory/test_pipeline_memory.json")
    except:
        pass
    
    return result["success"]


if __name__ == "__main__":
    print("=" * 60)
    print("🧮 Math Mentor — System Tests")
    print("=" * 60)
    
    results = {}
    
    try:
        results["rag"] = test_rag()
    except Exception as e:
        print(f"  ❌ RAG test failed: {e}")
        results["rag"] = False
    
    try:
        results["memory"] = test_memory()
    except Exception as e:
        print(f"  ❌ Memory test failed: {e}")
        results["memory"] = False
    
    try:
        results["agents"] = test_agents()
    except Exception as e:
        print(f"  ❌ Agent test failed: {e}")
        results["agents"] = False
    
    try:
        results["pipeline"] = test_full_pipeline()
    except Exception as e:
        print(f"  ❌ Pipeline test failed: {e}")
        results["pipeline"] = False
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    for test, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {test.upper()}")
    
    all_passed = all(results.values())
    print("\n" + ("🎉 All tests passed!" if all_passed else "⚠️  Some tests failed"))
    print("=" * 60)
