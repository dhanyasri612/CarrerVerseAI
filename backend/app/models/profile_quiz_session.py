from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.sql import func

from app.database.database import Base


class ProfileQuizSession(Base):
    __tablename__ = "profile_quiz_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    language = Column(String(5), nullable=False, default="en")
    questions = Column(JSON, nullable=False, default=list)
    answers = Column(JSON, nullable=False, default=list)
    question_number = Column(Integer, nullable=False, default=1)
    status = Column(String(20), nullable=False, default="active")
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
