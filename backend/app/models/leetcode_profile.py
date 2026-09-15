from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class LeetCodeProfile(Base):
    __tablename__ = "leetcode_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    username = Column(String(255), nullable=False)
    profile_url = Column(String(500), nullable=True)
    real_name = Column(String(255), nullable=True)
    about = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    ranking = Column(Integer, nullable=True)
    reputation = Column(Integer, nullable=True)

    # Problem statistics
    total_solved = Column(Integer, default=0)
    easy_solved = Column(Integer, default=0)
    medium_solved = Column(Integer, default=0)
    hard_solved = Column(Integer, default=0)
    acceptance_rate = Column(Float, nullable=True)
    total_submissions = Column(Integer, default=0)

    # Contest statistics
    contest_rating = Column(Float, nullable=True)
    contest_ranking = Column(Integer, nullable=True)
    contest_attended = Column(Integer, default=0)
    contest_top_percentage = Column(Float, nullable=True)
    contest_badge = Column(String(100), nullable=True)

    # Rich metadata
    badges = Column(JSON, nullable=True)
    languages = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    recent_submissions = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user = relationship("User", back_populates="leetcode_profile")
