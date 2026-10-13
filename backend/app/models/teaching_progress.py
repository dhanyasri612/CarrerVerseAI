from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Boolean
from app.database.database import Base


class TeachingProgress(Base):
    __tablename__ = "teaching_progress"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    section_id = Column(String(50), nullable=False, index=True)
    lesson_id = Column(String(100), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="in_progress")  # in_progress, completed, mastered
    turns = Column(JSON, nullable=False, default=list)  # list of interaction turns
    hints_used = Column(Integer, nullable=False, default=0)
    current_stage = Column(String(50), nullable=False, default="objective")
    assessment_score = Column(Integer, nullable=True)
    mastery_evidence = Column(JSON, nullable=True, default=dict)
    recommended_next_lesson_id = Column(String(100), nullable=True)
    resources_viewed = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

