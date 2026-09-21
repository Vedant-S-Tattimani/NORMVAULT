"""
Performance and latency benchmarks for Phase 6:
Standard Edition, Amendment & Currentness Intelligence Engine.
"""

import time
from datetime import date
import pytest
from sqlalchemy.orm import Session

from app.models.standard import IndianStandard, StandardEdition, EditionStatus, Amendment, StandardStatus
from app.models.certification import CertificationRequirement, CertificationScheme, CertificationCurrentness
from app.services.currentness import (
    TenderCitationExtractor,
    CurrentnessAnalyzer,
    StandardTimelineBuilder,
)


@pytest.fixture
def seeded_benchmark_db(db_session: Session):
    """Seeds standards and amendments for latency benchmarks."""
    std = IndianStandard(
        standard_number="IS 12615",
        title="Line Operated Three-Phase A.C. Motors (IE Code)",
        status=StandardStatus.ACTIVE,
        is_mandatory_qco=True,
    )
    db_session.add(std)
    db_session.flush()

    ed = StandardEdition(
        standard_id=std.id,
        edition_number=1,
        year=2018,
        status=EditionStatus.CURRENT,
        is_current=True,
    )
    db_session.add(ed)
    db_session.flush()

    amd1 = Amendment(
        standard_id=std.id,
        edition_id=ed.id,
        amendment_number=1,
        title="Amendment 1: Efficiency Tolerances",
        issue_date=date(2019, 4, 15),
        summary="Revision of efficiency test tolerance values in Clause 7.1",
        affected_clauses="Clause 7.1",
        is_effective=True,
    )
    amd2 = Amendment(
        standard_id=std.id,
        edition_id=ed.id,
        amendment_number=2,
        title="Amendment 2: Terminal Box Marking",
        issue_date=date(2021, 9, 20),
        summary="Update to terminal box marking",
        affected_clauses="Clause 8.3",
        is_effective=True,
    )
    db_session.add(amd1)
    db_session.add(amd2)

    cert = CertificationRequirement(
        standard_id=std.id,
        edition_id=ed.id,
        edition_year=2018,
        scheme=CertificationScheme.ISI_MARK_SCHEME_I,
        is_mandatory_qco=True,
        qco_order_number="S.O. 2618(E)",
        notifying_ministry="Ministry of Heavy Industries",
        notification_date=date(2020, 6, 12),
        currentness_status=CertificationCurrentness.VERIFIED_CURRENT,
    )
    db_session.add(cert)
    db_session.commit()
    return db_session


def test_citation_extraction_latency_benchmark():
    extractor = TenderCitationExtractor()
    sample_text = (
        "Item 1: 15 kW, 415 V, 50 Hz, 3-phase squirrel cage induction motor conforming to "
        "IS 12615:2018 with Amendment 1 for line operated continuous duty S1. Degree of protection "
        "shall be IP55 as per IS/IEC 60034-5:2020. Dimensions must comply with IS 1231:1974. "
        "Installation practices shall adhere to IS 900:1990."
    )

    # Warmup
    for _ in range(5):
        extractor.extract_citations(sample_text)

    # Measure
    start_time = time.perf_counter()
    iterations = 100
    for _ in range(iterations):
        citations = extractor.extract_citations(sample_text)
        extractor.detect_conflicts(citations)
    duration_ms = ((time.perf_counter() - start_time) / iterations) * 1000

    print(f"\n[Benchmark] Mean Citation Extraction Latency: {duration_ms:.3f} ms (Target <= 10.0 ms)")
    assert duration_ms <= 10.0, f"Citation extraction latency exceeded target: {duration_ms:.2f} ms"


def test_currentness_evaluation_latency_benchmark(seeded_benchmark_db: Session):
    analyzer = CurrentnessAnalyzer()
    std = seeded_benchmark_db.query(IndianStandard).filter_by(standard_number="IS 12615").first()
    assert std is not None

    sample_text = "Supply of 15 kW motor conforming to IS 12615:2018 with IE3 rating."

    # Warmup
    for _ in range(3):
        analyzer.evaluate_requirement_currentness(seeded_benchmark_db, std, sample_text)

    # Measure
    start_time = time.perf_counter()
    iterations = 50
    for _ in range(iterations):
        result = analyzer.evaluate_requirement_currentness(seeded_benchmark_db, std, sample_text)
    duration_ms = ((time.perf_counter() - start_time) / iterations) * 1000

    print(f"\n[Benchmark] Mean Currentness Evaluation Latency: {duration_ms:.3f} ms (Target <= 20.0 ms)")
    assert duration_ms <= 20.0, f"Currentness evaluation latency exceeded target: {duration_ms:.2f} ms"
    assert result.status == "CURRENT"


def test_timeline_construction_latency_benchmark(seeded_benchmark_db: Session):
    builder = StandardTimelineBuilder()
    std = seeded_benchmark_db.query(IndianStandard).filter_by(standard_number="IS 12615").first()
    assert std is not None

    # Warmup
    for _ in range(3):
        builder.build_history(seeded_benchmark_db, std.id)

    # Measure
    start_time = time.perf_counter()
    iterations = 50
    for _ in range(iterations):
        history = builder.build_history(seeded_benchmark_db, std.id)
    duration_ms = ((time.perf_counter() - start_time) / iterations) * 1000

    print(f"\n[Benchmark] Mean Timeline Construction Latency: {duration_ms:.3f} ms (Target <= 30.0 ms)")
    assert duration_ms <= 30.0, f"Timeline construction latency exceeded target: {duration_ms:.2f} ms"
    assert history is not None
    assert len(history.timeline) >= 3
