from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.candidate_intelligence import UnifiedProfileResponse
from app.services.unified_profile_service import build_unified_candidate_profile


router = APIRouter(
    prefix="/candidate-intelligence",
    tags=["Candidate Intelligence"]
)


@router.get(
    "/unified-profile",
    response_model=UnifiedProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Unified Candidate Profile and Skill Intelligence",
    description="Aggregates candidate intelligence across basic profile, candidate profile, resumes, GitHub, LinkedIn, LeetCode, HackerRank, and certifications."
)
def get_unified_candidate_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UnifiedProfileResponse:
    """
    Get unified profile and multi-source skill intelligence for the currently authenticated user.
    """
    try:
        return build_unified_candidate_profile(db=db, current_user=current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build unified candidate profile: {str(e)}"
        )
