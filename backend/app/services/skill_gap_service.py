from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.models.job import Job
from app.models.user import User
from app.utils.skill_normalizer import normalize_skill


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
            status_code=404,
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
            status_code=404,
            detail="Parsed resume not found"
        )

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    resume_skills = parsed_resume.skills or []
    required_skills = job.required_skills or []

    resume_skills = {
        normalize_skill(skill)
        for skill in resume_skills
        if skill
    }

    required_skills = {
        normalize_skill(skill)
        for skill in required_skills
        if skill
    }

    matched_skills = resume_skills.intersection(
        required_skills
    )

    missing_skills = required_skills.difference(
        resume_skills
    )

    if required_skills:
        match_percentage = (
            len(matched_skills) /
            len(required_skills)
        ) * 100
    else:
        match_percentage = 0

    return {
        "resume_id": resume_id,
        "job_id": job_id,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "match_percentage": round(
            match_percentage,
            2
        )
    }