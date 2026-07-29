from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.parsers.resume_parser import parse_resume
from app.models.user import User


def parse_resume_by_id(db: Session, resume_id: int , current_user: User):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return parse_resume(resume.file_path)