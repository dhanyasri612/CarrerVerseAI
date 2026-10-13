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

    if job and job.required_skills:
        requirements = [item.strip() for item in job.required_skills if isinstance(item, str) and item.strip()]
        if requirements:
            return requirements

    from app.ai.agents.role_requirements import get_role_requirements
    role_req = get_role_requirements(request.target_role)
    if role_req and role_req.get("required_skills"):
        return role_req["required_skills"]

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Role requirements are unavailable for the target role",
    )


def _build_candidate_evidence(
    db: Session,
    current_user: User,
    resume: Resume,
) -> str:
    parsed = getattr(resume, "parsed_resume", None)
    if parsed and parsed.skills:
        resume_dict = {
            "skills": parsed.skills,
            "education": parsed.education or [],
            "experience": parsed.experience or [],
            "projects": parsed.projects or [],
            "certifications": parsed.certifications or [],
            "achievements": [],
        }
    else:
        resume_analysis = analyze_resume_intelligence(
            db=db,
            current_user=current_user,
            resume_id=resume.id,
        )
        resume_dict = (
            resume_analysis.model_dump(mode="json")
            if hasattr(resume_analysis, "model_dump")
            else dict(resume_analysis)
        )

    unified_profile = build_unified_candidate_profile(db=db, current_user=current_user)
    profile_dict = (
        unified_profile.model_dump(mode="json")
        if hasattr(unified_profile, "model_dump")
        else dict(unified_profile)
    )

    compact_skills = [
        {"name": s.get("name"), "category": s.get("category"), "confidence": s.get("confidence_score"), "sources": s.get("sources")}
        for s in (profile_dict.get("unified_skills") or [])[:30]
        if isinstance(s, dict)
    ]

    cert_items = (profile_dict.get("certifications_summary") or {}).get("items", [])
    compact_certs = [
        c.get("title") or c.get("name")
        for c in cert_items
        if isinstance(c, dict) and (c.get("title") or c.get("name"))
    ]

    hr = profile_dict.get("hackerrank_summary") or {}
    compact_hr = {
        "badges": [b.get("badge_name") for b in hr.get("badges", []) if isinstance(b, dict) and b.get("badge_name")]
    }

    lc = profile_dict.get("leetcode_summary") or {}
    compact_lc = {
        "total_solved": lc.get("total_solved"),
        "ranking": lc.get("ranking"),
    }

    evidence: dict[str, Any] = {
        "phase_2_resume_intelligence": {
            "skills": resume_dict.get("skills", []),
            "education": resume_dict.get("education", []),
            "experience": resume_dict.get("experience", []),
            "projects": resume_dict.get("projects", []),
            "certifications": resume_dict.get("certifications", []),
            "achievements": resume_dict.get("achievements", []),
        },
        "multi_source_candidate_profile": {
            "unified_skills": compact_skills,
            "experience": profile_dict.get("experience", []),
            "projects": [
                {
                    "title": p.get("title") if isinstance(p, dict) else getattr(p, "title", str(p)),
                    "technologies": p.get("technologies") if isinstance(p, dict) else getattr(p, "technologies", []),
                }
                for p in (profile_dict.get("projects") or [])[:10]
            ],
            "certifications": compact_certs,
            "github": profile_dict.get("github_summary", {}),
            "leetcode": compact_lc,
            "hackerrank": compact_hr,
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
