from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.resume import Resume
from app.parsers.resume_parser import parse_resume
from app.parsers.resume_parser import RESUME_PARSER_VERSION
from app.models.user import User
from app.models.parsed_resume import ParsedResume
from app.services.resume_service import _sha256_file


def parse_resume_by_id(db: Session, resume_id: int, current_user: User):
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
    
    existing = (
        db.query(ParsedResume)
        .filter(ParsedResume.resume_id == resume.id)
        .first()
    )

    import os
    if not os.path.exists(resume.file_path):
        if existing:
            return existing
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found on disk. Please upload your resume again."
        )

    content_hash = _sha256_file(resume.file_path)
    if (
        existing
        and resume.content_hash == content_hash
        and resume.parser_version == RESUME_PARSER_VERSION
        and resume.parsed_status
    ):
        return existing

    try:
        parsed_data = parse_resume(resume.file_path)
    except Exception as e:
        resume.parsed_status = False
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse resume file: {str(e)}"
        )

    parsed_resume = existing or ParsedResume(resume_id=resume.id)
    parsed_resume.name = parsed_data.name
    parsed_resume.email = parsed_data.email
    parsed_resume.phone = parsed_data.phone
    parsed_resume.skills = parsed_data.skills
    parsed_resume.education = parsed_data.education
    parsed_resume.experience = parsed_data.experience
    parsed_resume.projects = parsed_data.projects
    parsed_resume.certifications = parsed_data.certifications
    if not existing:
        db.add(parsed_resume)
    resume.parsed_status = True
    resume.content_hash = content_hash
    resume.parser_version = RESUME_PARSER_VERSION
    resume.parsed_at = datetime.utcnow()
    db.commit()
    db.refresh(parsed_resume)
    from app.ai.stores.candidate_store_sync import sync_candidate_ai_stores_safe
    sync_candidate_ai_stores_safe(db, current_user)
    return parsed_resume


def get_parsed_resume_by_id(
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
    
    return parsed_resume


def delete_parsed_resume(
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

    db.delete(parsed_resume)
    resume.parsed_status = False
    db.commit()
    from app.ai.stores.candidate_store_sync import sync_candidate_ai_stores_safe
    sync_candidate_ai_stores_safe(db, current_user)

    return {
        "message": "Parsed resume deleted successfully"
    }


def reparse_resume(
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    existing = (
        db.query(ParsedResume)
        .filter(
            ParsedResume.resume_id == resume.id
        )
        .first()
    )

    try:
        parsed_data = parse_resume(resume.file_path)
    except Exception as e:
        resume.parsed_status = False
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reparse resume file: {str(e)}"
        )

    parsed_resume = existing or ParsedResume(resume_id=resume.id)
    parsed_resume.name = parsed_data.name
    parsed_resume.email = parsed_data.email
    parsed_resume.phone = parsed_data.phone
    parsed_resume.skills = parsed_data.skills
    parsed_resume.education = parsed_data.education
    parsed_resume.experience = parsed_data.experience
    parsed_resume.projects = parsed_data.projects
    parsed_resume.certifications = parsed_data.certifications
    if not existing:
        db.add(parsed_resume)
    resume.parsed_status = True
    resume.content_hash = _sha256_file(resume.file_path)
    resume.parser_version = RESUME_PARSER_VERSION
    resume.parsed_at = datetime.utcnow()
    db.commit()
    db.refresh(parsed_resume)
    from app.ai.stores.candidate_store_sync import sync_candidate_ai_stores_safe
    sync_candidate_ai_stores_safe(db, current_user)

    return parsed_resume
