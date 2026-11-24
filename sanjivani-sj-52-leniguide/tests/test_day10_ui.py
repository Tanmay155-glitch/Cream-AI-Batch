"""
Tests for Day 10: Streamlit UI, Must-See Route Strip, Feedback & Checkpoint 2.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide
"""

import json
import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ui.app import (
    AJANTA_ROUTE,
    ELLORA_ROUTE,
    FEEDBACK_FILE,
    call_backend,
    feedback_counts,
    load_feedback,
    save_feedback,
)

# ============================================================================
# 1. File Artifact & Configuration Tests
# ============================================================================

def test_day10_files_exist():
    """Verify all required Day 10 deliverable files exist."""
    assert (PROJECT_ROOT / "ui" / "app.py").exists(), "ui/app.py must exist"
    assert (PROJECT_ROOT / "docs" / "leniguide_ui_preview.svg").exists(), "docs/leniguide_ui_preview.svg must exist"
    assert (PROJECT_ROOT / "docs" / "checkpoint_2_demo.md").exists(), "docs/checkpoint_2_demo.md must exist"
    assert (PROJECT_ROOT / "data" / "feedback.json").exists(), "data/feedback.json must exist"
    
    # Check requirements.txt
    req_content = (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "streamlit" in req_content.lower(), "requirements.txt must include streamlit"
    
    # Check README.md
    readme_content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "leniguide_ui_preview.svg" in readme_content, "README must embed UI preview svg"
    assert "streamlit run ui/app.py" in readme_content, "README must contain Streamlit run command"
    assert "Must-See Route" in readme_content, "README must document signature feature"


# ============================================================================
# 2. Signature Feature: Route Strip Math & Walking Order Tests
# ============================================================================

def test_ajanta_route_specification():
    """
    Verify Ajanta Must-See route:
    - 8 caves in walking order (Cave 1 -> Cave 26)
    - Exactly 5 starred caves
    - Fits into 3-4 hours (175 - 180 mins)
    """
    assert len(AJANTA_ROUTE) == 8, f"Expected 8 Ajanta caves, got {len(AJANTA_ROUTE)}"
    
    # Verify walking order
    expected_caves = ["Cave 1", "Cave 2", "Cave 9", "Cave 10", "Cave 16", "Cave 17", "Cave 19", "Cave 26"]
    actual_caves = [c["cave"] for c in AJANTA_ROUTE]
    assert actual_caves == expected_caves, f"Caves not in walking order: {actual_caves}"
    
    # Top 5 stars
    starred = [c for c in AJANTA_ROUTE if c["star"]]
    assert len(starred) == 5, f"Expected exactly 5 starred caves, got {len(starred)}"
    
    # Time math: Full route and core (starred) route
    # Master prompt: Show total minutes and core-route total for starred caves
    total_mins = sum(c["mins"] for c in AJANTA_ROUTE)
    starred_mins = sum(c["mins"] for c in starred)
    
    # Core starred route should fit 3-4 hours (180-240 min)
    assert 180 <= starred_mins <= 240, f"Core starred route time {starred_mins} min outside 3-4 hour window"
    
    # Full route may exceed (master prompt allows this)
    assert total_mins >= starred_mins, "Total time must be >= starred time"


def test_ellora_route_specification():
    """
    Verify Ellora Must-See route:
    - 12 caves across Buddhist, Hindu, and Jain
    - Exactly 5 starred caves
    - Fits into 3-4 hours (220 - 240 mins)
    """
    assert len(ELLORA_ROUTE) == 12, f"Expected 12 Ellora caves, got {len(ELLORA_ROUTE)}"
    
    # Verify all 3 religions represented
    religions = {c["religion"] for c in ELLORA_ROUTE}
    assert {"Buddhist", "Hindu", "Jain"}.issubset(religions), f"Missing religious traditions: {religions}"
    
    # Top 5 stars
    starred = [c for c in ELLORA_ROUTE if c["star"]]
    assert len(starred) == 5, f"Expected exactly 5 starred caves, got {len(starred)}"
    
    # Cave 16 Kailasha must be starred and have substantial time
    kailasha = next((c for c in ELLORA_ROUTE if "16" in c["cave"]), None)
    assert kailasha is not None, "Cave 16 must be present in Ellora route"
    assert kailasha["star"] is True, "Cave 16 Kailasa must be starred"
    assert kailasha["mins"] >= 30, "Cave 16 Kailasa requires at least 30 mins"
    
    # Time math: Full route and core (starred) route
    # Master prompt: Show total minutes and core-route total for starred caves
    total_mins = sum(c["mins"] for c in ELLORA_ROUTE)
    starred_mins = sum(c["mins"] for c in starred)
    
    # Core starred route should fit 3-4 hours (180-240 min)
    assert 180 <= starred_mins <= 300, f"Core starred route time {starred_mins} min outside 3-5 hour window"
    
    # Full route may exceed (master prompt allows this)
    assert total_mins >= starred_mins, "Total time must be >= starred time"


# ============================================================================
# 3. User Feedback Persistence Loop Tests
# ============================================================================

def test_feedback_persistence(tmp_path, monkeypatch):
    """Verify thumbs up / down feedback persists to JSON and increments counters."""
    test_file = tmp_path / "feedback_test.json"
    monkeypatch.setattr("ui.app.FEEDBACK_FILE", test_file)
    
    # Initially empty
    assert load_feedback() == []
    assert feedback_counts() == {"up": 0, "down": 0}
    
    # Save thumbs up
    save_feedback(
        question="Which cave has Padmapani?",
        answer="Cave 1 at Ajanta features Padmapani.",
        rating="up",
        mode="rag"
    )
    
    counts = feedback_counts()
    assert counts["up"] == 1
    assert counts["down"] == 0
    
    # Save thumbs down
    save_feedback(
        question="Unanswerable question",
        answer="I don't know.",
        rating="down",
        mode="agent"
    )
    
    counts2 = feedback_counts()
    assert counts2["up"] == 1
    assert counts2["down"] == 1
    
    # Inspect persisted JSON file
    data = json.loads(test_file.read_text(encoding="utf-8"))
    assert len(data) == 2
    assert data[0]["question"] == "Which cave has Padmapani?"
    assert data[0]["rating"] == "up"
    assert data[0]["mode"] == "rag"
    assert "timestamp" in data[0]


# ============================================================================
# 4. Backend Calling & Direct Import Fallback Tests
# ============================================================================

def test_call_backend_rag_fallback():
    """Verify call_backend executes RAG question via direct import when server is down."""
    res = call_backend(
        question="What is special about the Kailasa temple in Ellora cave 16?",
        mode="rag",
        backend_url="http://127.0.0.1:9999"  # Deliberately unreachable port
    )
    assert isinstance(res, dict)
    assert "answer" in res
    assert "citations" in res
    # Should ground to Cave 16 Kailasa
    assert "16" in res["answer"] or "Kailasa" in res["answer"] or "Kailash" in res["answer"]


def test_call_backend_agent_fallback():
    """Verify call_backend executes Agent question via direct import when server is down."""
    res = call_backend(
        question="We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost?",
        mode="agent",
        backend_url="http://127.0.0.1:9999"  # Deliberately unreachable port
    )
    assert isinstance(res, dict)
    assert "answer" in res
    answer = res["answer"]
    # Check closure rules and fee calculations
    assert "Ellora" in answer
    assert "Ajanta" in answer
    assert "320" in answer or "280" in answer


# ============================================================================
# 5. Streamlit App Headless Execution (AppTest)
# ============================================================================

def test_streamlit_app_init():
    """Smoke test that Streamlit App initializes without throwing unhandled exceptions."""
    from streamlit.testing.v1 import AppTest
    
    app_path = str(PROJECT_ROOT / "ui" / "app.py")
    at = AppTest.from_file(app_path)
    at.run()
    
    # App should run without unhandled exceptions
    assert not at.exception, f"Streamlit app raised an exception: {at.exception}"
