"""
Performance and Latency Benchmarks for Phase 7:
Procurement Specification Gap & Compliance Readiness Engine.
Asserts that all gap analysis algorithms operate well within sub-second / sub-25ms budgets.
"""

import time
from datetime import date
from typing import Optional
import pytest
from sqlalchemy.orm import Session

from app.models.gap import (
    GapType,
    GapSeverity,
    ReadinessState,
    CompletenessCategory,
    CoverageStatus,
    SpecificationGap,
)
from app.models.document import Document
from app.models.requirement import ProcurementSpecification, Requirement, TechnicalParameter
from app.models.standard import IndianStandard, StandardEdition, StandardStatus, EditionStatus, Amendment
from app.models.certification import CertificationRequirement, CertificationScheme, CertificationCurrentness
from app.services.gaps import (
    AmbiguityDetector,
    ConflictDetector,
    CompletenessAnalyzer,
    DependencyGapAnalyzer,
    TraceabilityBuilder,
    ProcurementReadinessService,
)


def make_param(name: str, val: str, unit: Optional[str] = None, requirement_id: Optional[int] = None) -> TechnicalParameter:
    kwargs = {
        "name": name,
        "original_value": val,
        "normalized_value": val,
        "target_value": val,
        "unit": unit,
    }
    if requirement_id is not None:
        kwargs["requirement_id"] = requirement_id
    return TechnicalParameter(**kwargs)


@pytest.fixture
def benchmark_spec():
    """Builds a realistic 8-clause industrial motor specification for benchmarking."""
    spec = ProcurementSpecification(
        id=9999,
        title="Industrial Motor Tender - Benchmark",
        raw_content="Tender for 30 kW motor.",
    )
    clauses = [
        "Supply of 30 kW, 415 V +/- 10%, 50 Hz +/- 5%, 4 Pole (1500 RPM) squirrel cage induction motor.",
        "Motor shall conform to IS 12615:2018 with IE3 efficiency class and continuous duty S1.",
        "Degree of protection shall be IP55 with Class F insulation and Class B temperature rise limits.",
        "Mounting arrangement shall be B3 foot mounted conforming to IS 1231.",
        "Loss determination and testing shall be carried out per IS 15999 (Part 1) with tolerance limits as per IS/IEC 60034-1.",
        "Earthing terminals shall be provided on frame and terminal box per IS 3043.",
        "Installation shall follow IS 900 code of practice.",
        "Motor shall bear the Standard Mark (ISI mark) under a valid BIS License as per mandatory Electrical Motors QCO.",
    ]

    reqs = []
    for i, text in enumerate(clauses):
        r = Requirement(id=9000 + i, specification_id=9999, extracted_text=text)
        reqs.append(r)

    reqs[0].parameters = [
        make_param("rated_power", "30", "kW"),
        make_param("voltage", "415", "V"),
        make_param("frequency", "50", "Hz"),
        make_param("speed", "1500", "RPM"),
        make_param("efficiency_class", "IE3"),
        make_param("duty", "S1"),
        make_param("enclosure_ip", "IP55"),
        make_param("insulation", "Class F"),
        make_param("mounting", "B3"),
    ]
    spec.requirements = reqs
    return spec


@pytest.fixture
def benchmark_standard():
    std = IndianStandard(id=12615, standard_number="IS 12615", title="IE Motors", is_mandatory_qco=True)
    ed = StandardEdition(id=1, standard_id=12615, year=2018, status=EditionStatus.CURRENT)
    return std, ed


def test_benchmark_ambiguity_detection_latency():
    detector = AmbiguityDetector()
    text = (
        "The motor shall be suitable for harsh environments and severe operating conditions. "
        "Supplier shall provide high quality, heavy duty motors with high efficiency and robust workmanship."
    )

    latencies = []
    for _ in range(50):
        start = time.perf_counter()
        gaps = detector.detect_ambiguities(text=text, specification_id=1, parameters_count=0)
        dur = (time.perf_counter() - start) * 1000.0
        latencies.append(dur)

    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)]
    # Ambiguity detection must complete well within 5ms (typically < 0.2ms)
    assert p95 < 5.0, f"Ambiguity detection p95 latency {p95:.2f}ms exceeds 5ms limit"


def test_benchmark_conflict_detection_latency(benchmark_spec):
    detector = ConflictDetector()

    latencies = []
    for _ in range(50):
        start = time.perf_counter()
        p_gaps = detector.detect_parameter_conflicts(
            specification_id=benchmark_spec.id,
            requirements=benchmark_spec.requirements,
        )
        e_gaps = detector.detect_edition_inconsistencies(
            specification_id=benchmark_spec.id,
            requirements=benchmark_spec.requirements,
        )
        dur = (time.perf_counter() - start) * 1000.0
        latencies.append(dur)

    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)]
    # Conflict detection must complete within 10ms (typically < 0.5ms)
    assert p95 < 10.0, f"Conflict detection p95 latency {p95:.2f}ms exceeds 10ms limit"


def test_benchmark_completeness_analysis_latency(benchmark_spec, benchmark_standard):
    std, ed = benchmark_standard
    analyzer = CompletenessAnalyzer()

    latencies = []
    for _ in range(50):
        start = time.perf_counter()
        gaps, metrics = analyzer.analyze_completeness(
            specification_id=benchmark_spec.id,
            requirements=benchmark_spec.requirements,
            applicable_standard=std,
            applicable_edition=ed,
        )
        dur = (time.perf_counter() - start) * 1000.0
        latencies.append(dur)

    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)]
    assert p95 < 5.0, f"Completeness analysis p95 latency {p95:.2f}ms exceeds 5ms limit"


def test_benchmark_coverage_matrix_latency(benchmark_spec, benchmark_standard):
    std, ed = benchmark_standard
    builder = TraceabilityBuilder()

    latencies = []
    for _ in range(50):
        start = time.perf_counter()
        matrix = builder.build_coverage_matrix(
            specification_id=benchmark_spec.id,
            requirements=benchmark_spec.requirements,
            gaps=[],
            applicable_standard=std,
            applicable_edition=ed,
        )
        dur = (time.perf_counter() - start) * 1000.0
        latencies.append(dur)

    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)]
    assert p95 < 10.0, f"Coverage matrix p95 latency {p95:.2f}ms exceeds 10ms limit"


def test_benchmark_full_readiness_assessment_latency(benchmark_spec, benchmark_standard):
    std, ed = benchmark_standard
    service = ProcurementReadinessService()

    latencies = []
    for _ in range(50):
        start = time.perf_counter()
        res = service.evaluate_specification(
            specification=benchmark_spec,
            applicable_standard=std,
            applicable_edition=ed,
            db=None,
        )
        dur = (time.perf_counter() - start) * 1000.0
        latencies.append(dur)

    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)]
    # Full readiness assessment across 8 clauses must complete within 25ms (typically ~1-3ms)
    assert p95 < 25.0, f"Full readiness assessment p95 latency {p95:.2f}ms exceeds 25ms budget"
