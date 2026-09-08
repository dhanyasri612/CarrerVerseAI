from sqlalchemy import Column , Integer , String , Boolean , ForeignKey ,  Text , DateTime
from sqlalchemy.orm import relationship 
from app.database.database import Base
from datetime import datetime
from app.models.resume import Resume

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String(255),index=True,nullable=False)
    email = Column(String(255),index=True,nullable=False,unique=True)
    hashed_password = Column(String(255),nullable=False)
    college = Column(String,nullable=True)
    degree = Column(String,nullable=True)
    graduation_year = Column(Integer,nullable=True)
    location = Column(String,nullable=True)
    bio = Column(Text,nullable=True)
    phone = Column(String(),index=True)
    is_active = Column(Boolean,default=True)
    role_id = Column(Integer,ForeignKey("roles.id"),nullable=False)
    role = relationship("Role",back_populates="users")
    resumes = relationship("Resume", back_populates="user",cascade="all,delete-orphan")
    candidate_profile = relationship(
    "CandidateProfile",
    back_populates="user",
    uselist=False,
    cascade="all,delete-orphan"
    )
    github_profile = relationship(
    "GitHubProfile",
    back_populates="user",
    uselist=False,
    cascade="all,delete-orphan"
    )
    
    created_at = Column(DateTime,default=datetime.utcnow)
    updated_at = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)