#!/usr/bin/env python3
"""
benchmark.py — Run the 10 golden questions and report latency, tokens, cache hits.
Uses the FastAPI TestClient to avoid needing a running server.
"""

import json
import statistics
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Force offline/fake mode for benchmarking
import os

os.environ.setdefault("LLM_PROVIDER", "fake")

from fastapi.testclient import TestClient

from app.main import app

GOLDEN_QUESTIONS = [
    "Which day is Ellora closed? And Ajanta?",
    "What is special about the Kailasa temple in Ellora cave 16?",
    "Which caves in Ajanta have the best paintings?",
    "We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost?",
    "Make a 3-hour plan for Ellora covering Buddhist, Hindu and Jain caves.",
    "How many tourists visited Ajanta caves last Diwali?",
    "Is Ajanta open on Monday?",
    "What is the entry fee for Ajanta for Indians?",
    "Which Ellora caves are Jain?",
    "Ajanta cave 26 में काय खास आहे?",
]


def run_benchmark():
    client = TestClient(app)

    print("=" * 70)
    print("LeniGuide Benchmark — 10 Golden Questions")
    print("=" * 70)

    latencies = []
    cache_hits = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    results = []

    for i, q in enumerate(GOLDEN_QUESTIONS, 1):
        start = time.perf_counter()
        resp = client.post("/ask", json={"question": q})
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

        data = resp.json()
        meta = data.get("meta", {})
        is_cache_hit = meta.get("cache_hit", False)
        if is_cache_hit:
            cache_hits += 1
        total_prompt_tokens += meta.get("prompt_tokens", 0)
        total_completion_tokens += meta.get("completion_tokens", 0)

        status = "ABSTAINED" if data.get("abstained") else "ANSWERED"
        print(f"  Q{i:2d}: {elapsed_ms:7.1f} ms | {status:9s} | cache={'HIT' if is_cache_hit else 'MISS'} | {q[:50]}")

        results.append({
            "question": q,
            "latency_ms": round(elapsed_ms, 2),
            "status": status,
            "cache_hit": is_cache_hit,
            "confidence": data.get("confidence", ""),
            "answer_preview": data.get("answer", "")[:80],
        })

    # Run again for cache hits
    print("\n--- Second pass (cache expected) ---")
    for i, q in enumerate(GOLDEN_QUESTIONS, 1):
        start = time.perf_counter()
        resp = client.post("/ask", json={"question": q})
        elapsed_ms = (time.perf_counter() - start) * 1000
        data = resp.json()
        meta = data.get("meta", {})
        is_cache_hit = meta.get("cache_hit", False)
        if is_cache_hit:
            cache_hits += 1
        print(f"  Q{i:2d}: {elapsed_ms:7.1f} ms | cache={'HIT' if is_cache_hit else 'MISS'}")

    # Summary
    sorted_lat = sorted(latencies)
    p50 = sorted_lat[len(sorted_lat) // 2]
    p95_idx = int(len(sorted_lat) * 0.95)
    p95 = sorted_lat[min(p95_idx, len(sorted_lat) - 1)]

    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY (with FakeLLM)")
    print("=" * 70)
    print(f"  Questions run:          {len(GOLDEN_QUESTIONS)}")
    print(f"  p50 latency:            {p50:.1f} ms")
    print(f"  p95 latency:            {p95:.1f} ms")
    print(f"  Avg latency:            {statistics.mean(latencies):.1f} ms")
    print(f"  Total prompt tokens:    {total_prompt_tokens}")
    print(f"  Total completion tokens: {total_completion_tokens}")
    print(f"  Avg tokens/request:     {(total_prompt_tokens + total_completion_tokens) / len(GOLDEN_QUESTIONS):.0f}")
    print(f"  Cache hits (pass 2):    {cache_hits}/{len(GOLDEN_QUESTIONS) * 2}")
    print(f"  Cache hit rate (pass 2): {cache_hits / (len(GOLDEN_QUESTIONS) * 2) * 100:.0f}%")
    print("=" * 70)

    # Write results
    results_dir = PROJECT_ROOT / "eval" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "p50_ms": round(p50, 2),
            "p95_ms": round(p95, 2),
            "avg_ms": round(statistics.mean(latencies), 2),
            "cache_hit_rate": round(cache_hits / (len(GOLDEN_QUESTIONS) * 2) * 100, 1),
            "total_prompt_tokens": total_prompt_tokens,
            "total_completion_tokens": total_completion_tokens,
            "mode": "FakeLLM",
            "results": results,
        }, f, indent=2)
    print("\nResults saved to eval/results/benchmark_results.json")


if __name__ == "__main__":
    run_benchmark()
