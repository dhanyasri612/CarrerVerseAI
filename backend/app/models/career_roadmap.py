from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


class CareerRoadmap(Base):
    __tablename__ = "career_roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role = Column(String(100), nullable=False, index=True)
    experience_level = Column(String(50), nullable=True, default="intermediate")
    version = Column(Integer, nullable=True, default=1)
    readiness_score = Column(Integer, default=0)
    current_version = Column(Integer, default=1)
    total_milestones = Column(Integer, default=0)
    completed_milestones = Column(Integer, default=0)
    last_reviewed_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), onupdate=func.now(), nullable=False)

    versions = relationship("RoadmapVersion", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapVersion.version_number.desc()")
    change_logs = relationship("RoadmapChangeLog", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapChangeLog.created_at.desc()")
    user = relationship("User")


class RoadmapVersion(Base):
    __tablename__ = "roadmap_versions"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("career_roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, default=1)
    change_summary = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    roadmap = relationship("CareerRoadmap", back_populates="versions")
    milestones = relationship("RoadmapMilestone", back_populates="version", cascade="all, delete-orphan", order_by="RoadmapMilestone.stage_order")


class RoadmapMilestone(Base):
    __tablename__ = "roadmap_milestones"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("roadmap_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    stage_order = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    why_recommended = Column(Text, nullable=True)
    prerequisites = Column(JSON, default=list)
    estimated_effort = Column(String(50), nullable=True)
    skills = Column(JSON, default=list)
    practical_project = Column(String(255), nullable=True)
    completion_criteria = Column(JSON, default=list)
    learning_resources = Column(JSON, default=list)
    status = Column(String(50), default="upcoming")  # "completed", "in_progress", "upcoming"
    progress_pct = Column(Integer, default=0)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    version = relationship("RoadmapVersion", back_populates="milestones")


class RoadmapTrendSignal(Base):
    __tablename__ = "roadmap_trend_signals"

    id = Column(Integer, primary_key=True, index=True)
    technology = Column(String(100), nullable=False, index=True)
    target_roles = Column(JSON, default=list)
    trend_status = Column(String(50), nullable=False)  # "newly_released", "increased_attention", "job_market_required"
    why_it_matters = Column(Text, nullable=False)
    evidence_summary = Column(Text, nullable=False)
    source_name = Column(String(150), nullable=False)
    source_url = Column(String(300), nullable=False)
    publication_date = Column(String(50), nullable=False)
    source_type = Column(String(50), default="official_documentation")  # "official_release", "engineering_blog", "job_market_demand", "industry_report"
    reliability = Column(String(50), default="verified_official")
    impact_level = Column(String(50), default="high")
    last_verified_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RoadmapChangeLog(Base):
    __tablename__ = "roadmap_change_logs"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("career_roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)  # "adaptive_recommendation", "milestone_completed", "roadmap_initialized", "version_promoted"
    title = Column(String(200), nullable=False)
    why_changed = Column(Text, nullable=False)
    proposed_action = Column(Text, nullable=True)
    evidence_summary = Column(Text, nullable=True)
    evidence_source = Column(String(200), nullable=True)
    evidence_url = Column(String(300), nullable=True)
    evidence_date = Column(String(50), nullable=True)
    status = Column(String(50), default="pending")  # "pending", "accepted", "dismissed", "applied"
    suggested_milestone_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    roadmap = relationship("CareerRoadmap", back_populates="change_logs")
