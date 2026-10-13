from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class QuizQuestion(BaseModel):
    id: str
    question: str
    question_type: str = "single"
    options: List[str] = Field(default_factory=list)
    why_it_matters: str = ""


class QuizAnswerRequest(BaseModel):
    answer: str = Field(..., min_length=1, max_length=4000)


class QuizResult(BaseModel):
    career_direction: str
    summary: str
    career_paths: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    skills_to_develop: List[str] = Field(default_factory=list)
    recommended_next_steps: List[str] = Field(default_factory=list)


class QuizSessionCreateRequest(BaseModel):
    language: str = Field("en", min_length=2, max_length=5)


class QuizSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: str
    candidate_id: int
    language: str
    questions: List[QuizQuestion] = Field(default_factory=list)
    current_question: Optional[QuizQuestion] = None
    question_number: int
    answers: List[Dict[str, Any]] = Field(default_factory=list)
    status: str
    result: Optional[QuizResult] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
