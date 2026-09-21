"""
Comprehensive unit and integration test suite for the Hybrid Standards Retrieval Engine.
Covers lexical search, dense embeddings, versioning, fusion, reranking, evidence, API, and failure modes.
"""

import json
from pathlib import Path
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.standard import IndianStandard, StandardEdition, StandardStatus
from app.models.clause import Clause
from app.models.requirement import (
    ProcurementSpecification,
    Requirement,
    TechnicalParameter,
    RequirementType,
    RequirementExtractionStatus,
)
from app.models.retrieval import (
    StandardIndexEntry,
    RetrievalRun,
    RetrievalCandidate,
    RetrievalEvidence,
    RetrievalRunStatus,
    EvidenceType,
)
from app.services.retrieval.embeddings import (
    DeterministicMockEmbeddingProvider,
    EmbeddingVersionMismatchError,
    get_embedding_provider,
)
from app.services.retrieval.lexical import LexicalSearchEngine, LexicalDocument, tokenize
from app.services.retrieval.query_builder import DeterministicQueryBuilder
from app.services.retrieval.metadata_filter import StandardsMetadataFilter, FilterCriteria
from app.services.retrieval.fusion import CandidateFusion
from app.services.retrieval.reranker import DeterministicFeatureReranker
from app.services.retrieval.indexer import StandardsIndexer
from app.services.retrieval.engine import HybridRetrievalEngine
from app.services.retrieval.evaluation import (
    compute_recall_at_k,
    compute_precision_at_k,
    compute_reciprocal_rank,
    compute_ndcg_at_k,
    evaluate_dataset,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def seed_synthetic_standards(db: Session) -> list[IndianStandard]:
    """Helper to seed isolated synthetic test standards into the test DB."""
    fixture_path = FIXTURES_DIR / "synthetic_standards_pool.json"
    with open(fixture_path, "r") as f:
        data = json.load(f)

    standards = []
    for item in data["standards"]:
        std = IndianStandard(
            standard_number=item["standard_number"],
            title=item["title"],
            scope=item["scope"],
            division_code=item["division_code"],
            status=StandardStatus(item["status"]),
            is_mandatory_qco=item["is_mandatory_qco"],
            qco_reference=item.get("qco_reference"),
        )
        db.add(std)
        db.flush()

        ed = StandardEdition(
            standard_id=std.id,
            edition_number=1,
            year=item["year"],
            is_current=True,
        )
        db.add(ed)
        db.flush()

        for c_data in item.get("clauses", []):
            clause = Clause(
                edition_id=ed.id,
                clause_number=c_data["clause_number"],
                content=c_data["content"],
            )
            db.add(clause)

        standards.append(std)

    db.commit()
    return standards


# =============================================================================
# 1. Lexical Retrieval Unit Tests
# =============================================================================

def test_lexical_tokenization():
    """Verify tokenizer correctly removes punctuation and stopwords while expanding hyphens."""
    text = "Three-phase induction motor of 15 kW per IS 12615"
    tokens = tokenize(text)
    assert "motor" in tokens
    assert "induction" in tokens
    assert "three" in tokens
    assert "phase" in tokens
    assert "12615" in tokens
    # Stopwords like 'of', 'per' should be excluded
    assert "of" not in tokens
    assert "per" not in tokens


def test_lexical_bm25_ranking():
    """Verify BM25 correctly matches relevant documents and orders by relevance."""
    engine = LexicalSearchEngine()
    docs = [
        LexicalDocument(
            standard_id=1,
            standard_number="IS 12615",
            title="Three-Phase A.C. Motors Specification",
            scope="Energy efficient three-phase squirrel cage induction motor requirements.",
        ),
        LexicalDocument(
            standard_id=2,
            standard_number="IS 4984",
            title="Polyethylene Pipes for Water Supply",
            scope="HDPE pipes for potable water conveyance.",
        ),
    ]
    engine.index_documents(docs)

    results = engine.search("squirrel cage induction motor", top_k=5)
    assert len(results) > 0
    assert results[0].standard_number == "IS 12615"
    assert results[0].rank == 1
    assert "motor" in results[0].matched_tokens or "induction" in results[0].matched_tokens
    assert results[0].bm25_score > 0.0


# =============================================================================
# 2. Dense Semantic Embedding & Versioning Tests
# =============================================================================

def test_deterministic_mock_embedding():
    """Verify mock embedding provider generates reproducible unit-norm vectors."""
    provider = DeterministicMockEmbeddingProvider(dimension=128)
    v1 = provider.embed_text("Three-phase induction motor")
    v2 = provider.embed_text("Three-phase induction motor")
    v3 = provider.embed_text("Completely unrelated plastic pipe for sewage")

    assert len(v1) == 128
    assert v1 == v2  # 100% deterministic

    # Cosine similarity of identical queries must be ~1.0
    dot_same = sum(a * b for a, b in zip(v1, v2))
    assert pytest.approx(dot_same, abs=1e-4) == 1.0

    # Similar concepts have higher dot product than dissimilar
    v_motor = provider.embed_text("electric motor drive")
    dot_related = sum(a * b for a, b in zip(v1, v_motor))
    dot_unrelated = sum(a * b for a, b in zip(v1, v3))
    assert dot_related > dot_unrelated


def test_embedding_version_mismatch_rejection(db_session: Session):
    """Verify that an index entry created with a different model triggers an explicit mismatch error."""
    std = IndianStandard(
        standard_number="IS 1111",
        title="Test Standard",
        scope="Testing scope",
        status=StandardStatus.ACTIVE,
    )
    db_session.add(std)
    db_session.flush()

    # Manually insert index entry with outdated model
    entry = StandardIndexEntry(
        standard_id=std.id,
        index_version="v1.0",
        embedding_model="outdated-deprecated-model",
        embedding_dimension=256,
        content_hash="dummyhash",
        indexed_text="Dummy indexed text",
        embedding_vector=[0.0] * 256,
    )
    db_session.add(entry)
    db_session.commit()

    indexer = StandardsIndexer(provider=DeterministicMockEmbeddingProvider(dimension=128))
    with pytest.raises(EmbeddingVersionMismatchError) as exc_info:
        indexer.load_lexical_and_dense_indices(db_session)

    assert "outdated-deprecated-model" in str(exc_info.value)


# =============================================================================
# 3. Metadata Filtering & Candidate Fusion Tests
# =============================================================================

def test_metadata_filtering():
    """Verify metadata filtering logic handles withdrawn standards and QCO requirements."""
    meta_active = {
        "status": "ACTIVE",
        "division_code": "ETD",
        "is_mandatory_qco": True,
        "qco_reference": "Electrical QCO 2020",
    }
    meta_withdrawn = {
        "status": "WITHDRAWN",
        "division_code": "MED",
        "is_mandatory_qco": False,
    }

    # By default, withdrawn should be excluded when include_withdrawn is False
    criteria_normal = FilterCriteria(include_withdrawn=False)
    passes_act, score_act, reasons_act = StandardsMetadataFilter.evaluate(meta_active, criteria_normal)
    passes_wtd, score_wtd, reasons_wtd = StandardsMetadataFilter.evaluate(meta_withdrawn, criteria_normal)

    assert passes_act is True
    assert score_act >= 0.70
    assert any("QCO" in r for r in reasons_act)

    assert passes_wtd is False
    assert score_wtd == 0.0

    # Division filter
    crit_div = FilterCriteria(division_code="ETD")
    passes_div_ok, _, _ = StandardsMetadataFilter.evaluate(meta_active, crit_div)
    passes_div_fail, _, _ = StandardsMetadataFilter.evaluate(
        {"status": "ACTIVE", "division_code": "CED"}, crit_div
    )
    assert passes_div_ok is True
    assert passes_div_fail is False


def test_candidate_fusion_rrf():
    """Verify Reciprocal Rank Fusion merges candidate lists and preserves component scores."""
    from app.services.retrieval.lexical import LexicalSearchResult
    from app.services.retrieval.engine import DenseSearchResult

    lex_results = [
        LexicalSearchResult(standard_id=1, standard_number="IS 12615", title="Motor Spec", bm25_score=10.0, normalized_score=1.0, matched_tokens=["motor"], rank=1),
        LexicalSearchResult(standard_id=2, standard_number="IS 4984", title="Pipe Spec", bm25_score=5.0, normalized_score=0.5, matched_tokens=["pipe"], rank=2),
    ]
    dense_results = [
        DenseSearchResult(standard_id=1, standard_number="IS 12615", title="Motor Spec", semantic_score=0.92, scope_text="Motor scope", rank=1),
        DenseSearchResult(standard_id=3, standard_number="IS 2062", title="Steel Spec", semantic_score=0.70, scope_text="Steel scope", rank=2),
    ]

    fusion = CandidateFusion(k_rrf=60)
    fused = fusion.fuse(lex_results, dense_results)

    assert len(fused) == 3
    top = fused[0]
    assert top.standard_id == 1
    assert top.standard_number == "IS 12615"
    assert top.lexical_rank == 1
    assert top.semantic_rank == 1
    assert top.lexical_score == 1.0
    assert top.semantic_score == 0.92
    assert top.rrf_score == 1.0  # normalized max


# =============================================================================
# 4. Reranking & Retrieval Evidence Tests
# =============================================================================

def test_deterministic_feature_reranker():
    """Verify reranker elevates candidates with explicit standard citations and title match."""
    from app.services.retrieval.fusion import CandidateDraft

    cands = [
        CandidateDraft(
            standard_id=1,
            standard_number="IS 4984",
            title="HDPE Pipes for Water Supply",
            scope_text="Specification for high density polyethylene pipes",
            rrf_score=0.6,
        ),
        CandidateDraft(
            standard_id=2,
            standard_number="IS 12615",
            title="Three-Phase Induction Motors",
            scope_text="Efficiency classes for electric motors",
            rrf_score=0.5,
        ),
    ]

    reranker = DeterministicFeatureReranker()
    # Query explicitly cites IS 12615
    reranked = reranker.rerank(
        query="Motor specification per IS 12615",
        candidates=cands,
        explicit_citations=["IS 12615"],
    )

    assert reranked[0].standard_number == "IS 12615"
    assert reranked[0].rerank_score > reranked[1].rerank_score
    assert any("Explicit reference" in r for r in reranked[0].match_reasons)


# =============================================================================
# 5. Empty Knowledge Base & Safety Tests
# =============================================================================

def test_empty_knowledge_base_safety(db_session: Session):
    """Verify that when 0 verified standards exist, retrieval returns EMPTY_KB without hallucinating."""
    # Ensure DB has 0 standards
    assert db_session.query(IndianStandard).count() == 0

    spec = ProcurementSpecification(
        title="Empty Spec",
        raw_content="Need 50 kW motor per standards.",
        status="COMPLETED",
    )
    db_session.add(spec)
    db_session.flush()

    req = Requirement(
        specification_id=spec.id,
        requirement_type=RequirementType.ELECTRICAL if hasattr(RequirementType, "ELECTRICAL") else RequirementType.MATERIAL,
        extraction_status=RequirementExtractionStatus.EXPLICIT,
        extracted_text="Motor 50 kW 415V.",
    )
    db_session.add(req)
    db_session.commit()

    engine = HybridRetrievalEngine()
    run = engine.retrieve_for_requirement(db=db_session, requirement=req)

    assert run.status == RetrievalRunStatus.EMPTY_KB
    assert "NO_VERIFIED_STANDARDS" in run.error_message
    assert len(run.candidates) == 0


# =============================================================================
# 6. End-to-End Hybrid Engine & Evidence Verification
# =============================================================================

def test_hybrid_engine_end_to_end(db_session: Session):
    """Verify full retrieval pipeline with real evidence tracking on seeded standards."""
    seed_synthetic_standards(db_session)

    spec = ProcurementSpecification(
        title="Municipal Water Supply Tender",
        target_product_name="HDPE Pipes",
        raw_content="HDPE pipes PN 10 for potable water conveyance.",
        status="COMPLETED",
    )
    db_session.add(spec)
    db_session.flush()

    req = Requirement(
        specification_id=spec.id,
        requirement_type=RequirementType.MATERIAL,
        extraction_status=RequirementExtractionStatus.EXPLICIT,
        extracted_text="High density polyethylene (HDPE) pipes for potable water conveyance rating PN 10.",
    )
    db_session.add(req)
    db_session.flush()

    param = TechnicalParameter(
        requirement_id=req.id,
        name="Pressure Rating",
        original_value="PN 10",
        normalized_value="10 bar",
        target_value="10 bar",
    )
    db_session.add(param)
    db_session.commit()

    engine = HybridRetrievalEngine()
    run = engine.retrieve_for_requirement(db=db_session, requirement=req, top_k=3)

    assert run.status == RetrievalRunStatus.COMPLETED
    assert len(run.candidates) > 0

    top_cand = run.candidates[0]
    assert top_cand.standard.standard_number == "IS 4984"
    assert top_cand.rank == 1
    assert top_cand.final_retrieval_score > 0.0

    # Verify component scores exist and are not collapsed
    assert top_cand.lexical_score > 0.0
    assert top_cand.semantic_score > 0.0
    assert top_cand.metadata_score > 0.0
    assert top_cand.rerank_score > 0.0

    # Verify real evidence records
    assert len(top_cand.evidence) >= 2
    evidence_types = {e.evidence_type for e in top_cand.evidence}
    assert EvidenceType.LEXICAL_MATCH in evidence_types
    assert EvidenceType.SEMANTIC_SIMILARITY in evidence_types


# =============================================================================
# 7. FastAPI API Endpoints Integration Tests
# =============================================================================

def test_api_retrieval_endpoints(client: TestClient, db_session: Session):
    """Test all retrieval API routes via TestClient."""
    seed_synthetic_standards(db_session)

    # 1. Rebuild index endpoint
    resp_rebuild = client.post("/api/v1/retrieval/index/rebuild")
    assert resp_rebuild.status_code == 200
    data_rebuild = resp_rebuild.json()
    assert data_rebuild["success"] is True
    assert data_rebuild["standards_indexed"] >= 4

    # 2. Get index status
    resp_status = client.get("/api/v1/retrieval/index/status")
    assert resp_status.status_code == 200
    data_status = resp_status.json()
    assert data_status["is_indexed"] is True
    assert data_status["total_standards_indexed"] >= 4

    # 3. Create test requirement
    spec = ProcurementSpecification(
        title="Industrial Motor Tender",
        raw_content="Supply of IE3 induction motors.",
        status="COMPLETED",
    )
    db_session.add(spec)
    db_session.flush()

    req = Requirement(
        specification_id=spec.id,
        requirement_type=RequirementType.MATERIAL,
        extraction_status=RequirementExtractionStatus.EXPLICIT,
        extracted_text="Energy efficient three phase squirrel cage induction motor class IE3.",
    )
    db_session.add(req)
    db_session.commit()

    # 4. POST retrieval for requirement
    payload = {
        "top_k": 3,
        "include_withdrawn": False,
        "lexical_weight": 0.5,
        "semantic_weight": 0.5,
    }
    resp_retrieval = client.post(f"/api/v1/retrieval/requirements/{req.id}", json=payload)
    assert resp_retrieval.status_code == 200
    data_run = resp_retrieval.json()

    assert data_run["status"] == "COMPLETED"
    assert data_run["requirement_id"] == req.id
    assert len(data_run["candidates"]) <= 3
    assert data_run["candidates"][0]["standard_number"] == "IS 12615"
    assert "lexical_score" in data_run["candidates"][0]
    assert "semantic_score" in data_run["candidates"][0]
    assert "rerank_score" in data_run["candidates"][0]
    assert "final_retrieval_score" in data_run["candidates"][0]
    assert len(data_run["candidates"][0]["evidence"]) > 0

    run_id = data_run["run_id"]

    # 5. GET past run
    resp_get_run = client.get(f"/api/v1/retrieval/runs/{run_id}")
    assert resp_get_run.status_code == 200
    assert resp_get_run.json()["run_id"] == run_id

    # 6. GET candidates only
    resp_cands = client.get(f"/api/v1/retrieval/runs/{run_id}/candidates")
    assert resp_cands.status_code == 200
    assert len(resp_cands.json()) == len(data_run["candidates"])


def test_api_404_missing_requirement(client: TestClient):
    """Verify 404 is returned when requirement does not exist."""
    resp = client.post("/api/v1/retrieval/requirements/999999", json={"top_k": 5})
    assert resp.status_code == 404
    assert "does not exist" in resp.json()["detail"]


# =============================================================================
# 8. Evaluation Metrics Unit Tests
# =============================================================================

def test_evaluation_metrics_math():
    """Verify Recall@K, Precision@K, MRR, and NDCG math calculations."""
    retrieved = ["IS 12615", "IS 2062", "IS 4984"]
    relevant = {"IS 12615", "IS 4984"}

    # Recall@1: 1 hit out of 2 relevant = 0.5
    assert compute_recall_at_k(retrieved, relevant, 1) == 0.5
    # Recall@3: 2 hits out of 2 relevant = 1.0
    assert compute_recall_at_k(retrieved, relevant, 3) == 1.0

    # Precision@1: 1 hit out of 1 retrieved = 1.0
    assert compute_precision_at_k(retrieved, relevant, 1) == 1.0
    # Precision@3: 2 hits out of 3 retrieved = 2/3
    assert pytest.approx(compute_precision_at_k(retrieved, relevant, 3), abs=1e-3) == 0.667

    # Reciprocal Rank: first hit at rank 1 -> RR = 1.0
    assert compute_reciprocal_rank(retrieved, relevant) == 1.0

    # If first hit at rank 2:
    assert compute_reciprocal_rank(["IS 9999", "IS 12615"], relevant) == 0.5

    # NDCG@3
    ndcg = compute_ndcg_at_k(retrieved, relevant, 3)
    assert 0.0 < ndcg <= 1.0
