from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class HackerRankProfile(Base):
    __tablename__ = "hackerrank_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    username = Column(String(255), nullable=False)
    profile_url = Column(String(500), nullable=True)
    display_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    country = Column(String(100), nullable=True)
    school = Column(String(255), nullable=True)

    # Problem solving & achievements
    total_solved = Column(Integer, default=0)

    # Rich metadata
    badges = Column(JSON, nullable=True)
    certificates = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    domain_statistics = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user = relationship("User", back_populates="hackerrank_profile")
