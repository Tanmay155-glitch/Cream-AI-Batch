"""
Shared pytest fixtures for LeniGuide Day 11 test suite.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide

Provides:
- session-scoped FastAPI TestClient with pre-initialised app state
- function-scoped fake_llm fixture that patches RAG retrieve + LLM generate
  for 100 % offline, deterministic, < 2-second test runs with zero API keys.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Ensure project root is importable
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Session-scoped TestClient
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def client():
    """
    Create a TestClient with manually initialised global state.

    We skip the async ``startup_event`` (which loads embeddings / ChromaDB)
    and instead inject the minimal state the API endpoints need: 20 cave
    records, the SmartSearch engine, and an offline LLM client.
    """
    import os
    # Ensure offline mode so _ensure_vector_store skips heavy model loads
    os.environ.setdefault("LLM_PROVIDER", "offline")

    import app.main as main_module
    from app.llm import LLMClient
    from app.records import load_records
    from app.smart_search import SmartSearch

    # Pre-set vector store flag BEFORE TestClient triggers startup_event
    main_module._vector_store_ready = True
    main_module.records = load_records()
    main_module.smart_search = SmartSearch(main_module.records)
    main_module.llm_client = LLMClient()

    return TestClient(main_module.app)


# ---------------------------------------------------------------------------
# Deterministic fake-LLM fixture (function scope, via unittest.mock.patch)
# ---------------------------------------------------------------------------
_FAKE_CHUNKS = [
    {
        "text": (
            "Ellora Cave 16 houses the Kailasa Temple, the world's largest "
            "monolithic rock-cut monument, carved top-down from a single "
            "basalt cliff under the Rashtrakuta dynasty (8th century CE)."
        ),
        "title": "Ellora Cave 16 - Kailasa Temple",
        "source": "https://asi.nic.in/pages/WorldHeritageElloraCaves",
        "page": 1,
        "score": 0.95,
        "rerank_score": 0.95,
        "chunk_id": "ellora-16-kailasa-001",
        "metadata": {
            "site": "Ellora",
            "cave_no": "16",
            "is_official_asi": True,
            "source": "https://asi.nic.in/pages/WorldHeritageElloraCaves",
            "source_date": "2026-11",
            "title": "Ellora Cave 16 - Kailasa Temple",
        },
    }
]


def _fake_retrieve(question, top_k=4, chunk_size=400, chunk_overlap=60, site_filter=None):
    """Return deterministic context chunks citing official ASI pages."""
    return list(_FAKE_CHUNKS)


def _fake_generate(question, task="cave_qa", context_records=None, provider=None):
    """Return a deterministic LLM-style answer about the Kailasa Temple."""
    return {
        "answer": (
            "Ellora Cave 16 houses the world-famous Kailasa Temple, the largest "
            "monolithic rock-cut monument on Earth, carved top-down from a single "
            "basalt cliff face under 8th-century Rashtrakuta patronage (King Krishna I). "
            "Source: https://asi.nic.in/pages/WorldHeritageElloraCaves"
        ),
        "confidence": "high",
        "follow_up": "Would you like to know the visiting hours and entry fees?",
    }


@pytest.fixture
def fake_llm():
    """
    Patch ``app.rag.retrieve_context`` and ``app.rag.generate_chat_response``
    so ``POST /ask`` returns a grounded, citation-rich answer about Ellora
    Cave 16 (Kailasa Temple) without hitting any network or LLM API.
    """
    with patch("app.rag.retrieve_context", side_effect=_fake_retrieve):
        with patch("app.rag.generate_chat_response", side_effect=_fake_generate):
            yield
