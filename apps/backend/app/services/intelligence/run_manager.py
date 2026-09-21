"""
Procurement Intelligence Run Manager (Phase 8).
Enforces idempotency, versioning, and audit metadata tracking for analysis executions.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.intelligence import ProcurementIntelligenceRun
from app.models.requirement import ProcurementSpecification

ENGINE_VERSION = "8.0.0"
MODEL_VERSION = "deterministic-v1.0"
KNOWLEDGE_BASE_VERSION = "1.0.0"
RETRIEVAL_INDEX_VERSION = "1.0.0"


class RunManager:
    """
    Manages lifecycle, idempotency, and audit metadata for Procurement Intelligence Runs.
    """

    @staticmethod
    def compute_input_hash(specification: ProcurementSpecification, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Computes deterministic SHA-256 hash of specification content and engine configuration.
        """
        content = specification.raw_content or ""
        title = specification.title or ""
        config_str = json.dumps(config or {}, sort_keys=True)
        hash_input = f"{title}:{content}:{ENGINE_VERSION}:{MODEL_VERSION}:{config_str}"
        return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

    @classmethod
    def get_or_create_run(
        cls,
        db: Session,
        specification: ProcurementSpecification,
        config: Optional[Dict[str, Any]] = None,
        force_new: bool = False,
    ) -> Tuple[ProcurementIntelligenceRun, bool]:
        """
        Idempotently returns an existing run if inputs and versions match, or creates a new run.
        Returns: (run, is_created)
        """
        input_hash = cls.compute_input_hash(specification, config)

        if not force_new:
            existing_run = (
                db.query(ProcurementIntelligenceRun)
                .filter(
                    ProcurementIntelligenceRun.specification_id == specification.id,
                    ProcurementIntelligenceRun.input_hash == input_hash,
                    ProcurementIntelligenceRun.status == "COMPLETED",
                )
                .order_by(ProcurementIntelligenceRun.created_at.desc())
                .first()
            )
            if existing_run:
                return existing_run, False

        # Create new run
        now = datetime.now(timezone.utc)
        audit_metadata = {
            "engine_version": ENGINE_VERSION,
            "model_version": MODEL_VERSION,
            "knowledge_base_version": KNOWLEDGE_BASE_VERSION,
            "retrieval_index_version": RETRIEVAL_INDEX_VERSION,
            "analysis_timestamp": now.isoformat(),
            "input_document_hash": hashlib.sha256((specification.raw_content or "").encode("utf-8")).hexdigest(),
            "configuration": config or {},
        }

        new_run = ProcurementIntelligenceRun(
            specification_id=specification.id,
            created_at=now,
            engine_version=ENGINE_VERSION,
            model_version=MODEL_VERSION,
            status="IN_PROGRESS",
            readiness_state="UNRESOLVED_STANDARD_CONTEXT",
            overall_status="INITIALIZING",
            input_hash=input_hash,
            run_metadata=audit_metadata,
        )
        db.add(new_run)
        db.commit()
        db.refresh(new_run)
        return new_run, True

    @staticmethod
    def finalize_run(
        db: Session,
        run: ProcurementIntelligenceRun,
        readiness_state: str,
        requirements_count: int,
        standards_count: int,
        applicable_count: int,
        possible_count: int,
        not_applicable_count: int,
        insufficient_evidence_count: int,
        gap_count: int,
        critical_gap_count: int,
        high_gap_count: int,
        overall_status: str = "ANALYSIS_COMPLETE",
        additional_metadata: Optional[Dict[str, Any]] = None,
    ) -> ProcurementIntelligenceRun:
        """
        Finalizes an intelligence run with summary counts and status.
        """
        run.completed_at = datetime.now(timezone.utc)
        run.status = "COMPLETED"
        run.readiness_state = readiness_state
        run.requirements_count = requirements_count
        run.standards_count = standards_count
        run.applicable_count = applicable_count
        run.possible_count = possible_count
        run.not_applicable_count = not_applicable_count
        run.insufficient_evidence_count = insufficient_evidence_count
        run.gap_count = gap_count
        run.critical_gap_count = critical_gap_count
        run.high_gap_count = high_gap_count
        run.overall_status = overall_status

        if additional_metadata:
            meta = dict(run.run_metadata or {})
            meta.update(additional_metadata)
            run.run_metadata = meta

        db.commit()
        db.refresh(run)
        return run
