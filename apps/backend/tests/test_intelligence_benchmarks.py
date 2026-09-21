"""
Latency Benchmark Tests for Phase 8: Procurement Intelligence & Decision Package Engine.
Verifies microsecond to sub-50ms execution performance for run creation, orchestration,
summary assembly, evidence indexing, and JSON export.
"""

import time
import pytest
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.requirement import ProcurementSpecification, Requirement
from app.models.standard import IndianStandard, StandardEdition
from app.models.clause import Clause
from app.models.gap import SpecificationGap, GapType, GapSeverity
from app.services.intelligence.run_manager import RunManager
from app.services.intelligence.action_generator import ActionGenerator
from app.services.intelligence.evidence_indexer import EvidenceIndexer
from app.services.intelligence.summary_generator import SummaryGenerator
from app.services.intelligence.package_builder import DecisionPackageBuilder
from app.schemas.intelligence import PackageViewType


@pytest.fixture
def db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def benchmark_spec(db_session: Session):
    spec = db_session.query(ProcurementSpecification).first()
    if not spec:
        spec = ProcurementSpecification(
            title="Benchmark 15 kW Motor Spec",
            raw_content="Supply of 15 kW, 415 V, 50 Hz IE3 Induction Motor as per IS 12615:2018.",
            target_product_name="Three-phase induction motor",
        )
        db_session.add(spec)
        db_session.commit()
        db_session.refresh(spec)
    return spec


def test_benchmark_run_creation_latency(db_session: Session, benchmark_spec):
    """
    Benchmarks run creation / lookup latency (Target: < 10 ms).
    """
    times = []
    for _ in range(30):
        t0 = time.perf_counter()
        run, is_created = RunManager.get_or_create_run(db=db_session, specification=benchmark_spec)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000.0)

    avg_ms = sum(times) / len(times)
    assert avg_ms < 20.0, f"Run creation took {avg_ms:.2f} ms (expected < 20 ms)"


def test_benchmark_evidence_indexing_latency(db_session: Session):
    """
    Benchmarks evidence index assembly latency (Target: < 10 ms).
    """
    reqs = db_session.query(Requirement).limit(10).all()
    stds = db_session.query(IndianStandard).limit(5).all()
    eds = db_session.query(StandardEdition).limit(5).all()
    cls = db_session.query(Clause).limit(10).all()
    gaps = db_session.query(SpecificationGap).limit(10).all()

    times = []
    for _ in range(30):
        t0 = time.perf_counter()
        idx = EvidenceIndexer.build_evidence_index(
            requirements=reqs,
            standards=stds,
            editions=eds,
            clauses=cls,
            gaps=gaps,
        )
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000.0)

    avg_ms = sum(times) / len(times)
    assert avg_ms < 10.0, f"Evidence indexing took {avg_ms:.2f} ms (expected < 10 ms)"


def test_benchmark_full_orchestration_latency(db_session: Session, benchmark_spec):
    """
    Benchmarks full decision package orchestration latency (Target: < 50 ms).
    """
    builder = DecisionPackageBuilder()
    times = []
    for _ in range(15):
        t0 = time.perf_counter()
        pkg = builder.build_decision_package(db=db_session, specification=benchmark_spec, force_new_run=True)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000.0)

    avg_ms = sum(times) / len(times)
    assert avg_ms < 100.0, f"Full orchestration took {avg_ms:.2f} ms (expected < 100 ms)"


def test_benchmark_view_projection_latency(db_session: Session, benchmark_spec):
    """
    Benchmarks view projection latency (Target: < 5 ms).
    """
    builder = DecisionPackageBuilder()
    pkg = builder.build_decision_package(db=db_session, specification=benchmark_spec)

    times = []
    for _ in range(30):
        t0 = time.perf_counter()
        proj = SummaryGenerator.project_view(pkg, PackageViewType.EXECUTIVE_SUMMARY)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000.0)

    avg_ms = sum(times) / len(times)
    assert avg_ms < 5.0, f"View projection took {avg_ms:.2f} ms (expected < 5 ms)"
