from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.models.job import Job
from app.models.user import User
from app.parsers.skill_normalizer import get_canonical_skill_name


def get_job_recommendations(
    db: Session,
    resume_id: int,
    current_user: User
):
    # 1. Check that the resume belongs to the user
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

    # 2. Get parsed resume
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

    # 3. Get all jobs
    jobs = db.query(Job).all()

    # Map candidate skills to canonical names
    resume_skills_map = {}
    for skill in (parsed_resume.skills or []):
        if skill and isinstance(skill, str):
            canonical = get_canonical_skill_name(skill)
            if canonical:
                resume_skills_map[canonical.lower()] = canonical

    recommendations = []

    # 4. Compare resume with every job
    for job in jobs:
        required_skills_map = {}
        for skill in (job.required_skills or []):
            if skill and isinstance(skill, str):
                canonical = get_canonical_skill_name(skill)
                if canonical:
                    required_skills_map[canonical.lower()] = canonical

        matched_keys = set(resume_skills_map.keys()).intersection(set(required_skills_map.keys()))
        missing_keys = set(required_skills_map.keys()) - set(resume_skills_map.keys())

        matched_skills = [required_skills_map[k] for k in sorted(matched_keys)]
        missing_skills = [required_skills_map[k] for k in sorted(missing_keys)]

        if required_skills_map:
            match_percentage = (len(matched_skills) / len(required_skills_map)) * 100
        else:
            match_percentage = 100.0 if resume_skills_map else 0.0

        recommendations.append({
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "salary": job.salary,
            "match_percentage": round(match_percentage, 2),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills
        })

    # 5. Sort highest match first
    recommendations.sort(
        key=lambda x: x["match_percentage"],
        reverse=True
    )

    return recommendations