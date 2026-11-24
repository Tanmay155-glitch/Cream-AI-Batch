"""
test_planner.py — Tests for cave_trip_planner tool.
Covers: Mon start, Tue start, 1-day trip, fee totals with fixture fees,
online vs cash, bad date, null-fee handling.
"""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

# Use fixture fees for deterministic tests
FIXTURE_RULES = {
    "ajanta": {
        "closed_day": "Monday",
        "timings": "9:00 AM to 5:00 PM",
        "fee_indian_cash": 40,
        "fee_indian_online": 35,
        "child_free_under_age": 15,
        "source_url": "https://asi.nic.in/pages/WorldHeritageAjantaCaves",
        "verified_on": "2026-11-01",
        "authority": "official",
    },
    "ellora": {
        "closed_day": "Tuesday",
        "timings": "Sunrise to Sunset",
        "fee_indian_cash": 40,
        "fee_indian_online": 35,
        "child_free_under_age": 15,
        "source_url": "https://asi.nic.in/pages/WorldHeritageElloraCaves",
        "verified_on": "2026-11-01",
        "authority": "official",
    },
}

NULL_FEE_RULES = {
    "ajanta": {**FIXTURE_RULES["ajanta"], "fee_indian_cash": None, "fee_indian_online": None, "verified_on": None},
    "ellora": {**FIXTURE_RULES["ellora"], "fee_indian_cash": None, "fee_indian_online": None, "verified_on": None},
}


@pytest.fixture(autouse=True)
def mock_site_rules():
    """Patch load_site_rules to use fixture fees."""
    with patch("app.tools.load_site_rules", return_value=FIXTURE_RULES):
        yield


def test_monday_start_ellora_first():
    """14 Dec 2026 (Monday) → Day 1 = Ellora (Ajanta closed), Day 2 = Ajanta."""
    from app.tools import cave_trip_planner
    plan = cave_trip_planner(start_date="2026-12-14", num_days=2, adults=4, children_under_15=40)
    assert plan["schedule"][0]["assigned_site"] == "Ellora"
    assert plan["schedule"][1]["assigned_site"] == "Ajanta"


def test_tuesday_start_ajanta_first():
    """15 Dec 2026 (Tuesday) → Day 1 = Ajanta (Ellora closed), Day 2 = Ellora."""
    from app.tools import cave_trip_planner
    plan = cave_trip_planner(start_date="2026-12-15", num_days=2, adults=4, children_under_15=40)
    assert plan["schedule"][0]["assigned_site"] == "Ajanta"
    assert plan["schedule"][1]["assigned_site"] == "Ellora"


def test_one_day_trip():
    """1-day trip returns one site plus reason for the other."""
    from app.tools import cave_trip_planner
    plan = cave_trip_planner(start_date="2026-12-14", num_days=1, adults=2)
    assert len(plan["schedule"]) == 1
    assert plan["unique_sites_count"] == 1


def test_fee_total_q4():
    """Q4: 4 adults + 40 children under 15 = 4 × fee × 2 sites; children free."""
    from app.tools import cave_trip_planner
    plan = cave_trip_planner(start_date="2026-12-14", num_days=2, adults=4, children_under_15=40)
    fb = plan["fee_breakdown"]
    assert fb["fee_status"] == "verified"
    assert fb["cash_total_inr"] == 4 * 40 * 2  # 320
    assert fb["online_total_inr"] == 4 * 35 * 2  # 280
    assert fb["children_cost_inr"] == 0


def test_online_vs_cash():
    """Online fee < cash fee."""
    from app.tools import cave_trip_planner
    plan = cave_trip_planner(start_date="2026-12-14", num_days=2, adults=4, payment_mode="both")
    fb = plan["fee_breakdown"]
    assert fb["online_total_inr"] < fb["cash_total_inr"]
    assert fb["savings_online_inr"] > 0


def test_bad_date_raises():
    """Bad date string raises ValueError."""
    from app.tools import cave_trip_planner
    with pytest.raises(ValueError):
        cave_trip_planner(start_date="not-a-date", num_days=2)


def test_negative_days_raises():
    """num_days < 1 raises ValueError."""
    from app.tools import cave_trip_planner
    with pytest.raises(ValueError):
        cave_trip_planner(start_date="2026-12-14", num_days=-1)


def test_null_fee_returns_not_verified():
    """When fees are null, fee_status = 'not verified' and no total."""
    from app.tools import cave_trip_planner
    with patch("app.tools.load_site_rules", return_value=NULL_FEE_RULES):
        plan = cave_trip_planner(start_date="2026-12-14", num_days=2, adults=4)
        fb = plan["fee_breakdown"]
        assert fb["fee_status"] == "not verified"
        assert "cash_total_inr" not in fb


def test_planner_payment_parameter_and_sources():
    """Verify payment='online' parameter, fee_total, and source_url/source_date provenance."""
    from app.tools import cave_trip_planner
    plan = cave_trip_planner(
        start_date="2026-12-14",
        num_days=2,
        adults=4,
        children_under_15=40,
        payment="online",
        sites=["ajanta", "ellora"],
    )
    assert plan["fee_total"] == 4 * 35 * 2  # 280
    assert "source_url" in plan
    assert "asi.nic.in" in plan["source_url"]
    assert "source_date" in plan
    assert "itinerary" in plan
    assert len(plan["itinerary"]) == 2


def test_one_day_impossible_warning():
    """Verify impossible case warning when 1-day trip is requested for both sites."""
    from app.tools import cave_trip_planner
    plan = cave_trip_planner(
        start_date="2026-12-14",
        num_days=1,
        adults=4,
        sites=["ajanta", "ellora"],
    )
    assert "impossible_warning" in plan
    assert len(plan["impossible_warning"]) > 0
    assert "100 km" in plan["impossible_warning"]

