from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

from app.schemas.skill_gap import SkillGapResponse
from app.services.skill_gap_service import analyze_skill_gap


router = APIRouter(
    prefix="/skill-gap",
    tags=["Skill Gap Analysis"]
)


@router.get(
    "/{resume_id}/{job_id}",
    response_model=SkillGapResponse
)
def get_skill_gap(
    resume_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return analyze_skill_gap(
        db,
        resume_id,
        job_id,
        current_user
    )