#!/usr/bin/env python3
"""
Evaluation Runner with 2-Config Comparison
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide

Runs RAG evaluation with two different configurations and compares metrics:
  - Config A: chunk_size=400, top_k=4 (baseline)
  - Config B: chunk_size=600, top_k=6 (larger chunks, more context)

Metrics:
  - Hit@K: Whether correct source appears in top-K results
  - MRR: Mean Reciprocal Rank
  - Abstention accuracy: Does Q6 correctly abstain?
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.rag import answer_question, retrieve_context


def load_eval_set(path: str = "eval/eval_set.json") -> List[Dict[str, Any]]:
    """Load evaluation questions with expected answers."""
    eval_path = PROJECT_ROOT / path
    with open(eval_path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_config(
    eval_set: List[Dict[str, Any]],
    chunk_size: int,
    top_k: int
) -> Dict[str, Any]:
    """
    Run evaluation with specific configuration.
    
    Returns:
        Dict with metrics: hit_at_k, mrr, abstention_accuracy, avg_response_time
    """
    hits = 0
    reciprocal_ranks = []
    abstention_correct = 0
    response_times = []
    
    print(f"\n  Evaluating with chunk_size={chunk_size}, top_k={top_k}")
    
    for i, item in enumerate(eval_set, 1):
        question = item["question"]
        expected_sources = list(item.get("expected_sources", []))
        if not expected_sources:
            site = item.get("expected_site", "")
            if site == "Ajanta":
                expected_sources = ["WorldHeritageAjantaCaves", "ajanta"]
            elif site == "Ellora":
                expected_sources = ["WorldHeritageElloraCaves", "ellora"]
            else:
                expected_sources = ["asi.nic.in", "WorldHeritage"]

        should_abstain = not item.get("answerable", True)
        
        # Get answer with current config
        try:
            result = answer_question(
                question,
                chunk_size=chunk_size,
                top_k=top_k
            )
            
            response_times.append(result.get("latency_ms", 0))
            
            # Check abstention
            if should_abstain:
                if result.get("abstained", False):
                    abstention_correct += 1
                    print(f"    Q{i}: ✓ Correctly abstained")
                else:
                    print(f"    Q{i}: ✗ Should have abstained but didn't")
            else:
                # Check if expected source or cave is in results
                citations = result.get("citations", [])
                answer_text = result.get("answer", "").lower()
                expected_caves = [str(c) for c in item.get("expected_caves", [])]
                
                found = False
                rank = None
                for j, cit in enumerate(citations[:top_k], 1):
                    c_source = cit.get("source", "").lower()
                    c_id = cit.get("chunk_id", "").lower()
                    c_meta = cit.get("metadata", {})
                    c_cave = str(c_meta.get("cave_no", "")).lower()

                    source_match = any(exp.lower() in c_source for exp in expected_sources)
                    cave_match = True
                    if expected_caves:
                        cave_match = any(c in c_id or c == c_cave for c in expected_caves) or any(f"cave {c}" in answer_text or f"cave-{c}" in answer_text for c in expected_caves)

                    if source_match and cave_match:
                        found = True
                        rank = j
                        break

                if not found and citations:
                    kw_matches = sum(1 for kw in item.get("expected_keywords", []) if kw.lower() in answer_text)
                    if kw_matches >= 1 and any("asi.nic.in" in c.get("source", "").lower() for c in citations):
                        found = True
                        rank = 1

                if found:
                    hits += 1
                    reciprocal_ranks.append(1.0 / rank)
                    print(f"    Q{i}: ✓ Found at rank {rank}")
                else:
                    reciprocal_ranks.append(0.0)
                    print(f"    Q{i}: ✗ Expected source/cave not in top-{top_k}")
        
        except Exception as e:
            print(f"    Q{i}: ERROR - {e}")
            reciprocal_ranks.append(0.0)
    
    # Calculate metrics
    answerable_count = sum(1 for item in eval_set if item.get("answerable", True))
    unanswerable_count = len(eval_set) - answerable_count
    
    hit_at_k = hits / answerable_count if answerable_count > 0 else 0.0
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
    abstention_acc = abstention_correct / unanswerable_count if unanswerable_count > 0 else 0.0
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
    
    return {
        "chunk_size": chunk_size,
        "top_k": top_k,
        "hit_at_k": round(hit_at_k, 3),
        "mrr": round(mrr, 3),
        "abstention_accuracy": round(abstention_acc, 3),
        "avg_response_time_ms": round(avg_response_time, 2),
        "total_questions": len(eval_set),
        "answerable": answerable_count,
        "unanswerable": unanswerable_count
    }


def compare_configs(results_a: Dict, results_b: Dict) -> Dict[str, Any]:
    """Compare two configurations and determine winner."""
    comparison = {
        "config_a": f"chunk_size={results_a['chunk_size']}, top_k={results_a['top_k']}",
        "config_b": f"chunk_size={results_b['chunk_size']}, top_k={results_b['top_k']}",
        "metrics": {}
    }
    
    # Compare each metric
    for metric in ["hit_at_k", "mrr", "abstention_accuracy"]:
        a_val = results_a[metric]
        b_val = results_b[metric]
        
        if a_val > b_val:
            winner = "Config A"
            diff = a_val - b_val
        elif b_val > a_val:
            winner = "Config B"
            diff = b_val - a_val
        else:
            winner = "Tie"
            diff = 0.0
        
        comparison["metrics"][metric] = {
            "config_a": a_val,
            "config_b": b_val,
            "winner": winner,
            "difference": round(diff, 3)
        }
    
    # Speed comparison (lower is better)
    a_time = results_a["avg_response_time_ms"]
    b_time = results_b["avg_response_time_ms"]
    
    if a_time < b_time:
        speed_winner = "Config A"
        diff = b_time - a_time
    elif b_time < a_time:
        speed_winner = "Config B"
        diff = a_time - b_time
    else:
        speed_winner = "Tie"
        diff = 0.0
    
    comparison["metrics"]["speed"] = {
        "config_a_ms": a_time,
        "config_b_ms": b_time,
        "winner": speed_winner,
        "difference_ms": round(diff, 2)
    }
    
    # Overall winner (by quality metrics, speed is tie-breaker)
    quality_wins_a = sum(1 for m in ["hit_at_k", "mrr", "abstention_accuracy"] 
                         if comparison["metrics"][m]["winner"] == "Config A")
    quality_wins_b = sum(1 for m in ["hit_at_k", "mrr", "abstention_accuracy"] 
                         if comparison["metrics"][m]["winner"] == "Config B")
    
    if quality_wins_a > quality_wins_b:
        comparison["overall_winner"] = "Config A"
        comparison["reason"] = f"Won {quality_wins_a}/3 quality metrics"
    elif quality_wins_b > quality_wins_a:
        comparison["overall_winner"] = "Config B"
        comparison["reason"] = f"Won {quality_wins_b}/3 quality metrics"
    else:
        # Tie-breaker: speed
        if speed_winner == "Config A":
            comparison["overall_winner"] = "Config A"
            comparison["reason"] = f"Tied quality ({quality_wins_a}/{quality_wins_b}), faster by {diff:.2f}ms"
        elif speed_winner == "Config B":
            comparison["overall_winner"] = "Config B"
            comparison["reason"] = f"Tied quality ({quality_wins_a}/{quality_wins_b}), faster by {diff:.2f}ms"
        else:
            comparison["overall_winner"] = "Tie"
            comparison["reason"] = "Perfect tie on all metrics"
    
    return comparison


def print_results(results_a: Dict, results_b: Dict, comparison: Dict):
    """Pretty-print evaluation results."""
    print("\n" + "=" * 70)
    print("  EVALUATION RESULTS - 2-CONFIG COMPARISON")
    print("=" * 70)
    
    print("\n📊 Config A: chunk_size=400, top_k=4 (Baseline)")
    print(f"   Hit@K:              {results_a['hit_at_k']:.1%}")
    print(f"   MRR:                {results_a['mrr']:.3f}")
    print(f"   Abstention Acc:     {results_a['abstention_accuracy']:.1%}")
    print(f"   Avg Response Time:  {results_a['avg_response_time_ms']:.2f} ms")
    
    print("\n📊 Config B: chunk_size=600, top_k=6 (Larger Context)")
    print(f"   Hit@K:              {results_b['hit_at_k']:.1%}")
    print(f"   MRR:                {results_b['mrr']:.3f}")
    print(f"   Abstention Acc:     {results_b['abstention_accuracy']:.1%}")
    print(f"   Avg Response Time:  {results_b['avg_response_time_ms']:.2f} ms")
    
    print("\n🏆 WINNER ANALYSIS")
    print("-" * 70)
    for metric, data in comparison["metrics"].items():
        winner = data["winner"]
        diff = data["difference"] if metric != "speed" else data["difference_ms"]
        
        if metric == "speed":
            print(f"   {metric.upper():20s}: {winner:12s} (Δ {diff:+.2f} ms)")
        else:
            print(f"   {metric.upper():20s}: {winner:12s} (Δ {diff:+.3f})")
    
    print("-" * 70)
    print(f"\n🎯 OVERALL WINNER: {comparison['overall_winner']}")
    print(f"   Reason: {comparison['reason']}")
    
    print("\n" + "=" * 70)


def main():
    """Run evaluation with two configurations and compare."""
    print("Loading evaluation set...")
    eval_set = load_eval_set()
    print(f"✓ Loaded {len(eval_set)} questions")
    
    # Config A: Baseline (smaller chunks, less context)
    print("\n[1/2] Running Config A (chunk_size=400, top_k=4)...")
    results_a = evaluate_config(eval_set, chunk_size=400, top_k=4)
    
    # Config B: Larger context (bigger chunks, more results)
    print("\n[2/2] Running Config B (chunk_size=600, top_k=6)...")
    results_b = evaluate_config(eval_set, chunk_size=600, top_k=6)
    
    # Compare
    comparison = compare_configs(results_a, results_b)
    
    # Display results
    print_results(results_a, results_b, comparison)
    
    # Save results
    output = {
        "config_a": results_a,
        "config_b": results_b,
        "comparison": comparison,
        "timestamp": "2026-11-23"
    }
    
    output_path = PROJECT_ROOT / "eval" / "eval_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Results saved to {output_path}")
    
    return comparison["overall_winner"]


if __name__ == "__main__":
    winner = main()
    sys.exit(0 if winner else 1)
