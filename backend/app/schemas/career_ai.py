"""
Phase 7 — Request schemas for the LangGraph Career AI endpoints.

These models define what the frontend sends to each /ai/career/* endpoint.
All response schemas are reused from existing Phase 5/6 schemas.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CareerRecommendationRequest(BaseModel):
    """
    Request body for /ai/career/recommend.
    The authenticated user's candidate_id is resolved server-side from the JWT;
    the frontend only supplies the query and an optional language override.
    """
    query: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description=(
            "Natural-language career question, e.g. "
            "'What roles suit my skills?' or 'எனக்கு பொருத்தமான roles என்ன?'"
        ),
    )
    language: Optional[str] = Field(
        None,
        min_length=2,
        max_length=5,
        description=(
            "Optional explicit response language code ('en', 'ta', 'hi'). "
            "When omitted, language is auto-detected from the query."
        ),
    )

    @field_validator("query")
    @classmethod
    def query_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query must not be blank or whitespace only")
        return v


class CareerSkillGapRequest(BaseModel):
    """
    Request body for /ai/career/skill-gap.
    target_role is required: the Evaluation Agent performs role-specific gap analysis.
    Preserves the existing target_role=None safety behavior — if omitted or blank the
    backend returns 422 before calling the agent so the agent never receives None
    accidentally from the API layer.
    """
    target_role: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description=(
            "Target job role for skill-gap analysis, e.g. 'Backend Developer', "
            "'Machine Learning Engineer'."
        ),
    )
    query: Optional[str] = Field(
        None,
        max_length=2000,
        description=(
            "Optional natural-language question to customise the evaluation narrative. "
            "Defaults to a standard skill-gap query for the role if omitted."
        ),
    )
    language: Optional[str] = Field(
        None,
        min_length=2,
        max_length=5,
        description="Optional response language override ('en', 'ta', 'hi').",
    )

    @field_validator("target_role")
    @classmethod
    def role_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("target_role must not be blank")
        return v.strip()


class CareerInterviewRequest(BaseModel):
    """
    Request body for /ai/career/interview.
    Supports all existing interview modes: general, target_role, project, skill, skill_gap.
    The mode is determined deterministically by the Interview Agent from the query text.
    """
    query: Optional[str] = Field(
        None,
        max_length=2000,
        description=(
            "Natural-language interview request. "
            "Examples: 'Prepare me for a Backend Developer interview', "
            "'Ask me questions about my projects'. "
            "If omitted, defaults to a general interview for target_role (if supplied)."
        ),
    )
    target_role: Optional[str] = Field(
        None,
        max_length=200,
        description=(
            "Optional target job role to focus interview preparation, "
            "e.g. 'Backend Developer'. Supports all roles in the role registry."
        ),
    )
    language: Optional[str] = Field(
        None,
        min_length=2,
        max_length=5,
        description="Optional response language override ('en', 'ta', 'hi').",
    )

    @field_validator("query")
    @classmethod
    def query_not_blank_if_present(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("query must not be blank if provided")
        return v


class CareerIntelligenceRequest(BaseModel):
    """
    Request body for /ai/career/intelligence (full multi-agent orchestration).
    Submits the query to the complete LangGraph pipeline:
    Language Detection → Task Router → Recommendation / Evaluation / Interview Agents
    → Context Aggregator → Synthesis Agent → Structured MultiAgentResponse.
    """
    query: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description=(
            "Full natural-language career intelligence request. "
            "The task router automatically determines which agents to invoke. "
            "Examples: "
            "'Recommend roles, evaluate my gaps for Backend Developer, and generate interview questions.' "
            "'எனக்கு ஏற்ற career roles மற்றும் interview questions பரிந்துரை செய்.' "
            "'मेरे लिए career roles और skill gaps बताओ.'"
        ),
    )
    target_role: Optional[str] = Field(
        None,
        max_length=200,
        description=(
            "Optional explicit target role override. "
            "When supplied, overrides any role detected from the query text."
        ),
    )
    language: Optional[str] = Field(
        None,
        min_length=2,
        max_length=5,
        description=(
            "Optional response language override ('en', 'ta', 'hi'). "
            "Auto-detected from query when omitted."
        ),
    )

    @field_validator("query")
    @classmethod
    def query_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query must not be blank or whitespace only")
        return v
