"""
Pydantic schemas for Multi-Agent Coordination and Final Synthesis.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.interview import InterviewQuestion, InterviewResponse
from app.schemas.language import MultilingualResponseMetadata
from app.schemas.recommendation import (
    CareerRecommendationItem,
    CareerRecommendationResponse,
)
from app.schemas.skill_gap import SkillGapItem, SkillGapResponse


class AgentExecutionResult(BaseModel):
    """
    Status and audit tracking for an individual specialized agent execution.
    """
    model_config = ConfigDict(extra="ignore")

    agent_name: str = Field(..., description="Name of the specialized agent (e.g., recommendation, evaluation, interview)")
    status: str = Field(..., description="Execution status: success, failed, skipped, partial, invalid_role")
    execution_time_ms: Optional[float] = Field(None, description="Execution duration in milliseconds")
    result_summary: Optional[str] = Field(None, description="Brief summary of the agent's outcome")
    errors: List[str] = Field(default_factory=list, description="Errors encountered during agent execution")


class MultiAgentResponse(BaseModel):
    """
    Structured response synthesized across multiple coordinated specialized agents.
    """
    model_config = ConfigDict(extra="ignore")

    candidate_id: Optional[int] = Field(None, description="Candidate ID evaluated")
    query: str = Field(..., description="Original user query")
    language: str = Field("en", description="Target response language code (e.g., 'en', 'ta', 'hi')")
    language_metadata: Optional[MultilingualResponseMetadata] = Field(
        None,
        description="Language detection and normalization metadata",
    )
    target_role: Optional[str] = Field(None, description="Target job role evaluated or derived")
    agents_used: List[str] = Field(default_factory=list, description="List of specialized agents that executed")
    summary: str = Field(..., description="High-level synthesized executive summary")
    recommendations: List[CareerRecommendationItem] = Field(
        default_factory=list,
        description="Grounded role recommendations from Recommendation Agent",
    )
    recommendation_details: Optional[CareerRecommendationResponse] = Field(
        None,
        description="Full Recommendation Agent response payload when executed",
    )
    skill_gaps: List[SkillGapItem] = Field(
        default_factory=list,
        description="Structured skill gaps and strengths from Evaluation Agent",
    )
    evaluation_details: Optional[SkillGapResponse] = Field(
        None,
        description="Full Evaluation Agent response payload when executed",
    )
    interview_preparation: List[InterviewQuestion] = Field(
        default_factory=list,
        description="Personalized grounded interview questions from Interview Agent",
    )
    interview_details: Optional[InterviewResponse] = Field(
        None,
        description="Full Interview Agent response payload when executed",
    )
    final_guidance: str = Field(
        "",
        description="Unified, actionable career intelligence guidance synthesizing all findings",
    )
    evidence: Dict[str, Any] = Field(
        default_factory=dict,
        description="Aggregated audit metrics (sources, skills, projects, technologies)",
    )
    agent_results: Dict[str, AgentExecutionResult] = Field(
        default_factory=dict,
        description="Detailed execution status for each specialized agent",
    )
    model_name: Optional[str] = Field(None, description="LLM model identifier used for synthesis")
    status: str = Field(
        "completed",
        description="Overall execution status: completed, partial, failed, validation_failed, invalid_role",
    )
    errors: List[str] = Field(default_factory=list, description="Accumulated execution or parsing errors")

