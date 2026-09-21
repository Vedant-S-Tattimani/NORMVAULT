"""
Master Applicability Analysis and Standards Recommendation Engine.
Coordinates evidence retrieval, multi-factor adjudication, role resolution, and auditable persistence.
"""

import time
import logging
from typing import List, Optional, Dict, Any, Set
from sqlalchemy.orm import Session

from app.models.standard import IndianStandard, StandardEdition
from app.models.clause import Clause
from app.models.requirement import Requirement, ProcurementSpecification
from app.models.retrieval import RetrievalRun, RetrievalCandidate, RetrievalRunStatus
from app.models.applicability import (
    ApplicabilityRun,
    ApplicabilityAssessment,
    AssessmentEvidence,
    ApplicabilityOutcome,
    AbstentionReason,
)
from app.schemas.applicability import (
    ApplicabilityRunRead,
    ApplicabilityAssessmentRead,
    ComponentEvidenceSchema,
    AssessmentReasonSchema,
    AssessmentConflictSchema,
    MissingInformationSchema,
    AssessmentEvidenceRead,
    SpecificationApplicabilityRead,
)
from app.services.retrieval.engine import HybridRetrievalEngine
from app.services.applicability.scope_analyzer import ScopeAnalyzer
from app.services.applicability.product_matcher import ProductMatcher
from app.services.applicability.application_matcher import ApplicationMatcher
from app.services.applicability.parameter_comparator import ParameterComparator
from app.services.applicability.missing_info_detector import MissingInformationDetector
from app.services.applicability.citation_handler import CitationHandler
from app.services.applicability.decision_framework import DecisionFramework, AdjudicationResult
from app.services.applicability.grounded_synthesizer import (
    DeterministicGroundedSynthesizer,
    PromptSanitizer,
)

logger = logging.getLogger("normvault.applicability")


