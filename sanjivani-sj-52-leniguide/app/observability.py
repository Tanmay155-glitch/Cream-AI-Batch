"""
Observability instrumentation for LeniGuide production API.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide (Ajanta & Ellora UNESCO Heritage Guide)

Provides:
- Wall-clock latency measurement (time.perf_counter) in milliseconds.
- Token estimation (prompt / completion / total) with offline fallback.
- Estimated USD cost calculation per request.
- Structured JSON logging emitted via Python's logging module.
"""

import json
import logging
import time
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Logger setup — structured JSON lines
# ---------------------------------------------------------------------------
logger = logging.getLogger("leniguide.observability")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Cost rates (USD per 1 K tokens) — Groq Llama-3.1-8B-Instant tier
# ---------------------------------------------------------------------------
COST_PER_1K_PROMPT_TOKENS = 0.00005
COST_PER_1K_COMPLETION_TOKENS = 0.00015


# ---------------------------------------------------------------------------
# Token estimation helpers
# ---------------------------------------------------------------------------
def estimate_tokens(text: str) -> int:
    """Rough token count — 1 token ≈ 4 characters (GPT-family heuristic)."""
    return max(1, len(text) // 4)


def estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """Return estimated USD cost based on Groq Llama-3.1-8B pricing."""
    cost = (prompt_tokens / 1000) * COST_PER_1K_PROMPT_TOKENS + (completion_tokens / 1000) * COST_PER_1K_COMPLETION_TOKENS
    return round(cost, 8)


# ---------------------------------------------------------------------------
# Request lifecycle helpers
# ---------------------------------------------------------------------------
def start_timer() -> float:
    """Return a high-resolution monotonic timestamp."""
    return time.perf_counter()


def compute_latency_ms(start: float) -> float:
    """Return elapsed wall-clock time in milliseconds."""
    return round((time.perf_counter() - start) * 1000, 2)


def build_meta(
    *,
    endpoint: str,
    latency_ms: float,
    prompt_tokens: int,
    completion_tokens: int,
    cache_hit: bool,
    estimated_cost_usd: Optional[float] = None,
) -> Dict[str, Any]:
    """Build the ``meta`` dict attached to every API response."""
    total_tokens = prompt_tokens + completion_tokens
    cost = estimated_cost_usd if estimated_cost_usd is not None else estimate_cost(prompt_tokens, completion_tokens)
    return {
        "latency_ms": latency_ms,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": cost,
        "cache_hit": cache_hit,
    }


def log_request(
    *,
    endpoint: str,
    latency_ms: float,
    prompt_tokens: int,
    completion_tokens: int,
    cache_hit: bool,
    estimated_cost_usd: Optional[float] = None,
    total_tokens: Optional[int] = None,
    **extra: Any,
) -> None:
    """Emit a structured JSON log line for every completed request."""
    if total_tokens is None:
        total_tokens = prompt_tokens + completion_tokens
    cost = estimated_cost_usd if estimated_cost_usd is not None else estimate_cost(prompt_tokens, completion_tokens)
    log_entry = {
        "event": "request_completed",
        "endpoint": endpoint,
        "latency_ms": latency_ms,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": cost,
        "cache_hit": cache_hit,
    }
    logger.info(json.dumps(log_entry))
