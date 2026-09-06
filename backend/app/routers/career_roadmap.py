from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.career_roadmap import CareerRoadmapResponse
from app.services.career_roadmap_service import analyze_career_roadmap


router = APIRouter(
    prefix="/career-roadmap",
    tags=["Career Roadmap"]
)


@router.get(
    "/{resume_id}/{job_id}",
    response_model=CareerRoadmapResponse
)
def get_career_roadmap(
    resume_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return analyze_career_roadmap(
        db,
        resume_id,
        job_id,
        current_user
    )