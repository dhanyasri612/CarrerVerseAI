import os
import hashlib
import shutil
import uuid
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.user import User
from app.parsers.resume_parser import RESUME_PARSER_VERSION

UPLOAD_DIR = "uploads/resumes"

os.makedirs(UPLOAD_DIR, exist_ok=True)


def _sha256_file(file_path: str) -> str:
    digest = hashlib.sha256()
    with open(file_path, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def upload_resume(
    db: Session,
    current_user: User,
    file: UploadFile
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )
    
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is missing."
        )

    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{file_extension}"

    file_path = os.path.join(
        UPLOAD_DIR,
        unique_name
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)
    content_hash = _sha256_file(file_path)

    existing = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id, Resume.content_hash == content_hash)
        .order_by(Resume.updated_at.desc())
        .first()
    )
    if existing:
        os.remove(file_path)
        if existing.parser_version != RESUME_PARSER_VERSION:
            existing.parsed_status = False
            existing.parser_version = None
            db.commit()
        return existing

    resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=file_size,
        parsed_status=False,
        content_hash=content_hash,
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def get_resumes(
    db: Session,
    current_user: User
):
    return (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .all()
    )
    
    
def get_resume(
    db: Session,
    current_user: User,
    resume_id: int
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
            detail="Resume not found."
        )

    return resume


def delete_resume(
    db: Session,
    current_user: User,
    resume_id: int
):
    resume = get_resume(
        db,
        current_user,
        resume_id
    )

    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)

    db.delete(resume)
    db.commit()
    from app.ai.stores.candidate_store_sync import sync_candidate_ai_stores_safe
    sync_candidate_ai_stores_safe(db, current_user)

    return {
        "message": "Resume deleted successfully."
    }
