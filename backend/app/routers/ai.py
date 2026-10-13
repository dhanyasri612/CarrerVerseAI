from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.errors import (
    AIConfigurationError,
    AIInvalidResponseError,
    AIProviderAuthenticationError,
    AIProviderError,
    AIProviderTimeoutError,
)
from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.ai import AITestRequest, AITestResponse
from app.schemas.resume_ai import ResumeAIAnalysis
from app.schemas.skill_gap_ai import SkillGapAnalysis, SkillGapRequest
from app.schemas.teaching import (
    TeachingEvaluationRequest,
    TeachingInteractionRequest,
    TeachingInteractionResponse,
    TeachingProgressResponse,
    SkillLearningPathResponse,
    ProjectLearningJourneyResponse,
    RepositoryUnderstandingModel,
    TeachingChatRequest,
    TeachingChatResponse,
)
from app.services.skill_gap_ai_service import analyze_skill_gap_with_roadmap
from app.services.resume_ai_service import analyze_resume_intelligence


router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/test", response_model=AITestResponse, status_code=status.HTTP_200_OK)
def test_ai(request: AITestRequest, _: User = Depends(get_current_user)) -> AITestResponse:
    from app.services.ai_service import ai_service

    try:
        result, model = ai_service.test(request.message)
        return AITestResponse(success=result.success, message=result.message, model=model)
    except AIConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AIProviderAuthenticationError as exc:
        raise HTTPException(status_code=502, detail="AI provider authentication failed") from exc
    except AIProviderTimeoutError as exc:
        raise HTTPException(status_code=504, detail="AI provider request timed out") from exc
    except AIInvalidResponseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail="AI provider request failed") from exc


