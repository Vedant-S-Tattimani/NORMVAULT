"""
Standards recommendation endpoints.
Scheduled for Phase 3 (Retrieval & Ranking).
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.post(
    "/generate",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Generate Standard Recommendations",
    description="Generates evidence-backed Indian Standard recommendations for specifications. Scheduled for Phase 3.",
)
def generate_recommendations() -> dict:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Semantic retrieval and recommendation pipeline will be activated in Phase 3. No fake recommendations are served.",
    )
