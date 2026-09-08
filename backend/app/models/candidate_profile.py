from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey , JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class CandidateProfile(Base):
    
    __tablename__ = "candidate_profiles"
    
    id = Column(Integer,primary_key=True,index=True)
    
    user_id = Column(Integer,ForeignKey("users.id"),unique=True,nullable=False)
    
    summary = Column(Text,nullable=True)
    
    skills = Column(JSON,nullable=True)
    
    education = Column(JSON,nullable=True)
    
    experience = Column(JSON,nullable=True)
    
    projects = Column(JSON,nullable=True)
    
    certifications = Column(JSON,nullable=True)
    
    github_data = Column(JSON,nullable=True)
    
    coding_data = Column(JSON,nullable=True)
    
    created_at = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    
    user = relationship("User",back_populates="candidate_profile")