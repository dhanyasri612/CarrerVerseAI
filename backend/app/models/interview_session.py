from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text

from app.database.database import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    session_id = Column(String(36), primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    target_role = Column(String(200), nullable=True)
    interview_mode = Column(String(30), nullable=False)
    focus_topic = Column(String(200), nullable=True)
    language = Column(String(10), nullable=False, default="en")
    current_question = Column(JSON, nullable=True)
    question_number = Column(Integer, nullable=False, default=1)
    transcript = Column(JSON, nullable=False, default=list)
    final_report = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)