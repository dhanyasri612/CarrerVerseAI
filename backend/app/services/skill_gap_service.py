from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.models.job import Job
from app.models.user import User
from app.parsers.skill_normalizer import normalize_skill, get_canonical_skill_name
from app.services.unified_profile_service import build_unified_candidate_profile


def analyze_skill_gap(
    db: Session,
    resume_id: int,
    job_id: int,
    current_user: User
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    parsed_resume = (
        db.query(ParsedResume)
        .filter(
            ParsedResume.resume_id == resume.id
        )
        .first()
    )

    if not parsed_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parsed resume not found"
        )

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    resume_skills_map = {}
    for s in (parsed_resume.skills or []):
        if s and isinstance(s, str):
            canon = get_canonical_skill_name(s)
            if canon:
                resume_skills_map[canon.lower()] = canon

    required_skills_map = {}
    for s in (job.required_skills or []):
        if s and isinstance(s, str):
            canon = get_canonical_skill_name(s)
            if canon:
                required_skills_map[canon.lower()] = canon

    matched_keys = set(resume_skills_map.keys()).intersection(set(required_skills_map.keys()))
    missing_keys = set(required_skills_map.keys()) - set(resume_skills_map.keys())

    matched_skills = [required_skills_map[k] for k in sorted(matched_keys)]
    missing_skills = [required_skills_map[k] for k in sorted(missing_keys)]

    if required_skills_map:
        match_percentage = (len(matched_skills) / len(required_skills_map)) * 100
    else:
        match_percentage = 100.0 if resume_skills_map else 0.0

    return {
        "resume_id": resume_id,
        "job_id": job_id,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "match_percentage": round(match_percentage, 2)
    }


def analyze_unified_skill_gap(
    db: Session,
    job_id: int,
    current_user: User
) -> Dict[str, Any]:
    """
    Perform deep skill-gap analysis comparing the candidate's complete
    multi-source Unified Candidate Profile against job requirements.
    """
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # 1. Build unified candidate intelligence profile
    unified_profile = build_unified_candidate_profile(db=db, current_user=current_user)

    # 2. Map candidate skills
    candidate_skills_dict = {}
    for skill_item in unified_profile.unified_skills:
        canonical_name = skill_item.name
        candidate_skills_dict[canonical_name.lower()] = skill_item

    # 3. Map required job skills
    raw_required = job.required_skills or []
    required_skills_map = {}
    for raw_req in raw_required:
        if not raw_req or not isinstance(raw_req, str):
            continue
        canon_name, cat = normalize_skill(raw_req)
        if canon_name:
            required_skills_map[canon_name.lower()] = (canon_name, cat)

    matched_skills = []
    missing_skills = []
    matched_skills_details = []

    for req_key, (canon_name, cat) in required_skills_map.items():
        if req_key in candidate_skills_dict:
            matched_skills.append(canon_name)
            skill_info = candidate_skills_dict[req_key]
            matched_skills_details.append({
                "name": canon_name,
                "category": skill_info.category or cat,
                "confidence_score": skill_info.confidence_score,
                "sources": skill_info.sources
            })
        else:
            missing_skills.append(canon_name)

    total_required = len(required_skills_map)
    if total_required > 0:
        match_percentage = round((len(matched_skills) / total_required) * 100, 2)
    else:
        match_percentage = 100.0 if len(candidate_skills_dict) > 0 else 0.0

    # 4. Generate contextual, intelligent recommendations
    recommendations: List[str] = []
    if missing_skills:
        top_missing = missing_skills[:3]
        recommendations.append(f"Target priority skills to acquire: {', '.join(top_missing)}.")

    if unified_profile.completeness.score < 80:
        recommendations.append("Connect more external integrations (GitHub, LeetCode, Certifications) to provide additional proof for your verified skills.")

    if match_percentage >= 80.0:
        recommendations.append("High match profile! Your verified skill profile strongly aligns with this role's requirements.")
    elif match_percentage >= 50.0:
        recommendations.append("Moderate match. Closing the identified skill gaps will make your profile highly competitive.")
    else:
        recommendations.append("Consider completing relevant certifications and repositories to demonstrate required skills before applying.")

    return {
        "job_id": job.id,
        "job_title": job.title,
        "company": job.company,
        "match_percentage": match_percentage,
        "total_required_skills": total_required,
        "matched_skills_count": len(matched_skills),
        "missing_skills_count": len(missing_skills),
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "matched_skills_details": matched_skills_details,
        "recommendations": recommendations,
        "profile_completeness_score": unified_profile.completeness.score
    }