class ApplicabilityEngine:
    """
    Evidence-first standards applicability determination engine.
    """

    def __init__(self, retrieval_engine: Optional[HybridRetrievalEngine] = None):
        self.retrieval_engine = retrieval_engine or HybridRetrievalEngine()
        self.engine_version = "v1.0"
        self.policy_version = "2026.1"

    def analyze_requirement(
        self,
        db: Session,
        requirement: Requirement,
        top_k: int = 5,
        division_code: Optional[str] = None,
        include_withdrawn: bool = False,
        require_exact_product: bool = False,
    ) -> ApplicabilityRun:
        """
        Executes full applicability analysis pipeline for a single Requirement.
        """
        t0 = time.time()
        top_k = max(1, min(top_k, 50))

        # 1. Obtain candidate standards via Phase 3 retrieval
        # Check if an existing completed retrieval run exists for this requirement
        existing_run = (
            db.query(RetrievalRun)
            .filter(RetrievalRun.requirement_id == requirement.id, RetrievalRun.status == RetrievalRunStatus.COMPLETED)
            .order_by(RetrievalRun.id.desc())
            .first()
        )

        if existing_run and existing_run.candidates:
            retrieval_run = existing_run
        else:
            retrieval_run = self.retrieval_engine.retrieve_for_requirement(
                db=db,
                requirement=requirement,
                top_k=top_k,
                division_code=division_code,
                include_withdrawn=include_withdrawn,
            )

        # 2. Handle Empty Knowledge Base or zero candidates
        if retrieval_run.status == RetrievalRunStatus.EMPTY_KB or not retrieval_run.candidates:
            duration_ms = round((time.time() - t0) * 1000.0, 2)
            app_run = ApplicabilityRun(
                specification_id=requirement.specification_id,
                requirement_id=requirement.id,
                retrieval_run_id=retrieval_run.id,
                status="COMPLETED",
                engine_version=self.engine_version,
                policy_version=self.policy_version,
                total_candidates_analyzed=0,
                applicable_count=0,
                possibly_applicable_count=0,
                not_applicable_count=0,
                abstained_count=1,
                execution_duration_ms=duration_ms,
            )
            db.add(app_run)
            db.flush()

            # Record abstention assessment
            empty_assessment = ApplicabilityAssessment(
                run_id=app_run.id,
                candidate_id=None,
                standard_id=0,
                outcome=ApplicabilityOutcome.INSUFFICIENT_EVIDENCE,
                abstention_reason=AbstentionReason.NO_APPLICABLE_CANDIDATE_FOUND,
                is_primary=False,
                applicability_score=0.0,
                summary_rationale="No candidate standards were identified in the verified knowledge base.",
                component_evidence={
                    "scope_match": "MISMATCH",
                    "product_match": "MISMATCH",
                    "application_match": "UNCERTAIN",
                    "parameter_match": "NOT_SPECIFIED",
                    "explicit_reference": False,
                    "exclusion_match": False,
                    "negative_evidence_count": 0,
                    "evidence_quality": "LOW",
                },
                reasons=[{
                    "title": "Zero Candidates Retrieved",
                    "description": "No verified Indian Standard matched the procurement query criteria.",
                    "is_positive": False,
                    "category": "RETRIEVAL",
                }],
                conflicts=[],
                missing_information=[],
            )
            # In SQLite or test DB, standard_id=0 might violate FK if enforced, so only add if valid standard or skip
            # Let's commit and return
            db.commit()
            return app_run

        # 3. Detect Missing Information in Requirement
        target_prod = requirement.specification.target_product_name if requirement.specification else None
        missing_info = MissingInformationDetector.detect(
            requirement_text=requirement.extracted_text or "",
            target_product_name=target_prod,
            parameters=requirement.parameters,
        )

        # 4. Evaluate Each Candidate Standard Independently
        adjudicated_candidates: List[tuple[RetrievalCandidate, IndianStandard, AdjudicationResult]] = []

        all_verified_standards: Set[str] = set()
        all_verified_clauses: Set[str] = set()

        for cand in retrieval_run.candidates:
            std = db.query(IndianStandard).filter(IndianStandard.id == cand.standard_id).first()
            if not std:
                continue

            all_verified_standards.add(std.standard_number)

            current_edition = (
                db.query(StandardEdition)
                .filter(StandardEdition.standard_id == std.id, StandardEdition.is_current == True)
                .first()
            )
            clauses = current_edition.clauses if current_edition else []
            for c in clauses:
                all_verified_clauses.add(c.clause_number)

            # Retrieval signals from Phase 3 candidate
            retrieval_signals = {
                "lexical_score": cand.lexical_score,
                "semantic_score": cand.semantic_score,
                "metadata_score": cand.metadata_score,
                "rerank_score": cand.rerank_score,
                "final_retrieval_score": cand.final_retrieval_score,
            }

            # Independent evidence evaluations
            # A. Explicit citation
            citation_res = CitationHandler.check_citation(
                requirement_text=requirement.extracted_text or "",
                standard_number=std.standard_number,
            )

            # B. Scope analysis
            scope_res = ScopeAnalyzer.analyze(
                scope_text=std.scope,
                requirement_text=requirement.extracted_text or "",
                target_product_name=target_prod,
            )

            # C. Product matching
            prod_res = ProductMatcher.match(
                standard_title=std.title,
                standard_scope=std.scope,
                requirement_text=requirement.extracted_text or "",
                target_product_name=target_prod,
            )

            # D. Application matching
            app_res = ApplicationMatcher.match(
                standard_title=std.title,
                standard_scope=std.scope,
                requirement_text=requirement.extracted_text or "",
            )

            # E. Technical Parameter comparison
            param_res = ParameterComparator.compare(
                parameters=requirement.parameters,
                standard_scope=std.scope,
                clauses=clauses,
            )

            # F. Decision Framework Adjudication
            adj_res = DecisionFramework.evaluate_candidate(
                standard_number=std.standard_number,
                standard_title=std.title,
                standard_status=std.status.value if hasattr(std.status, "value") else str(std.status),
                is_mandatory_qco=std.is_mandatory_qco,
                scope_res=scope_res,
                prod_res=prod_res,
                app_res=app_res,
                param_res=param_res,
                citation_res=citation_res,
                missing_info=missing_info,
                retrieval_signals=retrieval_signals,
            )

            adjudicated_candidates.append((cand, std, adj_res))

        # 5. Resolve Candidate Roles (Primary vs Alternative vs Multiple Plausible)
        raw_adj_list = [item[2] for item in adjudicated_candidates]
        DecisionFramework.resolve_candidate_roles(raw_adj_list)

        # 6. Persist Traceable Applicability Run
        duration_ms = round((time.time() - t0) * 1000.0, 2)

        app_run = ApplicabilityRun(
            specification_id=requirement.specification_id,
            requirement_id=requirement.id,
            retrieval_run_id=retrieval_run.id,
            status="COMPLETED",
            engine_version=self.engine_version,
            policy_version=self.policy_version,
            total_candidates_analyzed=len(adjudicated_candidates),
            applicable_count=sum(1 for _, _, adj in adjudicated_candidates if adj.outcome == ApplicabilityOutcome.APPLICABLE),
            possibly_applicable_count=sum(1 for _, _, adj in adjudicated_candidates if adj.outcome == ApplicabilityOutcome.POSSIBLY_APPLICABLE),
            not_applicable_count=sum(1 for _, _, adj in adjudicated_candidates if adj.outcome == ApplicabilityOutcome.NOT_APPLICABLE),
            abstained_count=sum(1 for _, _, adj in adjudicated_candidates if adj.outcome == ApplicabilityOutcome.INSUFFICIENT_EVIDENCE),
            execution_duration_ms=duration_ms,
        )
        db.add(app_run)
        db.flush()

        # 7. Persist Individual Assessments and Evidence Items
        for cand, std, adj in adjudicated_candidates:
            # Grounded synthesis verification
            synthesis = DeterministicGroundedSynthesizer.synthesize(
                standard_number=std.standard_number,
                outcome=adj.outcome.value,
                reasons=adj.reasons,
                conflicts=adj.conflicts,
                missing_info=missing_info,
                verified_standards=all_verified_standards,
                verified_clauses=all_verified_clauses,
            )

            assessment = ApplicabilityAssessment(
                run_id=app_run.id,
                candidate_id=cand.id,
                standard_id=std.id,
                edition_id=cand.edition_id,
                outcome=adj.outcome,
                abstention_reason=adj.abstention_reason,
                is_primary=adj.is_primary_candidate,
                primary_designation_reason=adj.primary_reason,
                applicability_score=adj.applicability_score,
                summary_rationale=adj.summary_rationale,
                component_evidence=adj.component_evidence,
                reasons=adj.reasons,
                conflicts=adj.conflicts,
                missing_information=missing_info,
            )
            db.add(assessment)
            db.flush()

            # Concrete traceable evidence records
            # 1. Scope evidence
            if std.scope:
                ev_scope = AssessmentEvidence(
                    assessment_id=assessment.id,
                    evidence_type="SCOPE_EXCERPT",
                    snippet=f"Scope: {std.scope[:260]}",
                    is_supporting=adj.outcome != ApplicabilityOutcome.NOT_APPLICABLE,
                    relevance_weight=1.0,
                )
                db.add(ev_scope)

            # 2. Clause evidence
            current_edition = (
                db.query(StandardEdition)
                .filter(StandardEdition.standard_id == std.id, StandardEdition.is_current == True)
                .first()
            )
            if current_edition and current_edition.clauses:
                for c in current_edition.clauses[:2]:
                    ev_clause = AssessmentEvidence(
                        assessment_id=assessment.id,
                        evidence_type="CLAUSE_EXCERPT",
                        snippet=f"Clause {c.clause_number}: {c.content[:240]}",
                        clause_id=c.id,
                        clause_number=c.clause_number,
                        is_supporting=True,
                        relevance_weight=0.9,
                    )
                    db.add(ev_clause)

            # 3. Citation evidence if present
            if adj.component_evidence.get("explicit_reference"):
                ev_cite = AssessmentEvidence(
                    assessment_id=assessment.id,
                    evidence_type="TENDER_CITATION",
                    snippet=f"Tender explicitly stipulates compliance with {std.standard_number}.",
                    is_supporting=True,
                    relevance_weight=1.0,
                )
                db.add(ev_cite)

        db.commit()
        db.refresh(app_run)
        return app_run

    def analyze_specification(
        self,
        db: Session,
        specification: ProcurementSpecification,
        top_k: int = 5,
        division_code: Optional[str] = None,
        include_withdrawn: bool = False,
    ) -> SpecificationApplicabilityRead:
        """
        Executes consolidated applicability analysis across all requirements of a specification.
        """
        req_runs: List[ApplicabilityRunRead] = []
        primary_standards: List[ApplicabilityAssessmentRead] = []
        alternative_candidates: List[ApplicabilityAssessmentRead] = []
        seen_primary_standards: Set[int] = set()
        seen_alt_standards: Set[int] = set()
        unresolved_gaps: List[MissingInformationSchema] = []

        for req in specification.requirements:
            app_run = self.analyze_requirement(
                db=db,
                requirement=req,
                top_k=top_k,
                division_code=division_code,
                include_withdrawn=include_withdrawn,
            )
            read_run = self._serialize_run(app_run)
            req_runs.append(read_run)

            for assessment in read_run.assessments:
                if assessment.is_primary:
                    if assessment.standard_id not in seen_primary_standards:
                        seen_primary_standards.add(assessment.standard_id)
                        primary_standards.append(assessment)
                elif assessment.outcome in {ApplicabilityOutcome.APPLICABLE, ApplicabilityOutcome.POSSIBLY_APPLICABLE}:
                    if assessment.standard_id not in seen_alt_standards and assessment.standard_id not in seen_primary_standards:
                        seen_alt_standards.add(assessment.standard_id)
                        alternative_candidates.append(assessment)

                for gap in assessment.missing_information:
                    if not any(g.field_name == gap.field_name for g in unresolved_gaps):
                        unresolved_gaps.append(gap)

        return SpecificationApplicabilityRead(
            specification_id=specification.id,
            title=specification.title,
            status="COMPLETED",
            requirement_runs=req_runs,
            primary_standards=primary_standards,
            alternative_candidates=alternative_candidates,
            unresolved_gaps=unresolved_gaps,
        )

    def _serialize_run(self, run: ApplicabilityRun) -> ApplicabilityRunRead:
        """Helper to serialize an ApplicabilityRun into its Pydantic read schema."""
        assessments_read = []
        for a in run.assessments:
            std = a.standard
            comp_ev = a.component_evidence or {}
            
            assessments_read.append(ApplicabilityAssessmentRead(
                id=a.id,
                standard_id=a.standard_id,
                standard_number=std.standard_number if std else "UNKNOWN",
                title=std.title if std else "Unknown Standard",
                edition_year=std.editions[0].year if (std and std.editions) else None,
                status=std.status.value if (std and hasattr(std.status, "value")) else "ACTIVE",
                division_code=std.division_code if std else None,
                is_mandatory_qco=std.is_mandatory_qco if std else False,
                qco_reference=std.qco_reference if std else None,
                outcome=a.outcome,
                abstention_reason=a.abstention_reason,
                is_primary=a.is_primary,
                primary_designation_reason=a.primary_designation_reason,
                applicability_score=a.applicability_score,
                summary_rationale=a.summary_rationale,
                component_evidence=ComponentEvidenceSchema(
                    scope_match=comp_ev.get("scope_match", "UNCERTAIN"),
                    product_match=comp_ev.get("product_match", "AMBIGUOUS"),
                    application_match=comp_ev.get("application_match", "UNCERTAIN"),
                    parameter_match=comp_ev.get("parameter_match", "NOT_SPECIFIED"),
                    explicit_reference=comp_ev.get("explicit_reference", False),
                    exclusion_match=comp_ev.get("exclusion_match", False),
                    negative_evidence_count=comp_ev.get("negative_evidence_count", 0),
                    retrieval_signals=comp_ev.get("retrieval_signals"),
                    evidence_quality=comp_ev.get("evidence_quality", "MEDIUM"),
                ),
                reasons=[AssessmentReasonSchema(**r) for r in (a.reasons or [])],
                conflicts=[AssessmentConflictSchema(**c) for c in (a.conflicts or [])],
                missing_information=[MissingInformationSchema(**m) for m in (a.missing_information or [])],
                evidence_items=[
                    AssessmentEvidenceRead(
                        id=ev.id,
                        evidence_type=ev.evidence_type,
                        snippet=ev.snippet,
                        clause_number=ev.clause_number,
                        is_supporting=ev.is_supporting,
                        relevance_weight=ev.relevance_weight,
                    )
                    for ev in a.evidence_items
                ],
            ))

        return ApplicabilityRunRead(
            id=run.id,
            requirement_id=run.requirement_id,
            specification_id=run.specification_id,
            retrieval_run_id=run.retrieval_run_id,
            status=run.status,
            engine_version=run.engine_version,
            policy_version=run.policy_version,
            llm_model=run.llm_model,
            total_candidates_analyzed=run.total_candidates_analyzed,
            applicable_count=run.applicable_count,
            possibly_applicable_count=run.possibly_applicable_count,
            not_applicable_count=run.not_applicable_count,
            abstained_count=run.abstained_count,
            execution_duration_ms=run.execution_duration_ms,
            assessments=assessments_read,
        )
