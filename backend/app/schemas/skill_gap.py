"""
Pydantic schemas for Skill-Gap & Candidate Evaluation Agent.
Includes schemas for both LangGraph Phase 5C evaluation and legacy router endpoints.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

# ----------------------------------------------------
# 1. Phase 5C LangGraph Evaluation / Skill-Gap Models
# ----------------------------------------------------

SkillGapStatus = Literal[
    "demonstrated",
    "partially_demonstrated",
    "missing",
    "insufficient_evidence",
]

GapLevel = Literal[
    "none",
    "low",
    "medium",
    "high",
]


class SkillGapItem(BaseModel):
    """
    Evaluation assessment for a single required or optional target skill.
    """
    model_config = ConfigDict(extra="ignore")

    skill: str = Field(..., description="Canonical name of the target skill")
    category: str = Field(..., description="Skill category or domain classification")
    target_requirement: str = Field("required", description="Requirement level (required or optional)")
    candidate_evidence: List[str] = Field(
        default_factory=list,
        description="Factual evidence items found in candidate data",
    )
    evidence_sources: List[str] = Field(
        default_factory=list,
        description="Originating data sources (e.g., github, resume, leetcode, graph)",
    )
    status: str = Field(
        ...,
        description="Factual evidence status: demonstrated, partially_demonstrated, missing, insufficient_evidence",
    )
    gap_level: str = Field(
        ...,
        description="Categorical gap severity: none, low, medium, high",
    )
    explanation: str = Field(
        "",
        description="Grounded explanation describing the match or deficiency",
    )


class SkillGapResponse(BaseModel):
    """
    Structured skill-gap evaluation response comparing candidate evidence against target role.
    """
    model_config = ConfigDict(extra="ignore")

    candidate_id: Optional[int] = Field(None, description="Candidate ID evaluated")
    target_role: Optional[str] = Field(None, description="Target job role evaluated")
    query: str = Field(..., description="Original user inquiry")
    strengths: List[str] = Field(
        default_factory=list,
        description="Demonstrated candidate skills that directly satisfy target requirements",
    )
    skill_gaps: List[SkillGapItem] = Field(
        default_factory=list,
        description="Detailed breakdown of each target skill requirement and gap level",
    )
    summary: str = Field(
        ...,
        description="Grounded narrative synthesis of the candidate's skill fit",
    )
    improvement_areas: List[str] = Field(
        default_factory=list,
        description="Actionable, grounded learning/upskilling focus areas",
    )
    model_name: Optional[str] = Field(None, description="LLM model identifier used for narrative synthesis")
    status: str = Field("completed", description="Execution status: completed, invalid_role, failed")
    errors: List[str] = Field(default_factory=list, description="Any validation or execution errors")
    matched_skills: List[Dict[str, Any]] = Field(default_factory=list, description="List of matched skills with evidence")
    missing_skills: List[Dict[str, Any]] = Field(default_factory=list, description="List of missing target skills")
    partial_skills: List[Dict[str, Any]] = Field(default_factory=list, description="List of partially demonstrated skills")
    readiness_score: Optional[float] = Field(None, description="Readiness ratio (0.0 to 1.0)")


# ----------------------------------------------------
# 2. Legacy Router & Service Skill Gap Models
# ----------------------------------------------------

class MatchedSkillDetail(BaseModel):
    """Detail of a matched skill against job requirements."""
    model_config = ConfigDict(extra="ignore")

    name: str
    category: str
    confidence_score: float = 0.5
    sources: List[str] = Field(default_factory=list)


class UnifiedSkillGapResponse(BaseModel):
    """Response model for Unified Multi-Source Profile vs. Job Skill-Gap Analysis."""
    model_config = ConfigDict(extra="ignore")

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
    profile_completeness_score: int = 0


class ResumeSkillGapResponse(BaseModel):
    """Response model for individual Resume vs. Job Skill-Gap Analysis."""
    model_config = ConfigDict(extra="ignore")

    resume_id: int
    job_id: int
    matched_skills: List[str]
    missing_skills: List[str]
    match_percentage: float