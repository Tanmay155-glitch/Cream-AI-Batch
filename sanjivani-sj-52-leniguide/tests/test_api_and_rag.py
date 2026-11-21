"""
Day 11/12 – Tests for FastAPI endpoints and RAG pipeline.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide

5 tests: GET /health (+ ASI metadata), GET /records/{id} 404,
         POST /ask (fake LLM), POST /ask Q6 guardrail.
"""


# ============================================================================
# Test 5: GET /health returns 200, status ok, records_count 20, ASI metadata
# ============================================================================
def test_health_endpoint(client):
    """Verify GET /health returns status 200 with records_count == 20 and ASI metadata."""
    resp = client.get("/health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    body = resp.json()
    assert body["status"] == "ok", f"Expected status 'ok', got {body['status']}"
    assert body["records_count"] == 20, f"Expected 20 records, got {body['records_count']}"
    # Day 12: Verify enriched ASI metadata fields from feat/health-asi-metadata
    assert body["project_id"] == "SJ-52", f"Expected project_id 'SJ-52', got {body.get('project_id')}"
    assert "asi_source_verified" in body, "Missing 'asi_source_verified' field in /health"
    assert body["app"] == "LeniGuide", f"Expected app 'LeniGuide', got {body.get('app')}"
    assert "version" in body, "Missing 'version' field in /health"


# ============================================================================
# Test 6: GET /records/Ajanta-999 returns HTTP 404
# ============================================================================
def test_get_record_404_when_missing(client):
    """Verify GET /records/Ajanta-999 returns HTTP 404 for a non-existent cave."""
    resp = client.get("/records/Ajanta-999")
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"


# ============================================================================
# Test 7: POST /ask with fake LLM returns grounded Kailasa answer + ASI citation
# ============================================================================
def test_ask_endpoint_with_fake_llm(client, fake_llm):
    """
    With fake_llm patching RAG internals, POST /ask about Kailasa must
    return HTTP 200 with 'Kailasa' or '16' in the answer and an
    asi.nic.in URL in citations.
    """
    resp = client.post("/ask", json={
        "question": "What is special about the Kailasa temple in Ellora cave 16?"
    })
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    body = resp.json()

    answer_lower = body["answer"].lower()
    assert "kailasa" in answer_lower or "16" in answer_lower, (
        f"'Kailasa' or '16' not found in answer: {body['answer'][:120]}"
    )

    citations_str = str(body.get("citations", []))
    assert "asi.nic.in" in citations_str, (
        f"asi.nic.in not found in citations: {citations_str[:200]}"
    )


# ============================================================================
# Test 8: POST /ask Q6 guardrail returns "I don't know"
# ============================================================================
def test_ask_endpoint_q6_guardrail_i_dont_know(client):
    """
    The Q6 out-of-scope guardrail must trigger for Diwali footfall queries,
    returning HTTP 200 with 'i don't know' in the answer text.
    """
    resp = client.post("/ask", json={
        "question": "How many tourists visited Ajanta caves last Diwali?"
    })
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    body = resp.json()
    assert "i don't know" in body["answer"].lower(), (
        f"Q6 guardrail failed — 'I don't know' not in answer: {body['answer'][:200]}"
    )