@router.post(
    "/resume/{resume_id}/analyze",
    response_model=ResumeAIAnalysis,
    status_code=status.HTTP_200_OK,
    summary="Analyze a user's resume with evidence-based AI intelligence",
)
def analyze_resume_ai_endpoint(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return analyze_resume_intelligence(db=db, current_user=current_user, resume_id=resume_id)
    except HTTPException:
        raise
    except AIConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AIProviderAuthenticationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except AIProviderTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except AIInvalidResponseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post(
    "/skill-gap/analyze",
    response_model=SkillGapAnalysis,
    status_code=status.HTTP_200_OK,
    summary="Analyze evidence-based skill gaps and generate a personalized roadmap",
)
def analyze_skill_gap_ai_endpoint(
    request: SkillGapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return analyze_skill_gap_with_roadmap(
            db=db,
            current_user=current_user,
            request=request,
        )
    except HTTPException:
        raise
    except AIConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AIProviderAuthenticationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except AIProviderTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except AIInvalidResponseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# =============================================================================
# Phase 7 — LangGraph Career AI Endpoints
# These endpoints expose the complete Phase 1–6 AI architecture through FastAPI.
# The authenticated user's ID is used as candidate_id — no frontend-supplied ID.
# =============================================================================

from app.schemas.career_ai import (
    CareerIntelligenceRequest,
    CareerInterviewRequest,
    CareerRecommendationRequest,
    CareerSkillGapRequest,
)
from app.schemas.agent import CareerIntelligenceResponse
from app.schemas.skill_gap import SkillGapResponse
from app.schemas.interview import InterviewResponse
from app.schemas.multi_agent import MultiAgentResponse
from app.schemas.rag import RAGGenerationResponse, RAGRequest
from app.schemas.interview_session import (
    InterviewAnswerRequest,
    InterviewSessionCreateRequest,
    InterviewSessionResponse,
    InterviewSessionSummaryResponse,
)
from app.ai.agents.service import (
    run_career_recommendation,
    run_skill_gap_evaluation,
    run_interview_preparation,
    run_multi_agent_career_intelligence,
)
from app.ai.rag.generator import rag_generator
from app.services.conversational_interview_service import (
    InterviewSessionNotFound,
    InterviewSessionStateError,
    complete_interview_session,
    create_interview_session,
    get_candidate_connected_resources,
    get_candidate_interview_sessions,
    get_candidate_question_history,
    get_interview_session,
    submit_interview_answer,
    update_session_language,
)
from app.schemas.profile_quiz import QuizAnswerRequest, QuizSessionCreateRequest, QuizSessionResponse
from app.services.profile_quiz_service import (
    QuizSessionNotFound,
    QuizSessionStateError,
    answer_quiz_question,
    complete_quiz,
    create_quiz_session,
    get_quiz_session,
)


def _handle_ai_error(exc: Exception) -> HTTPException:
    """
    Maps AI-layer exceptions to clean HTTP responses without exposing internals.
    """
    import socket
    import urllib.error
    from app.ai.errors import (
        AIConfigurationError,
        AIProviderAuthenticationError,
        AIProviderTimeoutError,
        AIProviderRateLimitError,
        AIInvalidResponseError,
        AIProviderError,
    )
    if isinstance(exc, AIConfigurationError):
        return HTTPException(status_code=503, detail="CareerVerse AI service is not configured correctly.")
    if isinstance(exc, AIProviderAuthenticationError):
        return HTTPException(status_code=502, detail="AI provider authentication failed.")
    if isinstance(exc, (AIProviderTimeoutError, TimeoutError, socket.timeout)):
        return HTTPException(status_code=504, detail="CareerVerse AI took too long to respond. Please retry.")
    if isinstance(exc, (ConnectionError, ConnectionRefusedError, urllib.error.URLError)):
        return HTTPException(status_code=503, detail="CareerVerse AI service is temporarily offline or unavailable. Please retry.")
    if isinstance(exc, AIProviderRateLimitError):
        return HTTPException(status_code=429, detail="AI provider rate limit reached. Please retry later.")
    if isinstance(exc, AIInvalidResponseError):
        return HTTPException(status_code=502, detail="AI provider returned an unprocessable response.")
    if isinstance(exc, AIProviderError):
        return HTTPException(status_code=502, detail="AI provider request failed.")
    return HTTPException(status_code=503, detail="CareerVerse AI is temporarily unavailable. Please retry in a moment.")


@router.post(
    "/rag",
    response_model=RAGGenerationResponse,
    status_code=status.HTTP_200_OK,
    summary="Answer a candidate question using grounded profile retrieval",
    description=(
        "Retrieves only the authenticated candidate's ChromaDB vector and Neo4j graph context, "
        "then generates a grounded response with the configured LLM provider. Retrieval service "
        "availability is returned in retrieval_metadata."
    ),
    responses={
        401: {"description": "Authentication required"},
        422: {"description": "Invalid RAG request"},
        429: {"description": "AI provider rate limit reached"},
        502: {"description": "AI provider error"},
        503: {"description": "AI service not configured"},
        504: {"description": "AI provider timeout"},
    },
)
def grounded_rag_answer(
    request: RAGRequest,
    current_user: User = Depends(get_current_user),
) -> RAGGenerationResponse:
    """Generate a grounded answer for the authenticated candidate only."""
    if not current_user.id or current_user.id <= 0:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    try:
        return rag_generator.generate_response(
            candidate_id=current_user.id,
            query=request.query,
            top_k=request.top_k,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            language=request.language,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.post(
    "/career/recommend",
    response_model=CareerIntelligenceResponse,
    status_code=status.HTTP_200_OK,
    summary="AI Career Role Recommendations",
    description=(
        "Generates grounded, evidence-based career role recommendations for the authenticated candidate "
        "using the LangGraph Recommendation Agent backed by ChromaDB semantic search and Neo4j "
        "Knowledge Graph retrieval. Supports English, Tamil, and Hindi queries."
    ),
    responses={
        400: {"description": "Invalid or empty query"},
        401: {"description": "Authentication required"},
        404: {"description": "Candidate profile not found"},
        422: {"description": "Validation error in request body"},
        429: {"description": "AI provider rate limit reached"},
        502: {"description": "AI provider error"},
        503: {"description": "AI service not configured"},
        504: {"description": "AI provider timeout"},
    },
)
def career_recommend(
    request: CareerRecommendationRequest,
    current_user: User = Depends(get_current_user),
) -> CareerIntelligenceResponse:
    """
    Returns structured career role recommendations for the authenticated user.
    Candidate identity is resolved from the JWT — the frontend does not supply a candidate_id.
    """
    if not current_user.id or current_user.id <= 0:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")
    try:
        return run_career_recommendation(
            candidate_id=current_user.id,
            query=request.query,
            language=request.language,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.post(
    "/career/skill-gap",
    response_model=SkillGapResponse,
    status_code=status.HTTP_200_OK,
    summary="AI Skill-Gap Analysis",
    description=(
        "Evaluates the authenticated candidate's verified skills against a target job role's "
        "requirements using the LangGraph Evaluation Agent. Returns structured strengths, "
        "skill gaps, gap severity, and actionable improvement areas. "
        "target_role is required. Preserves the target_role=None safety behavior — "
        "the agent is never called with an invented role. "
        "Supports English, Tamil, and Hindi."
    ),
    responses={
        400: {"description": "target_role is required or invalid"},
        401: {"description": "Authentication required"},
        404: {"description": "Candidate profile not found"},
        422: {"description": "Validation error in request body"},
        429: {"description": "AI provider rate limit reached"},
        502: {"description": "AI provider error"},
        503: {"description": "AI service not configured"},
        504: {"description": "AI provider timeout"},
    },
)
def career_skill_gap(
    request: CareerSkillGapRequest,
    current_user: User = Depends(get_current_user),
) -> SkillGapResponse:
    """
    Returns a structured skill-gap analysis for the authenticated user vs the target role.
    """
    if not current_user.id or current_user.id <= 0:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")
    try:
        return run_skill_gap_evaluation(
            candidate_id=current_user.id,
            target_role=request.target_role,
            query=request.query,
            language=request.language,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.post(
    "/career/interview",
    response_model=InterviewResponse,
    status_code=status.HTTP_200_OK,
    summary="AI Interview Preparation",
    description=(
        "Generates personalized, evidence-grounded interview questions for the authenticated "
        "candidate using the LangGraph Interview Agent. "
        "Supports five interview modes determined automatically from the query: "
        "general, target_role, project_based, skill_based, skill_gap. "
        "Supports English, Tamil, and Hindi."
    ),
    responses={
        400: {"description": "Invalid request — query or target_role required"},
        401: {"description": "Authentication required"},
        404: {"description": "Candidate profile not found"},
        422: {"description": "Validation error in request body"},
        429: {"description": "AI provider rate limit reached"},
        502: {"description": "AI provider error"},
        503: {"description": "AI service not configured"},
        504: {"description": "AI provider timeout"},
    },
)
def career_interview(
    request: CareerInterviewRequest,
    current_user: User = Depends(get_current_user),
) -> InterviewResponse:
    """
    Returns structured personalized interview preparation for the authenticated user.
    """
    if not current_user.id or current_user.id <= 0:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    # At least one of query or target_role must be supplied
    if not request.query and not request.target_role:
        raise HTTPException(
            status_code=400,
            detail="Provide at least a 'query' or a 'target_role' for interview preparation.",
        )
    try:
        return run_interview_preparation(
            candidate_id=current_user.id,
            query=request.query,
            target_role=request.target_role,
            language=request.language,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.post(
    "/career/interview/session",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a conversational interview session",
)
def create_conversational_interview_session(
    request: InterviewSessionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewSessionResponse:
    try:
        return create_interview_session(db, current_user, request)
    except InterviewSessionStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.post(
    "/career/interview/session/{session_id}/answer",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit an interview answer and receive a follow-up question",
)
def answer_conversational_interview(
    session_id: str,
    request: InterviewAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewSessionResponse:
    try:
        return submit_interview_answer(db, current_user, session_id, request)
    except InterviewSessionNotFound as exc:
        raise HTTPException(status_code=404, detail="Interview session not found") from exc
    except InterviewSessionStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.get(
    "/career/interview/session/{session_id}",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a conversational interview session",
)
def read_conversational_interview_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewSessionResponse:
    try:
        return get_interview_session(db, current_user, session_id)
    except InterviewSessionNotFound as exc:
        raise HTTPException(status_code=404, detail="Interview session not found") from exc


class UpdateSessionLanguageRequest(BaseModel):
    language: str


@router.patch(
    "/career/interview/session/{session_id}/language",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Update conversational interview session active language",
)
def patch_conversational_interview_language(
    session_id: str,
    body: UpdateSessionLanguageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewSessionResponse:
    try:
        return update_session_language(db, current_user, session_id, body.language)
    except InterviewSessionNotFound as exc:
        raise HTTPException(status_code=404, detail="Interview session not found") from exc
    except InterviewSessionStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.post(
    "/career/interview/session/{session_id}/complete",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete a conversational interview and generate its report",
)
def complete_conversational_interview(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewSessionResponse:
    try:
        return complete_interview_session(db, current_user, session_id)
    except InterviewSessionNotFound as exc:
        raise HTTPException(status_code=404, detail="Interview session not found") from exc
    except InterviewSessionStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.get(
    "/career/interview/sessions",
    response_model=List[InterviewSessionSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get candidate's past and active interview sessions timeline",
)
def read_candidate_interview_sessions(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[InterviewSessionSummaryResponse]:
    try:
        return get_candidate_interview_sessions(db, current_user, limit=limit, offset=offset)
    except Exception as exc:
        raise _handle_ai_error(exc) from exc



@router.get(
    "/career/interview/questions/history",
    status_code=status.HTTP_200_OK,
    summary="Get question history with 30-day cooldown status for spaced repetition",
)
def read_interview_question_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_candidate_question_history(db, current_user, days_cooldown=30)
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.post(
    "/career/interview/cyra-chat",
    status_code=status.HTTP_200_OK,
    summary="Interactive live chat with Cyra AI technical interviewer and mentor",
)
def chat_with_cyra_interviewer(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        from app.schemas.interview import CyraChatRequest
        from app.services.conversational_interview_service import generate_cyra_chat_response
        parsed_req = CyraChatRequest(**payload)
        return generate_cyra_chat_response(parsed_req, current_user)
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.get(
    "/career/interview/resources-and-modes",
    status_code=status.HTTP_200_OK,
    summary="Get candidate connected resources and tailored interview categories",
)
def read_candidate_interview_resources_and_modes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_candidate_connected_resources(db, current_user)
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.get(
    "/career/teaching/curriculum",
    status_code=status.HTTP_200_OK,
    summary="Get personalized 4-section AI Teaching curriculum grounded in candidate resources",
)
def read_teaching_curriculum(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.teaching_service import get_teaching_curriculum
    try:
        return get_teaching_curriculum(db, current_user)
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.post(
    "/career/teaching/evaluate-and-teach",
    status_code=status.HTTP_200_OK,
    summary="Evaluate candidate thought process and provide complete pedagogical teaching lesson with what is right and wrong",
)
def evaluate_candidate_and_teach(
    request: TeachingEvaluationRequest,
    current_user: User = Depends(get_current_user),
):
    from app.services.teaching_service import evaluate_and_teach
    try:
        return evaluate_and_teach(request, current_user)
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.post(
    "/career/teaching/interact",
    response_model=TeachingInteractionResponse,
    status_code=status.HTTP_200_OK,
    summary="Interactive multi-turn Socratic pedagogy for a teaching lesson",
)
def interact_teaching_lesson_endpoint(
    request: TeachingInteractionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TeachingInteractionResponse:
    from app.services.teaching_service import interact_with_teaching_lesson
    try:
        return interact_with_teaching_lesson(db, current_user, request)
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.get(
    "/career/teaching/progress",
    response_model=TeachingProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Get candidate's progress and mastery metrics across all teaching sections",
)
def read_teaching_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TeachingProgressResponse:
    from app.services.teaching_service import get_candidate_teaching_progress
    try:
        return get_candidate_teaching_progress(db, current_user)
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.get(
    "/career/teaching/concept-map",
    status_code=status.HTTP_200_OK,
    summary="Get Neo4j interactive concept map of prerequisites, skills, and project links",
)
def read_teaching_concept_map(
    lesson_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.teaching_service import get_teaching_concept_map
    try:
        return get_teaching_concept_map(db, current_user, lesson_id)
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.get(
    "/career/teaching/knowledge-profile",
    status_code=status.HTTP_200_OK,
    summary="Get verified learner knowledge profile with evidence, prerequisites, and gaps",
)
def read_learner_knowledge_profile_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.learner_knowledge_service import build_learner_knowledge_profile
    try:
        return build_learner_knowledge_profile(db, current_user)
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.get(
    "/career/teaching/skill-path",
    response_model=SkillLearningPathResponse,
    status_code=status.HTTP_200_OK,
    summary="Get 7-stage structured curriculum and diagnostic path for any technical skill",
)
def read_skill_learning_path_endpoint(
    skill: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SkillLearningPathResponse:
    from app.services.skill_learning_service import build_skill_learning_path
    try:
        return build_skill_learning_path(db, skill, current_user)
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.get(
    "/career/teaching/project-path",
    response_model=ProjectLearningJourneyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get personalized 7-stage learning journey and interview prep for a connected repository",
)
def read_project_learning_path_endpoint(
    repository_id: int,
    force_refresh: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectLearningJourneyResponse:
    from app.services.repository_understanding_service import build_project_learning_journey
    try:
        return build_project_learning_journey(db, repository_id, current_user, force_refresh)
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.get(
    "/career/teaching/repository-understanding",
    response_model=RepositoryUnderstandingModel,
    status_code=status.HTTP_200_OK,
    summary="Get 13-point structured architecture and evidence understanding model for a repository",
)
def read_repository_understanding_endpoint(
    repository_id: int,
    force_refresh: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RepositoryUnderstandingModel:
    from app.services.repository_understanding_service import build_repository_understanding
    try:
        return build_repository_understanding(db, repository_id, current_user, force_refresh)
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.post(
    "/career/teaching/chat",
    response_model=TeachingChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Persistent conversational tutor Dr. Cyra Vance with multi-turn Socratic pedagogy and persistence",
)
def chat_with_teaching_mentor_endpoint(
    request: TeachingChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TeachingChatResponse:
    from app.services.teaching_service import chat_with_teaching_mentor
    try:
        return chat_with_teaching_mentor(db, current_user, request)
    except Exception as exc:
        raise _handle_ai_error(exc) from exc






@router.post("/career/quiz/session", response_model=QuizSessionResponse, status_code=status.HTTP_201_CREATED)
def create_profile_quiz_session(
    request: QuizSessionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizSessionResponse:
    try:
        return create_quiz_session(db, current_user, request)
    except QuizSessionStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.get("/career/quiz/session/{session_id}", response_model=QuizSessionResponse)
def read_profile_quiz_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizSessionResponse:
    try:
        return get_quiz_session(db, current_user, session_id)
    except QuizSessionNotFound as exc:
        raise HTTPException(status_code=404, detail="Quiz session not found") from exc


@router.post("/career/quiz/session/{session_id}/answer", response_model=QuizSessionResponse)
def answer_profile_quiz_question(
    session_id: str,
    request: QuizAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizSessionResponse:
    try:
        return answer_quiz_question(db, current_user, session_id, request)
    except QuizSessionNotFound as exc:
        raise HTTPException(status_code=404, detail="Quiz session not found") from exc
    except QuizSessionStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/career/quiz/session/{session_id}/complete", response_model=QuizSessionResponse)
def complete_profile_quiz_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizSessionResponse:
    try:
        return complete_quiz(db, current_user, session_id)
    except QuizSessionNotFound as exc:
        raise HTTPException(status_code=404, detail="Quiz session not found") from exc
    except QuizSessionStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise _handle_ai_error(exc) from exc


@router.post(
    "/career/intelligence",
    response_model=MultiAgentResponse,
    status_code=status.HTTP_200_OK,
    summary="Combined Career Intelligence (Multi-Agent)",
    description=(
        "Runs the complete LangGraph multi-agent orchestration pipeline for the authenticated candidate: "
        "Language Detection → Task Router → Recommendation Agent → Evaluation Agent → "
        "Interview Agent → Context Aggregator → Synthesis Agent → Structured Response. "
        "The task router automatically determines which combination of agents to invoke based on "
        "the query. A single query can trigger recommendation, skill-gap evaluation, and interview "
        "preparation simultaneously. "
        "Supports English, Tamil (தமிழ்), and Hindi (हिन्दी). "
        "This endpoint exposes the complete Phase 5E multi-agent coordination architecture."
    ),
    responses={
        400: {"description": "Invalid or empty query"},
        401: {"description": "Authentication required"},
        404: {"description": "Candidate profile not found"},
        422: {"description": "Validation error in request body"},
        429: {"description": "AI provider rate limit reached"},
        502: {"description": "AI provider error"},
        503: {"description": "AI service not configured"},
        504: {"description": "AI provider timeout"},
    },
)
def career_intelligence(
    request: CareerIntelligenceRequest,
    current_user: User = Depends(get_current_user),
) -> MultiAgentResponse:
    """
    Runs the full multi-agent LangGraph career intelligence pipeline for the authenticated user.
    """
    if not current_user.id or current_user.id <= 0:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")
    try:
        return run_multi_agent_career_intelligence(
            candidate_id=current_user.id,
            query=request.query,
            target_role=request.target_role,
            language=request.language,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_ai_error(exc) from exc
