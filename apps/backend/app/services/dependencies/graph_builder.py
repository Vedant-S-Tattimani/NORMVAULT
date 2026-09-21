"""
Directed Standards Dependency Graph Builder.
Handles multi-hop traversal, cycle detection, depth limits, and direct vs transitive separation.
"""

from typing import Dict, List, Set, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.standard import IndianStandard, StandardStatus
from app.models.reference import NormativeReference, ReferenceType, ReferenceSemantics, ProcurementImpact
from app.models.clause import Clause
from app.schemas.dependency import (
    DependencyNode,
    DependencyEdge,
    StandardsDependencyGraph,
)
from app.services.dependencies.compliance_classifier import ComplianceClassifier


class StandardsGraphBuilder:
    """
    Constructs a directed dependency graph starting from a root IndianStandard.
    Enforces depth bounding, cycle detection, and clause-level evidence resolution.
    """

    def __init__(self, max_depth: int = 3):
        self.max_depth = max(1, min(5, max_depth))

    def build_graph(self, db: Session, root_standard_id: int) -> StandardsDependencyGraph:
        """Builds a complete StandardsDependencyGraph for the given root standard ID."""
        root_std = db.query(IndianStandard).filter(IndianStandard.id == root_standard_id).first()
        if not root_std:
            raise ValueError(f"Standard with ID {root_standard_id} not found.")

        nodes_map: Dict[str, DependencyNode] = {}
        edges: List[DependencyEdge] = []
        direct_refs: List[DependencyEdge] = []
        transitive_deps: List[DependencyEdge] = []
        detected_cycles: List[List[str]] = []
        edge_signatures: Set[Tuple[str, str, str, int]] = set()

        # Add root node (depth 0)
        root_node = DependencyNode(
            standard_id=root_std.id,
            standard_number=root_std.standard_number,
            title=root_std.title,
            status=root_std.status.value if hasattr(root_std.status, "value") else str(root_std.status),
            is_mandatory_qco=root_std.is_mandatory_qco,
            depth=0,
            edition_year=root_std.editions[0].year if root_std.editions else None,
            provenance_id=root_std.provenance_id,
        )
        nodes_map[root_std.standard_number] = root_node

        # DFS traversal queue/stack with path tracking for cycles
        # State: (current_standard_id, current_standard_number, current_depth, current_path)
        visited_depth: Dict[str, int] = {root_std.standard_number: 0}

        def traverse(
            current_id: int,
            current_number: str,
            depth: int,
            path: List[str],
        ):
            if depth > self.max_depth:
                return

            outgoing_refs = (
                db.query(NormativeReference)
                .filter(NormativeReference.source_standard_id == current_id)
                .all()
            )

            for ref in outgoing_refs:
                target_number = ref.target_standard_number.strip()
                target_std = None

                if ref.target_standard_id:
                    target_std = db.query(IndianStandard).filter(IndianStandard.id == ref.target_standard_id).first()
                elif target_number:
                    target_std = db.query(IndianStandard).filter(IndianStandard.standard_number == target_number).first()

                # Fetch clause content if available
                clause_content = None
                if ref.source_clause_id:
                    cl = db.query(Clause).filter(Clause.id == ref.source_clause_id).first()
                    if cl:
                        clause_content = cl.content
                elif ref.referencing_clause and target_std:
                    # Try to locate by clause number
                    cl = (
                        db.query(Clause)
                        .join(Clause.edition)
                        .filter(
                            Clause.edition.has(standard_id=current_id),
                            Clause.clause_number == ref.referencing_clause,
                        )
                        .first()
                    )
                    if cl:
                        clause_content = cl.content

                # Resolve semantics and impact
                semantics = ComplianceClassifier.classify_semantics(
                    clause_content=clause_content,
                    condition_text=ref.condition_text,
                    declared_semantics=ref.reference_semantics,
                )
                impact = ComplianceClassifier.classify_procurement_impact(
                    relationship_type=ref.relationship_type,
                    semantics=semantics,
                    condition_text=ref.condition_text,
                    declared_impact=ref.procurement_impact,
                )

                # Cycle Detection
                is_cycle = False
                if target_number in path:
                    is_cycle = True
                    cycle_start = path.index(target_number)
                    cycle_subpath = path[cycle_start:] + [target_number]
                    if cycle_subpath not in detected_cycles:
                        detected_cycles.append(cycle_subpath)

                edge_sig = (current_number, target_number, ref.relationship_type.value, depth)
                if edge_sig not in edge_signatures:
                    edge_signatures.add(edge_sig)

                    edge = DependencyEdge(
                        id=ref.id,
                        source_standard_id=current_id,
                        source_standard_number=current_number,
                        target_standard_id=target_std.id if target_std else None,
                        target_standard_number=target_number,
                        relationship_type=ref.relationship_type,
                        reference_semantics=semantics,
                        procurement_impact=impact,
                        referencing_clause=ref.referencing_clause,
                        source_clause_id=ref.source_clause_id,
                        clause_content=clause_content,
                        condition_text=ref.condition_text,
                        triggering_condition=ref.triggering_condition,
                        test_name=ref.test_name,
                        depth=depth,
                        is_cycle=is_cycle,
                        provenance_id=ref.provenance_id,
                    )
                    edges.append(edge)

                    if depth == 1:
                        direct_refs.append(edge)
                    else:
                        transitive_deps.append(edge)

                # Add target node if not already present or if reached at shallower depth
                if target_number not in nodes_map or depth < nodes_map[target_number].depth:
                    node = DependencyNode(
                        standard_id=target_std.id if target_std else None,
                        standard_number=target_number,
                        title=target_std.title if target_std else f"Standard {target_number} (Unindexed)",
                        status=target_std.status.value if target_std and hasattr(target_std.status, "value") else "ACTIVE",
                        is_mandatory_qco=target_std.is_mandatory_qco if target_std else False,
                        depth=depth,
                        edition_year=target_std.editions[0].year if target_std and target_std.editions else None,
                        provenance_id=target_std.provenance_id if target_std else None,
                    )
                    nodes_map[target_number] = node

                # Recurse if not cycle, target exists in DB, and depth < max_depth
                if not is_cycle and target_std and depth < self.max_depth:
                    # If target standard was already visited at equal or shallower depth, avoid re-traversal
                    if target_number not in visited_depth or depth < visited_depth[target_number]:
                        visited_depth[target_number] = depth
                        traverse(
                            current_id=target_std.id,
                            current_number=target_number,
                            depth=depth + 1,
                            path=path + [target_number],
                        )

        # Launch traversal from root
        traverse(
            current_id=root_std.id,
            current_number=root_std.standard_number,
            depth=1,
            path=[root_std.standard_number],
        )

        return StandardsDependencyGraph(
            root_standard_id=root_std.id,
            root_standard_number=root_std.standard_number,
            root_standard_title=root_std.title,
            max_depth_traversed=self.max_depth,
            total_nodes=len(nodes_map),
            total_edges=len(edges),
            has_cycles=len(detected_cycles) > 0,
            detected_cycles=detected_cycles,
            nodes=list(nodes_map.values()),
            edges=edges,
            direct_references=direct_refs,
            transitive_dependencies=transitive_deps,
        )
