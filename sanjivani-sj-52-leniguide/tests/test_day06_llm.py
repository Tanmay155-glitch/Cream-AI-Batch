"""
Unit and integration tests for Day 6 LLM and prompt engineering.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016)
Project: SJ-52 | Product: LeniGuide
"""

import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.records import load_records
from app.smart_search import SmartSearch
from app.llm import generate_chat_response, LLMClient, load_prompt


def test_prompts_exist():
    """Verify that all required prompt templates are present and non-empty."""
    system_prompt = load_prompt("system_prompt.txt")
    cave_qa_prompt = load_prompt("task_cave_qa.txt")
    tour_planner_prompt = load_prompt("task_tour_planner.txt")

    assert len(system_prompt) > 100
    assert "Ajanta" in system_prompt and "Ellora" in system_prompt
    assert "monday" in system_prompt.lower() and "tuesday" in system_prompt.lower()
    assert "40" in system_prompt and "35" in system_prompt
    assert "under 15" in system_prompt.lower()
    assert "i don't know" in system_prompt.lower()

    assert "{context}" in cave_qa_prompt and "{question}" in cave_qa_prompt
    assert "{context}" in tour_planner_prompt and "{question}" in tour_planner_prompt


def test_llm_q1_weekly_closures():
    """Test Q1: Official ASI weekly closing rules."""
    res = generate_chat_response("Which day is Ellora closed? And Ajanta?")
    assert "answer" in res and "confidence" in res and "follow_up" in res
    assert "tuesday" in res["answer"].lower()
    assert "monday" in res["answer"].lower()
    assert res["confidence"] == "high"


def test_llm_q4_tour_planner_and_ticket_math():
    """Test Q4: School tour planning and ticket math (students under 15 are free)."""
    question = (
        "We are 4 teachers and 40 students under 15 coming on 14-15 December. "
        "Which site on which day, and total ticket cost?"
    )
    res = generate_chat_response(question, task="tour_planner")
    assert "answer" in res and "confidence" in res and "follow_up" in res
    assert "FREE" in res["answer"] or "Rs. 0" in res["answer"] or "free" in res["answer"].lower()
    assert "160" in res["answer"] or "320" in res["answer"] or "280" in res["answer"]
    assert res["confidence"] == "high"


def test_llm_q6_guardrail_unanswerable():
    """Test Q6 Guardrail: Diwali footfall statistics must return 'I don't know'."""
    question = "How many tourists visited Ajanta caves last Diwali?"
    res = generate_chat_response(question)
    assert "answer" in res and "confidence" in res and "follow_up" in res
    assert "I don't know" in res["answer"]
    assert res["confidence"] == "low"


def test_llm_client_class_interface():
    """Test LLMClient OOP wrapper."""
    client = LLMClient()
    res = client.chat("What is special about the Kailasa temple in Ellora cave 16?")
    assert "Kailasa" in res["answer"] or "monolithic" in res["answer"]
    assert res["confidence"] == "high"


if __name__ == "__main__":
    print("Running Day 6 Unit Tests...")
    test_prompts_exist()
    print("✓ test_prompts_exist passed")
    test_llm_q1_weekly_closures()
    print("✓ test_llm_q1_weekly_closures passed")
    test_llm_q4_tour_planner_and_ticket_math()
    print("✓ test_llm_q4_tour_planner_and_ticket_math passed")
    test_llm_q6_guardrail_unanswerable()
    print("✓ test_llm_q6_guardrail_unanswerable passed")
    test_llm_client_class_interface()
    print("✓ test_llm_client_class_interface passed")
    print("\n✅ ALL 5 UNIT TESTS PASSED!")

