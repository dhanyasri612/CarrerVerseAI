from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


SkillStatus = Literal[
    "demonstrated",
    "supported",
    "partially_supported",
    "self_reported",
    "unverified",
    "missing",
]
SkillPriority = Literal["critical", "high", "medium", "low"]
SkillConfidence = Literal["high", "medium", "low", "unverified"]


class SkillGapRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resume_id: int = Field(..., gt=0)
    target_role: str = Field(..., min_length=1, max_length=255)
    role_requirements: Optional[List[str]] = Field(
        None,
        description="Optional requirements when no matching stored Job exists.",
    )
    job_id: Optional[int] = Field(None, gt=0)


class CurrentSkillSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    demonstrated_skills: List[str] = Field(...)
    supported_skills: List[str] = Field(...)
    partially_supported_skills: List[str] = Field(...)
    self_reported_skills: List[str] = Field(...)
    unverified_skills: List[str] = Field(...)


class SkillGapItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    status: SkillStatus = Field(...)
    confidence: SkillConfidence = Field(...)
    priority: SkillPriority = Field(...)
    reason: str = Field(..., min_length=1)
    evidence: List[str] = Field(...)
    related_skills: List[str] = Field(...)


class RoadmapStage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: int = Field(..., ge=1)
    title: str = Field(..., min_length=1)
    goal: str = Field(..., min_length=1)
    skills: List[str] = Field(...)
    prerequisites: List[str] = Field(...)
    estimated_effort: str = Field(..., min_length=1)
    learning_objectives: List[str] = Field(...)
    practical_task: str = Field(..., min_length=1)


class SkillGapSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_gaps: int = Field(..., ge=0)
    critical_gaps: int = Field(..., ge=0)
    high_priority_gaps: int = Field(..., ge=0)
    medium_priority_gaps: int = Field(..., ge=0)
    low_priority_gaps: int = Field(..., ge=0)


class SkillGapAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_role: str = Field(..., min_length=1)
    current_skill_summary: CurrentSkillSummary = Field(...)
    skill_gaps: List[SkillGapItem] = Field(...)
    roadmap: List[RoadmapStage] = Field(...)
    summary: SkillGapSummary = Field(...)
