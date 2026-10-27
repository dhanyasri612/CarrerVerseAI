from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.career_roadmap import (
    CareerRoadmapResponse,
    PersonalizedRoadmapResponse,
    RoadmapGenerateRequest,
)
from app.services.career_roadmap_service import analyze_career_roadmap
from app.services.career_roadmap_generator import (
    generate_or_get_personalized_roadmap,
    accept_roadmap_recommendation,
    dismiss_roadmap_recommendation,
    toggle_milestone_progress,
)
from app.services.trend_intelligence_service import trend_intelligence_service


router = APIRouter(
    prefix="/career-roadmap",
    tags=["Career Roadmap"]
)


@router.get(
    "/personalized",
    response_model=PersonalizedRoadmapResponse,
    summary="Fetch personalized, trend-aware roadmap for current authenticated user"
)
def get_personalized_roadmap_endpoint(
    role: Optional[str] = Query(None, description="Target career role"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return generate_or_get_personalized_roadmap(
        db=db,
        current_user=current_user,
        target_role=role or "AI Engineer",
        force_refresh=False
    )


@router.post(
    "/generate",
    response_model=PersonalizedRoadmapResponse,
    summary="Generate or regenerate a personalized roadmap with latest profile & trend evidence"
)
def generate_personalized_roadmap_endpoint(
    request: RoadmapGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return generate_or_get_personalized_roadmap(
        db=db,
        current_user=current_user,
        target_role=request.target_role or "AI Engineer",
        force_refresh=request.force_refresh
    )


@router.post(
    "/recommendations/{change_id}/accept",
    response_model=PersonalizedRoadmapResponse,
    summary="Accept an adaptive roadmap recommendation, creating a new roadmap version"
)
def accept_recommendation_endpoint(
    change_id: int = Path(..., description="ID of the recommendation change log"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return accept_roadmap_recommendation(
        db=db,
        current_user=current_user,
        change_id=change_id
    )


@router.post(
    "/recommendations/{change_id}/dismiss",
    summary="Dismiss an adaptive roadmap recommendation"
)
def dismiss_recommendation_endpoint(
    change_id: int = Path(..., description="ID of the recommendation change log"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return dismiss_roadmap_recommendation(
        db=db,
        current_user=current_user,
        change_id=change_id
    )


@router.post(
    "/milestones/{milestone_id}/toggle",
    response_model=PersonalizedRoadmapResponse,
    summary="Toggle milestone completion status and dynamically update readiness score"
)
def toggle_milestone_endpoint(
    milestone_id: int = Path(..., description="ID of the milestone to toggle"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return toggle_milestone_progress(
        db=db,
        current_user=current_user,
        milestone_id=milestone_id
    )


@router.get(
    "/trends/{target_role}",
    summary="Get verified technology trend intelligence signals for a target role"
)
def get_role_trends_endpoint(
    target_role: str = Path(..., description="Target career role"),
    current_user: User = Depends(get_current_user)
):
    return {
        "target_role": target_role,
        "trends": trend_intelligence_service.get_signals_for_role(target_role)
    }


# Backwards compatibility: keep original endpoint for resume_id/job_id
@router.get(
    "/{resume_id}/{job_id}",
    response_model=CareerRoadmapResponse,
    summary="Legacy resume-to-job roadmap analysis"
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