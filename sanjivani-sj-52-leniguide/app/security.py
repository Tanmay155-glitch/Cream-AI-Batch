"""
Security guardrails for LeniGuide production API.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide (Ajanta & Ellora UNESCO Heritage Guide)

Provides:
- Input length enforcement (MAX_QUERY_LENGTH = 500 characters).
- Prompt-injection detection via compiled regex patterns.
- Safe refusal responses that never leak system prompt content.
"""

import re
from typing import Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_QUERY_LENGTH = 500

# Compiled regex patterns for adversarial prompt-injection attempts.
# Each pattern matches a known instruction-override technique.
_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+previous\s+instructions", re.IGNORECASE),
    re.compile(r"ignore\s+all\s+instructions", re.IGNORECASE),
    re.compile(r"system\s+prompt", re.IGNORECASE),
    re.compile(r"you\s+are\s+now", re.IGNORECASE),
    re.compile(r"disregard\s+your\s+rules", re.IGNORECASE),
    re.compile(r"reveal\s+your\s+instructions", re.IGNORECASE),
    re.compile(r"bypass", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
]

INJECTION_REFUSAL = (
    "I'm sorry, but I cannot process this request. "
    "LeniGuide only answers factual questions about Ajanta and Ellora caves "
    "based on official ASI records."
)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------
def validate_query_length(query: str) -> Tuple[bool, str]:
    """
    Validate that the query is non-empty and within the allowed character limit.

    Returns:
        (is_valid, error_message)  — error_message is empty when valid.
    """
    stripped = query.strip()
    if len(stripped) == 0:
        return False, "Query must not be empty."
    if len(query) > MAX_QUERY_LENGTH:
        return False, f"Query exceeds maximum allowed length of {MAX_QUERY_LENGTH} characters."
    return True, ""


def detect_prompt_injection(query: str) -> bool:
    """
    Return ``True`` when the query contains a known adversarial
    instruction-override pattern, ``False`` otherwise.
    """
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(query):
            return True
    return False
