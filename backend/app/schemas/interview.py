"""
Pydantic schemas for Personalized Interview Preparation Agent.
Includes individual interview question models and structured response containers.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

QuestionType = Literal[
    "technical",
    "project_based",
    "skill_based",
    "role_based",
    "skill_gap",
    "behavioral",
]

DifficultyLevel = Literal[
    "easy",
    "medium",
    "hard",
]


class InterviewQuestion(BaseModel):
    """
    Individual personalized interview preparation question grounded in candidate evidence.
    """
    model_config = ConfigDict(extra="ignore")

    question: str = Field(..., description="The interview question text")
    question_type: str = Field(
        ...,
        description="Category: technical, project_based, skill_based, role_based, skill_gap, behavioral",
    )
    difficulty: str = Field(
        ...,
        description="Assessed difficulty level: easy, medium, hard",
    )
    topic: str = Field(
        ...,
        description="Core subject or domain topic (e.g. Backend Architecture, Concurrency, Docker)",
    )
    rationale: str = Field(
        ...,
        description="Grounded explanation of why this question is recommended based on candidate evidence or target role",
    )
    supporting_skills: List[str] = Field(
        default_factory=list,
        description="Verified candidate skills relevant to this question",
    )
    supporting_projects: List[str] = Field(
        default_factory=list,
        description="Verified candidate projects relevant to this question",
    )
    supporting_technologies: List[str] = Field(
        default_factory=list,
        description="Verified candidate technologies relevant to this question",
    )
    evidence_sources: List[str] = Field(
        default_factory=list,
        description="Data evidence sources (e.g. project, skill, graph, resume, github, skill_gap)",
    )
    source_citations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Fresh technical documentation citations used to ground this question",
    )
    technical_source_status: str = "not_refreshed"


class InterviewResponse(BaseModel):
    """
    Structured interview preparation response containing personalized questions and preparation summary.
    """
    model_config = ConfigDict(extra="ignore")

    candidate_id: Optional[int] = Field(None, description="Candidate ID evaluated")
    target_role: Optional[str] = Field(None, description="Target job role if specified")
    query: str = Field(..., description="Original user interview query")
    interview_mode: Optional[str] = Field(
        None,
        description="Detected interview mode: general, target_role, project, skill, skill_gap",
    )
    questions: List[InterviewQuestion] = Field(
        default_factory=list,
        description="List of personalized grounded interview questions",
    )
    preparation_summary: str = Field(
        ...,
        description="Grounded narrative summary offering strategic preparation advice",
    )
    model_name: Optional[str] = Field(None, description="LLM model identifier used for generation")
    status: str = Field("completed", description="Execution status: completed, invalid_role, validation_failed, failed")
    errors: List[str] = Field(default_factory=list, description="Any validation or execution errors")


class CyraChatRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    message: str = Field(..., description="Candidate's chat message to Cyra")
    current_question: Optional[str] = Field(default="", description="Current technical interview question")
    role: Optional[str] = Field(default="Software Engineer", description="Target job role")
    candidate_code: Optional[str] = Field(default="", description="Candidate's current code snippet")
    action_type: Optional[str] = Field(default="chat", description="chat, hint, constraints, or approach")
    language: Optional[str] = Field(default="en", description="Conversation language (en, ta, hi)")


class CyraChatResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    reply: str = Field(..., description="Cyra's conversational AI response")
    action_type: str = Field(default="chat", description="Echo of action type")
    suggested_followups: List[str] = Field(default_factory=list, description="Dynamic suggested quick questions")

