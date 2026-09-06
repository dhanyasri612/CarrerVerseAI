from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.models.job import Job
from app.models.user import User


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
            status_code=404,
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
            status_code=404,
            detail="Parsed resume not found"
        )

    # 3. Get all jobs
    jobs = db.query(Job).all()

    resume_skills = {
        skill.strip().lower()
        for skill in (parsed_resume.skills or [])
        if skill
    }

    recommendations = []

    # 4. Compare resume with every job
    for job in jobs:

        required_skills = {
            skill.strip().lower()
            for skill in (job.required_skills or [])
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
                len(matched_skills)
                / len(required_skills)
            ) * 100
        else:
            match_percentage = 0

        recommendations.append({
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "match_percentage": round(
                match_percentage,
                2
            ),
            "matched_skills": sorted(
                matched_skills
            ),
            "missing_skills": sorted(
                missing_skills
            )
        })

    # 5. Sort highest match first
    recommendations.sort(
        key=lambda x: x["match_percentage"],
        reverse=True
    )

    return recommendations