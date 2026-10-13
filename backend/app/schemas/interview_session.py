from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


INTERVIEW_MODES = {
    "general",
    "target_role",
    "project",
    "skill",
    "skill_gap",
    "technical",
    "dsa",
    "database",
    "sql",
    "backend",
    "system_design",
    "frontend",
    "behavioral",
    "github",
    "comprehensive",
}
SUPPORTED_LANGUAGES = {"en", "ta", "hi", "es", "fr", "de", "te", "kn"}


class InterviewSessionCreateRequest(BaseModel):
    target_role: Optional[str] = Field(None, max_length=200)
    interview_mode: str = Field("general", min_length=2, max_length=30)
    focus_topic: Optional[str] = Field(None, max_length=200)
    language: str = Field("en", min_length=2, max_length=5)

    @field_validator("interview_mode")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in INTERVIEW_MODES:
            raise ValueError(f"interview_mode must be one of: {', '.join(sorted(INTERVIEW_MODES))}")
        return value

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in SUPPORTED_LANGUAGES:
            raise ValueError(f"language must be one of: {', '.join(sorted(SUPPORTED_LANGUAGES))}")
        return value

    @field_validator("target_role")
    @classmethod
    def normalize_role(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        return value or None


class InterviewAnswerRequest(BaseModel):
    answer: str = Field(..., min_length=1, max_length=10000)
    code: Optional[str] = None
    language: Optional[str] = None
    focus_topic: Optional[str] = None

    @field_validator("answer")
    @classmethod
    def answer_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("answer must not be blank")
        return value.strip()

    @field_validator("language")
    @classmethod
    def validate_answer_language(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        v = value.strip().lower()
        return v if v in SUPPORTED_LANGUAGES else "en"


class InterviewQuestionPayload(BaseModel):
    question: str
    question_id: Optional[str] = None
    session_id: Optional[str] = None
    track: Optional[str] = None
    question_text: Optional[str] = None
    question_type: str = "technical"
    difficulty: str = "medium"
    topic: str = "Technical Assessment"
    rationale: str = "Grounded in the candidate context and interview transcript."
    evidence_source: Optional[str] = "Unified Candidate Evidence"
    evidence_sources: Optional[List[str]] = Field(default_factory=list)
    source_ids: Optional[List[str]] = Field(default_factory=list)
    source_detail: Optional[str] = None
    language: Optional[str] = "en"
    follow_up_of: Optional[str] = None
    expected_concepts: Optional[List[str]] = Field(default_factory=list)
    normalized_concept: Optional[str] = None
    constraints: Optional[List[str]] = Field(default_factory=list)
    examples: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    hints: Optional[List[str]] = Field(default_factory=list)
    related_files: Optional[List[Union[str, Dict[str, Any]]]] = Field(default_factory=list)
    repository_context: Optional[Dict[str, Any]] = None
    suggested_points: Optional[List[str]] = Field(default_factory=list)
    test_cases: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    follow_ups: Optional[List[str]] = Field(default_factory=list)
    category: Optional[str] = None
    star_framework: Optional[Dict[str, str]] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.question_text and self.question:
            self.question_text = self.question
        elif not self.question and self.question_text:
            self.question = self.question_text
        if not self.evidence_sources and self.evidence_source:
            self.evidence_sources = [self.evidence_source]


class InterviewSessionSummaryResponse(BaseModel):
    session_id: str
    candidate_id: int
    target_role: Optional[str] = None
    interview_mode: str
    focus_topic: Optional[str] = None
    language: str
    question_count: int = 0
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    concepts_covered: List[str] = Field(default_factory=list)
    candidate_response_summary: Optional[str] = None
    evidence_sources: List[str] = Field(default_factory=list)
    recommendation: Optional[str] = None


class InterviewAnswerEvaluation(BaseModel):
    assessment: str = Field(default="Clear and relevant answer grounded in candidate experience.")
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    follow_up_reason: str = Field(default="Probe deeper into practical implementation and architecture decisions.")
    how_to_explain: Optional[str] = Field(default="Structure your answer by first stating the architectural challenge, detailing your chosen approach and trade-offs, and concluding with measurable outcomes.", description="Guidance on how the candidate should explain this to the interviewer")
    ideal_pitch_script: Optional[str] = Field(default=None, description="Model verbatim pitch script for the candidate")
    missing_elements: List[str] = Field(default_factory=list, description="Key concepts or metrics the candidate omitted")
    structural_framework: Optional[str] = Field(default="STAR / Architecture-Tradeoff Method", description="Recommended explanation framework")


class InterviewTranscriptEntry(BaseModel):
    question_number: int
    question: InterviewQuestionPayload
    answer: str
    evaluation: InterviewAnswerEvaluation
    created_at: datetime


class InterviewFinalReport(BaseModel):
    questions_asked: List[InterviewQuestionPayload] = Field(default_factory=list)
    candidate_answers: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    skill_areas_demonstrated: List[str] = Field(default_factory=list)
    unanswered_or_weak_areas: List[str] = Field(default_factory=list)
    overall_interview_summary: str = Field(default="The candidate demonstrated solid foundational knowledge and practical project competencies.")
    recommended_preparation_areas: List[str] = Field(default_factory=list)


class InterviewSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: str
    candidate_id: int
    target_role: Optional[str] = None
    interview_mode: str
    focus_topic: Optional[str] = None
    language: str
    current_question: Optional[InterviewQuestionPayload] = None
    question_number: int
    transcript: List[InterviewTranscriptEntry] = Field(default_factory=list)
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    latest_evaluation: Optional[InterviewAnswerEvaluation] = None
    final_report: Optional[InterviewFinalReport] = None


class InterviewSessionState(InterviewSessionResponse):
    """Internal response alias retained for service readability."""

    pass