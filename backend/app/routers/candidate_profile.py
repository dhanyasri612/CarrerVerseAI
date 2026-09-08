from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.candidate_profile import CandidateProfileResponse
from app.services.candidate_profile_service import aggregate_candidate_profile


router = APIRouter(
    prefix="/candidate-profile",
    tags=["Candidate Profile"]
)


@router.post(
    "/aggregate/{resume_id}",
    response_model=CandidateProfileResponse
)
def create_candidate_profile(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return aggregate_candidate_profile(
        db,
        resume_id,
        current_user
    )