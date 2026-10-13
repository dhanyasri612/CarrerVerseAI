"""
State definition for CareerVerse AI LangGraph agents.

Defines the shared typed state dictionary flowing across workflow nodes:
- request_processor (validation & intent/target-role extraction)
- task_router (deterministic multi-agent task planning)
- recommendation_node (career recommendations)
- evaluation_node (evaluation / skill gap)
- interview_node (personalized interview preparation)
- context_aggregator (combines candidate & agent outputs)
- synthesis_node (multi-agent synthesis & final unified guidance)
- rag_retrieval -> response_generation (general career intelligence RAG fallback)
"""

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
from app.schemas.rag import RAGRetrievedContext
from app.schemas.recommendation import CareerRecommendationResponse
from app.schemas.skill_gap import SkillGapResponse
from app.schemas.interview import InterviewResponse
from app.schemas.multi_agent import MultiAgentResponse


class CareerIntelligenceState(TypedDict, total=False):
    """
    Typed state container for CareerVerse AI multi-agent workflow.
    Adheres to LangGraph state standards.
    """
    candidate_id: int
    user_query: str
    original_query: str
    normalized_query: Optional[str]
    detected_language: str
    language_name: str
    language_confidence: float
    response_language: str
    language_metadata: Dict[str, Any]
    target_role: Optional[str]
    intent: str
    tasks: List[str]
    retrieved_context: Optional[RAGRetrievedContext]
    generated_answer: Optional[str]
    recommendation_response: Optional[CareerRecommendationResponse]
    evaluation_response: Optional[SkillGapResponse]
    interview_response: Optional[InterviewResponse]
    multi_agent_response: Optional[MultiAgentResponse]
    agent_results: Dict[str, Any]
    aggregated_context: Optional[Dict[str, Any]]
    agents_used: List[str]
    model_name: Optional[str]
    retrieval_metadata: Dict[str, Any]
    status: str
    metadata: Dict[str, Any]
    errors: List[str]

