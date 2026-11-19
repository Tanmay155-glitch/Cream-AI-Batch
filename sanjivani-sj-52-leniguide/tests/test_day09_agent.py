"""
Unit and Integration Tests for Day 9: Tools, Agent Loop, LangGraph Agent & POST /agent.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide (Ajanta & Ellora UNESCO Heritage Guide)
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent_loop import LeniGuideAgent, run_agent_loop
from app.graph import run_graph_agent
from app.main import AgentRequest, AskRequest, agent_endpoint, app, ask_endpoint
from app.tools import cave_trip_planner, extract_trip_params, rag_search_tool

# ============================================================================
# Session 1: Tools Tests
# ============================================================================

def test_cave_trip_planner_q4_math():
    """Verify Q4: 14-15 Dec 2026, 4 teachers, 40 students under 15."""
    plan = cave_trip_planner(
        start_date="2026-12-14",
        num_days=2,
        adults=4,
        children_under_15=40,
        payment_mode="both"
    )

    # 14 Dec 2026 is Monday -> Ajanta closed -> Ellora Day 1
    assert plan["schedule"][0]["assigned_site"] == "Ellora"
    assert plan["schedule"][0]["weekday"] == "Monday"
    assert plan["schedule"][0]["date"] == "2026-12-14"

    # 15 Dec 2026 is Tuesday -> Ellora closed -> Ajanta Day 2
    assert plan["schedule"][1]["assigned_site"] == "Ajanta"
    assert plan["schedule"][1]["weekday"] == "Tuesday"
    assert plan["schedule"][1]["date"] == "2026-12-15"

    fb = plan["fee_breakdown"]
    # 4 adults * Rs 40 = Rs 160 per site -> 2 sites = Rs 320 cash
    assert fb["cash_per_site_inr"] == 160
    assert fb["cash_total_inr"] == 320

    # 4 adults * Rs 35 = Rs 140 per site -> 2 sites = Rs 280 online
    assert fb["online_per_site_inr"] == 140
    assert fb["online_total_inr"] == 280

    # Children under 15 are free
    assert fb["children_cost_inr"] == 0
    assert fb["savings_online_inr"] == 40


def test_cave_trip_planner_tuesday_start():
    """Verify start on Tuesday (15 Dec 2026): Ellora closed -> Ajanta Day 1, Ellora Day 2."""
    plan = cave_trip_planner(
        start_date="2026-12-15",
        num_days=2,
        adults=2,
        children_under_15=10
    )
    assert plan["schedule"][0]["assigned_site"] == "Ajanta"
    assert plan["schedule"][0]["weekday"] == "Tuesday"
    assert plan["schedule"][1]["assigned_site"] == "Ellora"
    assert plan["schedule"][1]["weekday"] == "Wednesday"


def test_extract_trip_params():
    """Verify natural language parameter extraction."""
    q = "We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost?"
    params = extract_trip_params(q)
    assert params["adults"] == 4
    assert params["children_under_15"] == 40
    assert params["num_days"] == 2


# ============================================================================
# Session 1: ReAct Agent Loop Tests
# ============================================================================

def test_agent_loop_q4():
    """Verify hand-written agent loop correctly routes and solves Q4."""
    q4 = "We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost?"
    res = run_agent_loop(q4)

    assert "cave_trip_planner" in res["tools_used"]
    assert len(res["steps"]) >= 1
    assert "Ellora" in res["answer"]
    assert "Ajanta" in res["answer"]
    assert "280" in res["answer"]
    assert "320" in res["answer"]


def test_agent_loop_q6_guardrail():
    """Verify hand-written agent loop respects out-of-scope guardrail for Q6."""
    q6 = "How many tourists visited Ajanta caves last Diwali?"
    res = run_agent_loop(q6)

    assert res["abstained"] is True
    assert "don't know" in res["answer"].lower() or "not available" in res["answer"].lower()


# ============================================================================
# Session 2: LangGraph Stateful Agent Tests
# ============================================================================

def test_langgraph_q4_direct():
    """Verify LangGraph agent handles Q4 in single-shot mode."""
    q4 = "We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost?"
    res = run_graph_agent(question=q4, thread_id="test-q4-graph")

    assert "cave_trip_planner" in res["tools_used"]
    assert res["approval_status"] == "approved"
    assert "Ellora" in res["answer"] and "Ajanta" in res["answer"]
    assert "280" in res["answer"] and "320" in res["answer"]


def test_langgraph_human_approval_step():
    """Verify the one approval step in LangGraph (Turn 1: pending_approval -> Turn 2: approved)."""
    thread = "test-approval-step-88"
    q4 = "We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost?"

    # Turn 1: require approval
    t1 = run_graph_agent(question=q4, thread_id=thread, require_approval=True)
    assert t1["approval_status"] == "pending_approval"
    assert "[PREVIEW]" in t1["answer"]

    # Turn 2: human sends approval
    t2 = run_graph_agent(question="Please confirm this plan.", thread_id=thread, approved=True)
    assert t2["approval_status"] == "approved"
    assert "[CONFIRMED]" in t2["answer"]


# ============================================================================
# FastAPI POST /agent & RAG Endpoint Tests
# ============================================================================

def test_fastapi_post_agent_q4():
    """Verify POST /agent endpoint handler with Q4 request."""
    req = AgentRequest(
        question="We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost?",
        thread_id="api-test-q4"
    )
    res = agent_endpoint(req)

    assert "cave_trip_planner" in res.tools_used
    assert res.approval_status == "approved"
    assert "Ellora" in res.answer and "Ajanta" in res.answer
    assert "280" in res.answer and "320" in res.answer
    assert res.thread_id == "api-test-q4"


def test_fastapi_post_agent_approval_flow():
    """Verify POST /agent multi-turn human approval flow."""
    thread = "api-approval-thread-99"

    # Turn 1: pending approval
    req1 = AgentRequest(
        question="We are 4 teachers and 40 students under 15 coming on 14-15 December.",
        thread_id=thread,
        require_approval=True
    )
    res1 = agent_endpoint(req1)
    assert res1.approval_status == "pending_approval"

    # Turn 2: approved confirmation
    req2 = AgentRequest(
        question="I confirm the itinerary.",
        thread_id=thread,
        approved=True
    )
    res2 = agent_endpoint(req2)
    assert res2.approval_status == "approved"
    assert "[CONFIRMED]" in res2.answer


def test_fastapi_post_agent_guardrail():
    """Verify POST /agent abstains on Q6 out-of-scope query."""
    req = AgentRequest(
        question="How many tourists visited Ajanta caves last Diwali?"
    )
    res = agent_endpoint(req)
    assert res.abstained is True
    assert "don't know" in res.answer.lower()


def test_previous_endpoints_still_intact():
    """Ensure Day 8 RAG ask endpoint continues functioning."""
    ask_req = AskRequest(question="What is special about the Kailasa temple in Ellora cave 16?")
    ask_res = ask_endpoint(ask_req)
    assert ask_res.answer != ""
    assert len(ask_res.citations) > 0


if __name__ == "__main__":
    print("=" * 80)
    print("RUNNING DAY 9 COMPREHENSIVE TEST SUITE")
    print("Student: Tanmay Subhash Gawali (SJ-52)")
    print("=" * 80)

    test_cave_trip_planner_q4_math()
    print("✓ test_cave_trip_planner_q4_math passed")

    test_cave_trip_planner_tuesday_start()
    print("✓ test_cave_trip_planner_tuesday_start passed")

    test_extract_trip_params()
    print("✓ test_extract_trip_params passed")

    test_agent_loop_q4()
    print("✓ test_agent_loop_q4 passed")

    test_agent_loop_q6_guardrail()
    print("✓ test_agent_loop_q6_guardrail passed")

    test_langgraph_q4_direct()
    print("✓ test_langgraph_q4_direct passed")

    test_langgraph_human_approval_step()
    print("✓ test_langgraph_human_approval_step passed")

    test_fastapi_post_agent_q4()
    print("✓ test_fastapi_post_agent_q4 passed")

    test_fastapi_post_agent_approval_flow()
    print("✓ test_fastapi_post_agent_approval_flow passed")

    test_fastapi_post_agent_guardrail()
    print("✓ test_fastapi_post_agent_guardrail passed")

    test_previous_endpoints_still_intact()
    print("✓ test_previous_endpoints_still_intact passed")

    print("\n" + "=" * 80)
    print("✅ ALL 11 TEST CASES PASSED PERFECTLY!")
    print("=" * 80)
