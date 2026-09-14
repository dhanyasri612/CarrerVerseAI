from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.resume import Resume
from app.parsers.resume_parser import parse_resume
from app.models.user import User
from app.models.parsed_resume import ParsedResume


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

    if existing:
        db.delete(existing)
        db.commit()

    try:
        parsed_data = parse_resume(resume.file_path)
    except Exception as e:
        resume.parsed_status = False
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse resume file: {str(e)}"
        )

    parsed_resume = ParsedResume(
        resume_id=resume.id,
        name=parsed_data.name,
        email=parsed_data.email,
        phone=parsed_data.phone,
        skills=parsed_data.skills,
        education=parsed_data.education,
        experience=parsed_data.experience,
        projects=parsed_data.projects,
        certifications=parsed_data.certifications,
    )
    db.add(parsed_resume)
    resume.parsed_status = True
    db.commit()
    db.refresh(parsed_resume)
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

    if existing:
        db.delete(existing)
        db.commit()

    try:
        parsed_data = parse_resume(resume.file_path)
    except Exception as e:
        resume.parsed_status = False
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reparse resume file: {str(e)}"
        )

    parsed_resume = ParsedResume(
        resume_id=resume.id,
        name=parsed_data.name,
        email=parsed_data.email,
        phone=parsed_data.phone,
        skills=parsed_data.skills,
        education=parsed_data.education,
        experience=parsed_data.experience,
        projects=parsed_data.projects,
        certifications=parsed_data.certifications
    )

    db.add(parsed_resume)
    resume.parsed_status = True
    db.commit()
    db.refresh(parsed_resume)

    return parsed_resume