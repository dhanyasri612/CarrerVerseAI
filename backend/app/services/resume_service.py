import os
import shutil
import uuid
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.user import User

UPLOAD_DIR = "uploads/resumes"

os.makedirs(UPLOAD_DIR, exist_ok=True)


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

    resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=file_size,
        parsed_status=False
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

    return {
        "message": "Resume deleted successfully."
    }