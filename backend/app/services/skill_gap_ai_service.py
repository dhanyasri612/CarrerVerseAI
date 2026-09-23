import json
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ai.errors import AIInvalidResponseError
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User
from app.schemas.skill_gap_ai import SkillGapAnalysis, SkillGapRequest
from app.services.ai_service import ai_service
from app.services.resume_ai_service import analyze_resume_intelligence
from app.services.unified_profile_service import build_unified_candidate_profile


def _resolve_requirements(
    db: Session,
    request: SkillGapRequest,
) -> list[str]:
    if request.role_requirements:
        requirements = [item.strip() for item in request.role_requirements if item.strip()]
        if requirements:
            return requirements

    job_query = db.query(Job)
    job = None
    if request.job_id:
        job = job_query.filter(Job.id == request.job_id).first()
    else:
        job = job_query.filter(func.lower(Job.title) == request.target_role.lower()).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role requirements are unavailable for the target role",
        )

    requirements = [item.strip() for item in (job.required_skills or []) if isinstance(item, str) and item.strip()]
    if not requirements:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role requirements are unavailable for the target role",
        )
    return requirements


def _build_candidate_evidence(
    db: Session,
    current_user: User,
    resume: Resume,
) -> str:
    resume_analysis = analyze_resume_intelligence(
        db=db,
        current_user=current_user,
        resume_id=resume.id,
    )
    unified_profile = build_unified_candidate_profile(db=db, current_user=current_user)
    profile_data = unified_profile.model_dump(mode="json")
    evidence: dict[str, Any] = {
        "phase_2_resume_intelligence": resume_analysis.model_dump(mode="json"),
        "multi_source_candidate_profile": {
            "unified_skills": profile_data.get("unified_skills", []),
            "education": profile_data.get("education", []),
            "experience": profile_data.get("experience", []),
            "projects": profile_data.get("projects", []),
            "certifications": profile_data.get("certifications_summary", {}),
            "github": profile_data.get("github_summary", {}),
            "leetcode": profile_data.get("leetcode_summary", {}),
            "hackerrank": profile_data.get("hackerrank_summary", {}),
        },
    }
    return json.dumps(evidence, ensure_ascii=True)


def analyze_skill_gap_with_roadmap(
    db: Session,
    current_user: User,
    request: SkillGapRequest,
) -> SkillGapAnalysis:
    resume = (
        db.query(Resume)
        .filter(Resume.id == request.resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    requirements = _resolve_requirements(db, request)
    candidate_evidence = _build_candidate_evidence(db, current_user, resume)
    try:
        result, _ = ai_service.generate_skill_gap_analysis(
            target_role=request.target_role,
            role_requirements=requirements,
            candidate_evidence=candidate_evidence,
        )
    except AIInvalidResponseError:
        raise
    except Exception as exc:
        raise exc

    return result
