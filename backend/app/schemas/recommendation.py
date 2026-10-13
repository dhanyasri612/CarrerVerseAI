"""
Pydantic schemas for Candidate Career Recommendations.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ----------------------------------------------------
# 1. Legacy Job Recommendation Model
# ----------------------------------------------------

class JobRecommendation(BaseModel):
    """
    Response model for resume vs. job matching recommendations.
    """
    model_config = ConfigDict(extra="ignore")

    job_id: int
    title: str
    company: str
    location: Optional[str] = None
    salary: Optional[str] = None
    match_percentage: float
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)


# ----------------------------------------------------
# 2. Phase 5B LangGraph Career Recommendation Models
# ----------------------------------------------------

class CareerRecommendationItem(BaseModel):
    """
    Individual grounded career role recommendation.
    """
    model_config = ConfigDict(extra="ignore")

    title: str = Field(..., description="Recommended career role title (e.g., Full Stack Engineer)")
    category: str = Field(..., description="Career category or specialization domain")
    rationale: str = Field(..., description="Grounded explanation for why this role is recommended")
    supporting_skills: List[str] = Field(
        default_factory=list,
        description="Verified candidate skills from profile/graph directly supporting this role",
    )
    supporting_projects: List[str] = Field(
        default_factory=list,
        description="Relevant candidate projects demonstrating applied capability",
    )
    supporting_technologies: List[str] = Field(
        default_factory=list,
        description="Verified technologies used by candidate relevant to this role",
    )
    supporting_experience: List[str] = Field(
        default_factory=list,
        description="Relevant work or extracurricular experience supporting this recommendation",
    )
    confidence: str = Field(
        ...,
        description="Advisory/heuristic fit level (e.g. 'High (Heuristic)', 'Medium (Heuristic)'). Not a statistical probability.",
    )


class CareerRecommendationResponse(BaseModel):
    """
    Structured response container for grounded candidate career recommendations.
    """
    model_config = ConfigDict(extra="ignore")

    candidate_id: Optional[int] = Field(None, description="Candidate ID evaluated")
    query: str = Field(..., description="Original user recommendation query")
    recommendations: List[CareerRecommendationItem] = Field(
        default_factory=list,
        description="List of structured grounded role recommendations",
    )
    explanation: str = Field(
        ...,
        description="Comprehensive narrative explanation synthesizing the recommendations",
    )
    evidence: Dict[str, Any] = Field(
        default_factory=dict,
        description="Audit evidence metrics (skills count, projects count, sources)",
    )
    model_name: Optional[str] = Field(None, description="Generative model used for recommendation synthesis")
    status: str = Field("completed", description="Execution status (e.g., completed, insufficient_data, failed)")
    errors: List[str] = Field(default_factory=list, description="Any execution or parsing errors")