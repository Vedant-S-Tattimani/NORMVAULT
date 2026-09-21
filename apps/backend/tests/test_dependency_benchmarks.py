"""
Performance benchmarks and evaluation metrics for Standards Dependency Graph (Phase 5).
Measures traversal latency, cycle suppression, and node/edge scalability.
"""

import time
import pytest
from sqlalchemy.orm import Session
from app.models.standard import IndianStandard
from app.services.dependencies.engine import StandardsComplianceEngine
from tests.test_dependencies import seeded_dependency_db


def test_dependency_graph_traversal_benchmarks(seeded_dependency_db: Session):
    """
    Evaluates traversal latency and scalability across depth 1, 2, and 3.
    Target: < 50 ms mean traversal latency; 100% cycle suppression.
    """
    std = seeded_dependency_db.query(IndianStandard).filter_by(standard_number="IS 101").first()
    assert std is not None

    engine = StandardsComplianceEngine()

    latencies = {}
    graph_sizes = {}

    for depth in [1, 2, 3]:
        start = time.perf_counter()
        graph = engine.get_dependency_graph(seeded_dependency_db, std.id, max_depth=depth)
        duration_ms = (time.perf_counter() - start) * 1000.0

        latencies[depth] = duration_ms
        graph_sizes[depth] = (graph.total_nodes, graph.total_edges)

        # Performance assertion: each traversal completes well under 50ms
        assert duration_ms < 50.0, f"Traversal at depth {depth} took {duration_ms:.2f}ms (threshold: 50ms)"

        # Depth bounding assertion
        max_edge_depth = max((e.depth for e in graph.edges), default=0)
        assert max_edge_depth <= depth

        # Cycle suppression assertion: infinite recursion avoided
        if depth >= 3:
            assert graph.has_cycles is True
            assert len(graph.detected_cycles) > 0

    print(f"\n[BENCHMARK] Depth 1: {latencies[1]:.2f}ms | Nodes: {graph_sizes[1][0]}, Edges: {graph_sizes[1][1]}")
    print(f"[BENCHMARK] Depth 2: {latencies[2]:.2f}ms | Nodes: {graph_sizes[2][0]}, Edges: {graph_sizes[2][1]}")
    print(f"[BENCHMARK] Depth 3: {latencies[3]:.2f}ms | Nodes: {graph_sizes[3][0]}, Edges: {graph_sizes[3][1]}")
