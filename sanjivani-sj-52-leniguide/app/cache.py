"""
In-memory TTL response cache for LeniGuide production API.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide (Ajanta & Ellora UNESCO Heritage Guide)

Provides:
- Dictionary-based cache keyed by (endpoint, normalised_question).
- Configurable TTL (default 300 s) and max_size (default 128 entries).
- Hit / miss counters for observability metrics reporting.
"""

import time
from typing import Any, Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# TTL Cache Implementation
# ---------------------------------------------------------------------------


class TTLCache:
    """Simple in-memory TTL cache with LRU-style eviction."""

    def __init__(self, ttl_seconds: int = 300, max_size: int = 128) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._store: Dict[Tuple[str, str], Tuple[float, Any]] = {}
        self.hits: int = 0
        self.misses: int = 0

    # -- helpers -------------------------------------------------------------
    @staticmethod
    def _normalize_key(endpoint: str, question: str) -> Tuple[str, str]:
        return (endpoint.lower().strip(), question.lower().strip())

    def _evict_expired(self) -> None:
        now = time.time()
        expired = [k for k, (ts, _) in self._store.items() if now - ts > self.ttl_seconds]
        for k in expired:
            del self._store[k]

    def _evict_oldest(self) -> None:
        """Remove the oldest entry when at capacity."""
        if len(self._store) >= self.max_size:
            oldest_key = min(self._store, key=lambda k: self._store[k][0])
            del self._store[oldest_key]

    # -- public API ----------------------------------------------------------
    def get(self, endpoint: str, question: str) -> Optional[Any]:
        """Return cached response or ``None`` on miss."""
        key = self._normalize_key(endpoint, question)
        entry = self._store.get(key)
        if entry is None:
            self.misses += 1
            return None
        ts, value = entry
        if time.time() - ts > self.ttl_seconds:
            del self._store[key]
            self.misses += 1
            return None
        self.hits += 1
        return value

    def put(self, endpoint: str, question: str, value: Any) -> None:
        """Store a response in the cache."""
        self._evict_expired()
        self._evict_oldest()
        key = self._normalize_key(endpoint, question)
        self._store[key] = (time.time(), value)

    def clear(self) -> None:
        self._store.clear()
        self.hits = 0
        self.misses = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return round(self.hits / total, 4) if total > 0 else 0.0

    def stats(self) -> Dict[str, Any]:
        return {
            "cache_size": len(self._store),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate,
        }


# ---------------------------------------------------------------------------
# Module-level singleton shared by main.py
# ---------------------------------------------------------------------------
response_cache = TTLCache(ttl_seconds=300, max_size=128)
