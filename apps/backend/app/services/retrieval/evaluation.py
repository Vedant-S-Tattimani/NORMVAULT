"""
Information Retrieval Evaluation Metrics.
Calculates Recall@K, Precision@K, Mean Reciprocal Rank (MRR), and NDCG@K.

ENGINEERING LIMITATION NOTE:
These metrics are purely for software engineering verification and algorithmic sanity checks
against synthetic test sets. They do not constitute proof of real-world procurement validity.
"""

from dataclasses import dataclass, field
import math
from typing import List, Set, Dict, Any


@dataclass
class RetrievalMetrics:
    """Aggregated evaluation metrics across an evaluation dataset."""
    total_queries: int
    recall_at_1: float
    recall_at_3: float
    recall_at_5: float
    precision_at_1: float
    precision_at_3: float
    precision_at_5: float
    mrr: float
    ndcg_at_5: float
    per_query_details: List[Dict[str, Any]] = field(default_factory=list)


def compute_recall_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Recall@K = |Retrieved@K ∩ Relevant| / |Relevant|"""
    if not relevant_ids:
        return 1.0
    top_k = set(retrieved_ids[:k])
    hits = len(top_k & relevant_ids)
    return hits / len(relevant_ids)


def compute_precision_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Precision@K = |Retrieved@K ∩ Relevant| / K"""
    if k <= 0:
        return 0.0
    top_k = set(retrieved_ids[:k])
    hits = len(top_k & relevant_ids)
    return hits / k


def compute_reciprocal_rank(retrieved_ids: List[str], relevant_ids: Set[str]) -> float:
    """Reciprocal Rank (RR) = 1 / rank of first relevant candidate (or 0.0 if not found)"""
    for rank, item_id in enumerate(retrieved_ids, start=1):
        if item_id in relevant_ids:
            return 1.0 / rank
    return 0.0


def compute_dcg_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Discounted Cumulative Gain at K with binary relevance."""
    dcg = 0.0
    for i, item_id in enumerate(retrieved_ids[:k], start=1):
        rel = 1.0 if item_id in relevant_ids else 0.0
        dcg += rel / math.log2(i + 1.0)
    return dcg


def compute_ndcg_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Normalized Discounted Cumulative Gain at K."""
    if not relevant_ids:
        return 1.0
    actual_dcg = compute_dcg_at_k(retrieved_ids, relevant_ids, k)
    
    # Ideal DCG: all relevant items ranked first
    ideal_retrieved = list(relevant_ids)[:k]
    ideal_dcg = 0.0
    for i in range(1, len(ideal_retrieved) + 1):
        ideal_dcg += 1.0 / math.log2(i + 1.0)

    if ideal_dcg == 0.0:
        return 0.0
    return actual_dcg / ideal_dcg


def evaluate_dataset(
    evaluation_runs: List[Dict[str, Any]],
) -> RetrievalMetrics:
    """
    Compute aggregate benchmark metrics over an evaluation run list.
    Each item in evaluation_runs must have:
      - 'retrieved_standards': List[str] (ordered list of standard numbers)
      - 'expected_standards': List[str]
    """
    total = len(evaluation_runs)
    if total == 0:
        return RetrievalMetrics(
            total_queries=0,
            recall_at_1=0.0,
            recall_at_3=0.0,
            recall_at_5=0.0,
            precision_at_1=0.0,
            precision_at_3=0.0,
            precision_at_5=0.0,
            mrr=0.0,
            ndcg_at_5=0.0,
        )

    r1_sum = 0.0
    r3_sum = 0.0
    r5_sum = 0.0
    p1_sum = 0.0
    p3_sum = 0.0
    p5_sum = 0.0
    rr_sum = 0.0
    ndcg5_sum = 0.0
    details = []

    for run in evaluation_runs:
        retrieved = [s.upper().strip() for s in run.get("retrieved_standards", [])]
        expected = {s.upper().strip() for s in run.get("expected_standards", [])}

        r1 = compute_recall_at_k(retrieved, expected, 1)
        r3 = compute_recall_at_k(retrieved, expected, 3)
        r5 = compute_recall_at_k(retrieved, expected, 5)

        p1 = compute_precision_at_k(retrieved, expected, 1)
        p3 = compute_precision_at_k(retrieved, expected, 3)
        p5 = compute_precision_at_k(retrieved, expected, 5)

        rr = compute_reciprocal_rank(retrieved, expected)
        ndcg5 = compute_ndcg_at_k(retrieved, expected, 5)

        r1_sum += r1
        r3_sum += r3
        r5_sum += r5
        p1_sum += p1
        p3_sum += p3
        p5_sum += p5
        rr_sum += rr
        ndcg5_sum += ndcg5

        details.append({
            "case_id": run.get("case_id"),
            "r@1": r1,
            "r@3": r3,
            "r@5": r5,
            "rr": rr,
            "ndcg@5": ndcg5,
        })

    return RetrievalMetrics(
        total_queries=total,
        recall_at_1=round(r1_sum / total, 4),
        recall_at_3=round(r3_sum / total, 4),
        recall_at_5=round(r5_sum / total, 4),
        precision_at_1=round(p1_sum / total, 4),
        precision_at_3=round(p3_sum / total, 4),
        precision_at_5=round(p5_sum / total, 4),
        mrr=round(rr_sum / total, 4),
        ndcg_at_5=round(ndcg5_sum / total, 4),
        per_query_details=details,
    )
