from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

class IncorrectStatement(BaseModel):
    statement: str = Field(..., description="Incorrect statement made by the candidate")
    explanation: str = Field(..., description="Explanation why the statement is incorrect")


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
    "hackerrank",
    "resume",
}
SUPPORTED_LANGUAGES = {"en", "ta", "hi", "es", "fr", "de", "te", "kn", "ml"}


class InterviewSessionCreateRequest(BaseModel):
    target_role: Optional[str] = Field(None, max_length=200)
    interview_mode: str = Field("general", min_length=2, max_length=30)
    focus_topic: Optional[str] = Field(None, max_length=200)
    language: str = Field("en", min_length=2, max_length=5)
    repository_id: Optional[int] = None
    session_mode: Optional[str] = Field("fresh", description="fresh | revision | mock_exam")
    total_core_questions: int = Field(5, ge=1, le=15)

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
        # Normalize: lower case, strip, and handle regional variants like 'ta-IN'
        v = value.strip().lower()
        if "-" in v:
            v = v.split("-")[0]
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"language must be one of: {', '.join(sorted(SUPPORTED_LANGUAGES))}")
        return v

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
        if "-" in v:
            v = v.split("-")[0]
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"language must be one of: {', '.join(sorted(SUPPORTED_LANGUAGES))}")
        return v


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
    source_citations: List[Dict[str, Any]] = Field(default_factory=list)
    technical_source_status: str = "not_refreshed"
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
    core_question_index: Optional[int] = 1
    total_core_questions: int = 5
    is_follow_up: bool = False
    follow_up_of_core: Optional[int] = None
    competency_phase: Optional[str] = "Project Architecture & Understanding"
    repository_citations: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_status: Optional[str] = "grounded"

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
    overall_score: Optional[float] = None
    average_question_score: Optional[float] = None


class InterviewAnswerEvaluation(BaseModel):
    assessment: str = Field(default="Clear and relevant answer grounded in candidate experience.")
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    follow_up_reason: str = Field(default="Probe deeper into practical implementation and architecture decisions.")
    how_to_explain: Optional[str] = Field(default="Structure your answer by first stating the architectural challenge, detailing your chosen approach and trade-offs, and concluding with measurable outcomes.", description="Guidance on how the candidate should explain this to the interviewer")
    ideal_pitch_script: Optional[str] = Field(default=None, description="Model verbatim pitch script for the candidate")
    missing_elements: List[str] = Field(default_factory=list, description="Key concepts or metrics the candidate omitted")
    structural_framework: Optional[str] = Field(default="STAR / Architecture-Tradeoff Method", description="Recommended explanation framework")
    # New detailed feedback fields
    incorrect_statements: List[IncorrectStatement] = Field(default_factory=list, description="List of statements the candidate got wrong with explanations")
    key_takeaways: List[str] = Field(default_factory=list, description="Concise takeaways for the candidate")
    rubric_scores: Optional[Dict[str, int]] = Field(default_factory=dict)
    score: Optional[int] = None
    evaluation_status: str = Field(default="evaluated", description="'evaluated' | 'provisional' | 'unavailable'")
    is_follow_up_needed: bool = False
    follow_up_question_prompt: Optional[str] = None


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
    overall_score: Optional[float] = Field(default=None, description="Auditable overall score out of 10")
    average_question_score: Optional[float] = Field(default=None, description="Average across question rubric evaluations")
    relevance_score: Optional[float] = Field(default=None, description="Average relevance score out of 10")
    duration_seconds: Optional[int] = Field(default=None, description="Session total duration in seconds")
    competency_scores: Dict[str, float] = Field(default_factory=dict, description="Breakdown by competency dimension")
    question_evaluations: List[Dict[str, Any]] = Field(default_factory=list, description="Auditable question-level evaluation details")
    session_id: Optional[str] = None
    evaluated_at: Optional[datetime] = None


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
    core_question_number: int = 1
    total_core_questions: int = 5
    is_follow_up: bool = False
    session_mode: Optional[str] = "fresh"
    transcript: List[InterviewTranscriptEntry] = Field(default_factory=list)
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    latest_evaluation: Optional[InterviewAnswerEvaluation] = None
    evaluation: Optional[InterviewAnswerEvaluation] = None
    feedback: Optional[InterviewAnswerEvaluation] = None
    final_report: Optional[InterviewFinalReport] = None


class InterviewSessionState(InterviewSessionResponse):
    """Internal response alias retained for service readability."""

    pass

# Interview booklet models
class InterviewBookletQuestionEntry(BaseModel):
    sequence_number: int
    question: InterviewQuestionPayload
    answer: Optional[str] = None
    unanswered: bool = True
    skipped: bool = False
    evaluation: Optional[InterviewAnswerEvaluation] = None
    incorrect_statement_explanations: Optional[List[str]] = None
    takeaways: Optional[List[str]] = None

class InterviewBookletResponse(BaseModel):
    session_id: str
    candidate_id: int
    interview_mode: str
    language: str
    status: str
    overall_interview_summary: str
    question_count: int
    spreads: List[InterviewBookletQuestionEntry]