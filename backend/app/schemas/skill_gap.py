from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class SkillGapResponse(BaseModel):
    resume_id: int
    job_id: int
    matched_skills: List[str]
    missing_skills: List[str]
    match_percentage: float

    model_config = ConfigDict(from_attributes=True)


class MatchedSkillDetail(BaseModel):
    name: str = Field(..., description="Canonical skill name")
    category: str = Field(..., description="Skill taxonomy category")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Evidence confidence score")
    sources: List[str] = Field(default_factory=list, description="Verified data sources for this skill")


class UnifiedSkillGapResponse(BaseModel):
    job_id: int
    job_title: str
    company: str
    match_percentage: float
    total_required_skills: int
    matched_skills_count: int
    missing_skills_count: int
    matched_skills: List[str]
    missing_skills: List[str]
    matched_skills_details: List[MatchedSkillDetail] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    profile_completeness_score: int

    model_config = ConfigDict(from_attributes=True)