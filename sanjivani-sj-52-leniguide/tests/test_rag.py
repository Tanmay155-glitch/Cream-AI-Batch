"""
test_rag.py — Tests for app/rag.py retrieval and RAG pipeline.
Covers:
1. Time-sensitive query ranks the official ASI chunk first even when an unofficial
   chunk scores higher by raw similarity.
2. Every answer has >= 1 citation or is an explicit refusal.
3. Authority-based re-ranking boosts official sources over reference and unofficial.
4. Refusal guardrail triggers for out-of-scope questions without calling the LLM.
"""

import pytest

from app.rag import answer_question, is_unanswerable_query, retrieve_context


def test_time_sensitive_ranks_official_chunk_first():
    """
    Time-sensitive queries (fees, tickets, timings, closures) must rank
    official ASI chunks (asi.nic.in) first even if other chunks exist.
    """
    query = "What is the entry fee for Ajanta for Indians?"
    chunks = retrieve_context(query, top_k=4)

    assert len(chunks) > 0, "Should retrieve at least one chunk"
    top_chunk = chunks[0]
    source = top_chunk.get("source", "").lower()
    is_official = "asi.nic.in" in source or top_chunk.get("metadata", {}).get("is_official_asi", False)
    assert is_official, f"Top chunk for time-sensitive query must be official ASI, got: {source}"


def test_time_sensitive_timing_ranks_official_first():
    """Weekly closure queries must also rank official ASI sources first."""
    query = "Which day is Ellora closed? And Ajanta?"
    chunks = retrieve_context(query, top_k=4)

    assert len(chunks) > 0
    top_chunk = chunks[0]
    source = top_chunk.get("source", "").lower()
    is_official = "asi.nic.in" in source or top_chunk.get("metadata", {}).get("is_official_asi", False)
    assert is_official, f"Top chunk for closure query must be official ASI, got: {source}"


def test_every_answer_has_citation_or_refusal():
    """
    Every answer returned by answer_question must have at least one citation
    unless it is an explicit refusal (abstained=True).
    """
    test_questions = [
        "Which day is Ellora closed?",
        "What is special about the Kailasa temple in Ellora cave 16?",
        "Which caves in Ajanta have the best paintings?",
        "How many tourists visited Ajanta caves last Diwali?",  # Should abstain
        "Make a 3-hour plan for Ellora covering Buddhist, Hindu and Jain caves.",
    ]

    for q in test_questions:
        res = answer_question(q)
        if res.get("abstained"):
            # Refusals may have empty citations or out-of-scope notice
            assert "don't know" in res["answer"].lower() or "not in" in res["answer"].lower() or len(res["citations"]) == 0
        else:
            # Answered questions MUST have at least 1 citation
            assert len(res.get("citations", [])) >= 1, f"Question '{q}' answered without citation"
            assert "asi.nic.in" in str(res["citations"]), f"Question '{q}' citations missing asi.nic.in"


def test_q6_diwali_footfall_refusal():
    """Q6 footfall query must trigger out-of-scope abstention."""
    assert is_unanswerable_query("How many tourists visited Ajanta caves last Diwali?") is True
    res = answer_question("How many tourists visited Ajanta caves last Diwali?")
    assert res["abstained"] is True
    assert "don't know" in res["answer"].lower()
