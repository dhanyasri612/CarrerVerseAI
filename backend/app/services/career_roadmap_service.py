from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.models.job import Job
from app.models.user import User
from app.utils.skill_normalizer import normalize_skill


SKILL_LEARNING_PATHS = {
    "python": "Learn Python fundamentals, data structures, functions, and object-oriented programming.",
    "fastapi": "Learn FastAPI routing, request validation, dependency injection, and API development.",
    "postgresql": "Learn PostgreSQL fundamentals, SQL queries, joins, indexes, and database design.",
    "docker": "Learn Docker fundamentals, images, containers, Dockerfiles, and containerized deployment.",
    "javascript": "Learn JavaScript fundamentals, ES6+, asynchronous programming, and DOM concepts.",
    "react": "Learn React components, props, state, hooks, and frontend application development.",
    "node.js": "Learn Node.js fundamentals, Express APIs, asynchronous programming, and backend development.",
    "mongodb": "Learn MongoDB documents, collections, CRUD operations, indexing, and aggregation.",
}


def analyze_career_roadmap(
    db: Session,
    resume_id: int,
    job_id: int,
    current_user: User
):
    # 1. Check resume ownership
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

    # 3. Get target job
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

    # 4. Normalize resume skills
    current_skills = {
        normalize_skill(skill)
        for skill in (parsed_resume.skills or [])
        if skill
    }

    # 5. Normalize required job skills
    required_skills = {
        normalize_skill(skill)
        for skill in (job.required_skills or [])
        if skill
    }

    # 6. Find missing skills
    missing_skills = required_skills.difference(current_skills)

    # 7. Create roadmap
    roadmap = []

    for index, skill in enumerate(sorted(missing_skills), start=1):

        description = SKILL_LEARNING_PATHS.get(
            skill,
            f"Learn the fundamentals of {skill} and practice it through projects."
        )

        roadmap.append({
            "step": index,
            "skill": skill,
            "description": description
        })

    return {
        "resume_id": resume_id,
        "job_id": job_id,
        "current_skills": sorted(current_skills),
        "missing_skills": sorted(missing_skills),
        "roadmap": roadmap
    }