from sqlalchemy import Column, Integer, String, DateTime , ForeignKey , Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime

class Resume(Base):
    
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255),nullable=False)
    file_path = Column(String(500),nullable=False)
    file_type = Column(String(50),nullable=False)
    file_size = Column(Integer,nullable=False)
    parsed_status = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    user = relationship("User", back_populates="resumes")
    parsed_resume = relationship(
        "ParsedResume",
        back_populates="resume",
        uselist=False,
        cascade="all, delete-orphan",
    )
