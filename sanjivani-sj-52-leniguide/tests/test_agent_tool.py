"""
Day 11 – Tests for cave_trip_planner tool and agent loop execution.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide

3 tests: Monday/Tuesday closure assignment, ticket arithmetic, agent loop invocation.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent_loop import run_agent_loop
from app.tools import cave_trip_planner


# ============================================================================
# Test 9: Monday → Ellora (Ajanta closed), Tuesday → Ajanta (Ellora closed)
# ============================================================================
def test_cave_trip_planner_monday_tuesday_closures():
    """
    14 Dec 2026 is Monday, 15 Dec 2026 is Tuesday.
    Ajanta is closed on Mondays → Day 1 must be Ellora.
    Ellora is closed on Tuesdays → Day 2 must be Ajanta.
    """
    plan = cave_trip_planner(
        start_date="2026-12-14",
        num_days=2,
        adults=4,
        children_under_15=40,
    )

    sched = plan["schedule"]
    assert sched[0]["assigned_site"] == "Ellora", (
        f"Day 1 (Monday) should be Ellora, got {sched[0]['assigned_site']}"
    )
    assert sched[0]["weekday"] == "Monday"

    assert sched[1]["assigned_site"] == "Ajanta", (
        f"Day 2 (Tuesday) should be Ajanta, got {sched[1]['assigned_site']}"
    )
    assert sched[1]["weekday"] == "Tuesday"


# ============================================================================
# Test 10: Fee arithmetic – 4 adults × Rs 40 × 2 sites = Rs 320 (cash)
# ============================================================================
def test_cave_trip_planner_ticket_arithmetic():
    """
    4 adults + 40 children under 15, visiting 2 sites:
    - Cash total:   4 × Rs 40 × 2 = Rs 320
    - Online total: 4 × Rs 35 × 2 = Rs 280
    - Children cost: Rs 0 (FREE under ASI rules)
    """
    plan = cave_trip_planner(
        start_date="2026-12-14",
        num_days=2,
        adults=4,
        children_under_15=40,
    )

    fb = plan["fee_breakdown"]
    assert fb["cash_total_inr"] == 320, f"Cash total {fb['cash_total_inr']} != 320"
    assert fb["online_total_inr"] == 280, f"Online total {fb['online_total_inr']} != 280"
    assert fb["children_cost_inr"] == 0, f"Children cost {fb['children_cost_inr']} != 0"


# ============================================================================
# Test 11: Agent loop invokes cave_trip_planner and reports correct totals
# ============================================================================
def test_agent_loop_invokes_trip_planner():
    """
    run_agent_loop with the Q4 reference question must:
    - use 'cave_trip_planner' in tools_used
    - include '320' (cash) and '280' (online) in the answer text
    """
    question = (
        "We are 4 teachers and 40 students under 15 coming on 14-15 December. "
        "Which site on which day, and total ticket cost?"
    )
    result = run_agent_loop(question)

    assert "cave_trip_planner" in result["tools_used"], (
        f"cave_trip_planner not in tools_used: {result['tools_used']}"
    )
    assert "320" in result["answer"], f"'320' not found in answer: {result['answer'][:300]}"
    assert "280" in result["answer"], f"'280' not found in answer: {result['answer'][:300]}"
