from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

from app.schemas.recommendation import JobRecommendation
from app.services.recommendation_service import get_job_recommendations


router = APIRouter(
    prefix="/recommendations",
    tags=["Job Recommendations"]
)


@router.get(
    "/{resume_id}",
    response_model=list[JobRecommendation]
)
def get_recommendations(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_job_recommendations(
        db,
        resume_id,
        current_user
    )