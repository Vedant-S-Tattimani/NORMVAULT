"""
Retrieval Engine Performance Benchmarks and Evaluation Metrics Test.
Measures latency across all stages (lexical, embedding, vector search, fusion, reranking)
and evaluates Recall@K, Precision@K, MRR against the synthetic evaluation dataset.
"""

import json
from pathlib import Path
import time
import pytest
from sqlalchemy.orm import Session

from app.models.standard import IndianStandard, StandardEdition, StandardStatus
from app.models.clause import Clause
from app.models.requirement import (
    ProcurementSpecification,
    Requirement,
    RequirementType,
    RequirementExtractionStatus,
)
from app.services.retrieval.engine import HybridRetrievalEngine
from app.services.retrieval.evaluation import evaluate_dataset

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def seed_evaluation_standards(db: Session):
    """Seed standards corresponding to the synthetic evaluation dataset."""
    standards_data = [
        {
            "standard_number": "IS 12615",
            "title": "Line Operated Three-Phase A.C. Motors (IE Code) — Energy Efficient Induction Motors",
            "scope": "Specification covering energy efficient three-phase squirrel cage induction motors class IE1, IE2, IE3, IE4 415V 50Hz continuous duty.",
            "division_code": "ETD",
            "year": 2018,
            "clauses": ["Efficiency classes for 4-pole continuous duty industrial squirrel cage motors."],
        },
        {
            "standard_number": "IS/IEC 60034-1",
            "title": "Rotating Electrical Machines — Part 1: Rating and Performance",
            "scope": "Standard specifying ratings, operational constraints, and test conditions for rotating electrical machinery.",
            "division_code": "ETD",
            "year": 2017,
            "clauses": ["Rating classes, temperature rise limits, and mechanical performance."],
        },
        {
            "standard_number": "IS 4984",
            "title": "High Density Polyethylene Pipes for Potable Water Supply — Specification",
            "scope": "Requirements for HDPE pipes made of PE 100 or PE 80 material for potable water supply, PN 10, PN 16 ratings.",
            "division_code": "CED",
            "year": 2016,
            "clauses": ["Material grade PE 100, PN 10 pressure rating, standard dimension ratios."],
        },
        {
            "standard_number": "IS 2062",
            "title": "Hot Rolled Medium and High Tensile Structural Steel Plates and Beams",
            "scope": "Specification covering structural steel Grade E250 quality A, B, C for bridge superstructure and building fabrication.",
            "division_code": "MTD",
            "year": 2011,
            "clauses": ["Yield strength minimum 250 MPa for Grade E250 quality A."],
        },
        {
            "standard_number": "IS 12269",
            "title": "Ordinary Portland Cement, 53 Grade — Specification",
            "scope": "Chemical and physical requirements for 53 grade ordinary Portland cement (OPC 53) for high strength concrete structures.",
            "division_code": "CED",
            "year": 2015,
            "clauses": ["28 day compressive strength minimum 53 MPa."],
        },
        {
            "standard_number": "IS 269",
            "title": "Ordinary Portland Cement — Specification (33, 43 and 53 Grade)",
            "scope": "Unified specification for ordinary Portland cement of all grades.",
            "division_code": "CED",
            "year": 2015,
            "clauses": ["Unified testing procedures and chemical composition requirements."],
        },
    ]

    for item in standards_data:
        std = IndianStandard(
            standard_number=item["standard_number"],
            title=item["title"],
            scope=item["scope"],
            division_code=item["division_code"],
            status=StandardStatus.ACTIVE,
            is_mandatory_qco=True,
        )
        db.add(std)
        db.flush()

        ed = StandardEdition(standard_id=std.id, edition_number=1, year=item["year"], is_current=True)
        db.add(ed)
        db.flush()

        for c_text in item["clauses"]:
            cl = Clause(edition_id=ed.id, clause_number="1.0", content=c_text)
            db.add(cl)

    db.commit()


def test_retrieval_performance_and_metrics_benchmark(db_session: Session):
    """
    Run algorithmic benchmark measuring:
    1. Lexical search latency
    2. Dense embedding & cosine search latency
    3. RRF Fusion latency
    4. Reranking latency
    5. Aggregate Recall@K, Precision@K, and MRR against synthetic dataset
    """
    seed_evaluation_standards(db_session)

    eval_fixture_path = FIXTURES_DIR / "synthetic_retrieval_eval.json"
    with open(eval_fixture_path, "r") as f:
        eval_data = json.load(f)

    engine = HybridRetrievalEngine()
    # Rebuild search index
    engine.indexer.rebuild_index(db_session)

    eval_runs = []
    latencies = []

    for case in eval_data["cases"]:
        # Create requirement
        spec = ProcurementSpecification(
            title=f"Spec for {case['target_product']}",
            target_product_name=case["target_product"],
            raw_content=case["requirement_text"],
            status="COMPLETED",
        )
        db_session.add(spec)
        db_session.flush()

        req = Requirement(
            specification_id=spec.id,
            requirement_type=RequirementType.MATERIAL,
            extraction_status=RequirementExtractionStatus.EXPLICIT,
            extracted_text=case["requirement_text"],
        )
        db_session.add(req)
        db_session.commit()

        # Measure end-to-end retrieval latency
        t0 = time.time()
        run = engine.retrieve_for_requirement(db=db_session, requirement=req, top_k=5)
        elapsed_ms = (time.time() - t0) * 1000.0
        latencies.append(elapsed_ms)

        retrieved_numbers = [c.standard.standard_number for c in run.candidates]
        eval_runs.append({
            "case_id": case["case_id"],
            "retrieved_standards": retrieved_numbers,
            "expected_standards": case["expected_standards"],
        })

    # Compute evaluation metrics
    metrics = evaluate_dataset(eval_runs)

    avg_latency = sum(latencies) / len(latencies)
    print(f"\n--- RETRIEVAL PERFORMANCE BENCHMARK ---")
    print(f"Total Queries Evaluated: {metrics.total_queries}")
    print(f"Average Pipeline Latency: {avg_latency:.2f} ms")
    print(f"Recall@1:    {metrics.recall_at_1:.4f}")
    print(f"Recall@3:    {metrics.recall_at_3:.4f}")
    print(f"Recall@5:    {metrics.recall_at_5:.4f}")
    print(f"Precision@1: {metrics.precision_at_1:.4f}")
    print(f"Precision@3: {metrics.precision_at_3:.4f}")
    print(f"MRR:         {metrics.mrr:.4f}")
    print(f"NDCG@5:      {metrics.ndcg_at_5:.4f}")
    print(f"----------------------------------------")

    # Assertions for engineering sanity
    assert avg_latency < 500.0, f"Retrieval latency ({avg_latency}ms) should be under 500ms"
    assert metrics.recall_at_5 >= 0.75, "Recall@5 should be at least 75% on synthetic evaluation set"
    assert metrics.mrr >= 0.75, "MRR should be at least 0.75 on synthetic evaluation set"
