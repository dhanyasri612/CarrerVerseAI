from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.user import User
from app.parsers.resume_parser import extract_text_from_pdf
from app.schemas.resume_ai import ResumeAIAnalysis
from app.services.ai_service import ai_service


def analyze_resume_intelligence(db: Session, current_user: User, resume_id: int) -> ResumeAIAnalysis:
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    try:
        resume_text = extract_text_from_pdf(resume.file_path)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text is unavailable for AI analysis",
        ) from exc

    if not resume_text or not resume_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text is unavailable for AI analysis",
        )

    try:
        result, _ = ai_service.generate_resume_intelligence(resume_text=resume_text)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume AI analysis failed",
        ) from exc
