from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from app.database.database import Base


class CourseDocument(Base):
    """
    Persists metadata and indexing lifecycle status for candidate-uploaded course materials
    (PDF, Markdown, TXT) used as authoritative grounding in the AI Teaching Room.
    """
    __tablename__ = "course_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(32), nullable=False)  # "pdf", "markdown", "text"
    mime_type = Column(String(128), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="uploaded")  # "uploaded", "indexed", "failed", "degraded"
    error_message = Column(Text, nullable=True)
    total_pages = Column(Integer, nullable=True)
    total_chunks = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
