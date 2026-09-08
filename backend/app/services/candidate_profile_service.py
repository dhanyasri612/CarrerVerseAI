from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.models.candidate_profile import CandidateProfile


def aggregate_candidate_profile(
    db: Session,
    resume_id: int,
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
            ParsedResume.resume_id == resume_id
        )
        .first()
    )

    if not parsed_resume:
        raise HTTPException(
            status_code=404,
            detail="Parsed resume not found"
        )

    profile = (
        db.query(CandidateProfile)
        .filter(
            CandidateProfile.user_id == current_user.id
        )
        .first()
    )

    if not profile:
        profile = CandidateProfile(
            user_id=current_user.id
        )
        db.add(profile)

    profile.summary = (
        f"{parsed_resume.name or current_user.name} "
        f"career profile"
    )

    profile.skills = parsed_resume.skills or []
    profile.education = parsed_resume.education or []
    profile.experience = parsed_resume.experience or []
    profile.projects = parsed_resume.projects or []
    profile.certifications = parsed_resume.certifications or []

    db.commit()
    db.refresh(profile)

    return profile