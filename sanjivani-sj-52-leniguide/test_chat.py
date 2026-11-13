import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from app.records import load_records
from app.smart_search import SmartSearch
from app.llm import generate_chat_response, LLMClient

print("--- 1. Testing Records Loading ---")
records = load_records()
print(f"Loaded {len(records)} records")

print("--- 2. Testing SmartSearch ---")
searcher = SmartSearch(records)
results = searcher.search("Kailasa temple Cave 16", top_k=2)
print(f"Search results count: {len(results)}, top score: {results[0].get('score')}")

print("--- 3. Testing LLM Client on Q1 ---")
q1_res = generate_chat_response("Which day is Ellora closed? And Ajanta?")
print("Q1 keys:", list(q1_res.keys()))
print("Q1 answer:", q1_res["answer"][:120], "...")
print("Q1 confidence:", q1_res["confidence"])

print("--- 4. Testing LLM Client on Q4 (Tour planner / Ticket math) ---")
q4_res = generate_chat_response(
    "We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost?",
    task="tour_planner"
)
print("Q4 answer:", q4_res["answer"][:120], "...")
print("Q4 confidence:", q4_res["confidence"])

print("--- 5. Testing Guardrail on Q6 (Diwali footfall) ---")
q6_res = generate_chat_response("How many tourists visited Ajanta caves last Diwali?")
print("Q6 answer:", q6_res["answer"])
print("Q6 confidence:", q6_res["confidence"])
assert "I don't know" in q6_res["answer"], "Guardrail failed: Q6 did not return 'I don't know'"
assert q6_res["confidence"] == "low", "Guardrail failed: Q6 confidence was not 'low'"

print("\n✓ ALL CORE LLM & DOMAIN CHECKS PASSED SUCCESSFULLY!")
