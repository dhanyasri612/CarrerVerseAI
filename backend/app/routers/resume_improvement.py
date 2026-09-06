from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.resume_improvement import ResumeImprovementResponse
from app.services.resume_improvement_service import analyze_resume


router = APIRouter(
    prefix="/resume-improvement",
    tags=["Resume Improvement"]
)


@router.get(
    "/{resume_id}/{job_id}",
    response_model=ResumeImprovementResponse
)
def get_resume_improvement(
    resume_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return analyze_resume(
        db,
        resume_id,
        job_id,
        current_user
    )