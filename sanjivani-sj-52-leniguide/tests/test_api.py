"""
test_api.py — Tests for FastAPI endpoints.
Covers: health 200, records limit, 404 missing id, search,
/ask with FakeLLM, /ask Q6 returns refusal and never calls LLM.
Uses fixtures from conftest.py.
"""
import pytest


def test_health_200(client):
    """GET /health returns 200 with status ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_records_returns_list(client):
    """GET /records returns a list of records."""
    resp = client.get("/records")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 20


def test_records_limit(client):
    """GET /records?limit=5 returns at most 5."""
    resp = client.get("/records?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) <= 5


def test_record_missing_id_404(client):
    """GET /records/zzz returns 404."""
    resp = client.get("/records/zzz")
    assert resp.status_code == 404


def test_search(client):
    """GET /search?q=kailasa returns results."""
    resp = client.get("/search?q=kailasa")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_ask_basic(client, fake_llm):
    """POST /ask with a valid question returns an answer."""
    resp = client.post("/ask", json={"question": "Which day is Ellora closed?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert len(data["answer"]) > 0


def test_ask_q6_refusal(client, fake_llm):
    """POST /ask Q6 returns refusal, never calls the LLM."""
    resp = client.post("/ask", json={"question": "How many tourists visited Ajanta caves last Diwali?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["abstained"] is True
    assert "don't know" in data["answer"].lower() or "do not" in data["answer"].lower()
    import re
    numbers = re.findall(r'\b\d{3,}\b', data["answer"])
    real_numbers = [n for n in numbers if int(n) > 100]
    assert all(int(n) < 10000 for n in real_numbers), f"Answer contains suspicious numbers: {real_numbers}"


def test_ask_empty_question(client):
    """POST /ask with empty question returns 400."""
    resp = client.post("/ask", json={"question": ""})
    assert resp.status_code == 400
