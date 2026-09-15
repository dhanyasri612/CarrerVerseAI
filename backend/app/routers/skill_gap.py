from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.skill_gap import SkillGapResponse, UnifiedSkillGapResponse
from app.services.skill_gap_service import analyze_skill_gap, analyze_unified_skill_gap


router = APIRouter(
    prefix="/skill-gap",
    tags=["Skill Gap Analysis"]
)


@router.post(
    "/analyze-unified/{job_id}",
    response_model=UnifiedSkillGapResponse,
    status_code=status.HTTP_200_OK,
    summary="Unified Skill-Gap Analysis against Job using Complete Multi-Source Profile Intelligence"
)
def post_unified_skill_gap(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return analyze_unified_skill_gap(
        db=db,
        job_id=job_id,
        current_user=current_user
    )


@router.get(
    "/analyze-unified/{job_id}",
    response_model=UnifiedSkillGapResponse,
    status_code=status.HTTP_200_OK,
    summary="Fetch Unified Skill-Gap Analysis against Job"
)
def get_unified_skill_gap(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return analyze_unified_skill_gap(
        db=db,
        job_id=job_id,
        current_user=current_user
    )


@router.post(
    "/analyze/{resume_id}/{job_id}",
    response_model=SkillGapResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger skill gap analysis for a specific resume and job"
)
def post_skill_gap(
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


@router.get(
    "/{resume_id}/{job_id}",
    response_model=SkillGapResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze skill gap for a specific resume and job"
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