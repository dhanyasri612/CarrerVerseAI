"""
Pydantic schemas for LangGraph Career Intelligence Agent and Orchestration.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.recommendation import (
    CareerRecommendationItem,
    CareerRecommendationResponse,
)
from app.schemas.skill_gap import SkillGapResponse
from app.schemas.interview import (
    InterviewQuestion,
    InterviewResponse,
)
from app.schemas.language import MultilingualResponseMetadata
from app.schemas.multi_agent import MultiAgentResponse


class CareerIntelligenceResponse(BaseModel):
    """
    Structured response returned by the LangGraph Career Intelligence Orchestrator.
    """
    model_config = ConfigDict(extra="ignore")

    candidate_id: Optional[int] = Field(None, description="Candidate ID processed")
    query: str = Field(..., description="Original user query")
    language: str = Field("en", description="Detected or requested response language code (e.g., 'en', 'ta', 'hi')")
    language_metadata: Optional[MultilingualResponseMetadata] = Field(
        None,
        description="Detailed language detection and normalization metadata",
    )
    intent: str = Field(..., description="Detected intent (e.g. career_intelligence, recommendation, evaluation, interview, combined)")
    target_role: Optional[str] = Field(None, description="Target job role if intent is evaluation or interview")
    status: str = Field(..., description="Workflow execution status (e.g. completed, partial, failed, invalid_role, validation_failed)")
    retrieval_status: str = Field(..., description="Status of multi-modal RAG retrieval")
    generated_answer: str = Field(..., description="Generated grounded response or error detail")
    recommendations: List[CareerRecommendationItem] = Field(
        default_factory=list,
        description="Structured recommendation items if intent is recommendation or combined",
    )
    recommendation_details: Optional[CareerRecommendationResponse] = Field(
        None,
        description="Full structured recommendation payload when available",
    )
    evaluation_details: Optional[SkillGapResponse] = Field(
        None,
        description="Full structured evaluation/skill-gap payload when available",
    )
    interview_questions: List[InterviewQuestion] = Field(
        default_factory=list,
        description="Personalized interview questions if intent is interview or combined",
    )
    interview_details: Optional[InterviewResponse] = Field(
        None,
        description="Full structured interview preparation payload when available",
    )
    multi_agent_details: Optional[MultiAgentResponse] = Field(
        None,
        description="Full synthesized multi-agent response payload when available",
    )
    agents_used: List[str] = Field(
        default_factory=list,
        description="Specialized agents that participated in generating the response",
    )
    model_name: Optional[str] = Field(None, description="LLM model identifier used for generation")
    retrieval_metadata: Dict[str, Any] = Field(default_factory=dict, description="Audit retrieval metadata")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution and performance metadata")
    errors: List[str] = Field(default_factory=list, description="Any validation or execution error messages")

