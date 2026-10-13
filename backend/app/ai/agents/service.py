"""
Career Intelligence Service.

Provides unified high-level entry points for executing LangGraph-orchestrated
career intelligence, career recommendations, skill-gap evaluations,
interview preparation, and multi-agent coordinated synthesis across multiple languages.
"""

import logging
from typing import Optional

from app.ai.agents.evaluation_agent import EvaluationAgent, evaluation_agent
from app.ai.agents.interview_agent import InterviewAgent, interview_agent
from app.ai.agents.orchestrator import CareerOrchestrator, career_orchestrator
from app.ai.agents.recommendation_agent import RecommendationAgent, recommendation_agent
from app.schemas.agent import CareerIntelligenceResponse
from app.schemas.interview import InterviewQuestion, InterviewResponse
from app.schemas.multi_agent import MultiAgentResponse
from app.schemas.recommendation import CareerRecommendationResponse
from app.schemas.skill_gap import SkillGapResponse

logger = logging.getLogger("careerverse.ai.agents.service")


def run_career_intelligence(
    candidate_id: int,
    query: str,
    target_role: Optional[str] = None,
    language: Optional[str] = None,
    orchestrator: Optional[CareerOrchestrator] = None,
) -> CareerIntelligenceResponse:
    """
    Executes the LangGraph Career Intelligence workflow for a candidate and query.
    Automatically detects intent and language, and routes between general RAG, Recommendation Agent,
    Evaluation / Skill-Gap Agent, Interview Agent, and Multi-Agent Synthesis.

    Args:
        candidate_id: Integer candidate user ID
        query: Natural-language query from the candidate
        target_role: Optional explicit target role string
        language: Optional explicit response language code (e.g., 'en', 'ta', 'hi')
        orchestrator: Optional custom CareerOrchestrator instance (defaults to singleton)

    Returns:
        CareerIntelligenceResponse containing the orchestrated outcome
    """
    engine = orchestrator or career_orchestrator
    logger.info(
        "Invoking LangGraph Career Intelligence for Candidate ID: %s, Query: '%s', Target Role: '%s', Language: '%s'",
        candidate_id,
        str(query)[:40],
        target_role,
        language,
    )

    final_state = engine.run(
        candidate_id=candidate_id,
        query=query,
        target_role=target_role,
        language=language,
    )

    retrieval_status = "not_executed"
    if (
        final_state.get("retrieved_context") is not None
        or final_state.get("recommendation_response") is not None
        or final_state.get("evaluation_response") is not None
        or final_state.get("interview_response") is not None
        or final_state.get("multi_agent_response") is not None
    ):
        retrieval_status = "success"
    elif any("retrieval" in err.lower() for err in final_state.get("errors", [])):
        retrieval_status = "failed"
    elif final_state.get("status") == "validation_failed":
        retrieval_status = "skipped"

    generated_answer = final_state.get("generated_answer") or ""
    if not generated_answer and final_state.get("errors"):
        generated_answer = f"Error: {'; '.join(final_state['errors'])}"

    rec_response: Optional[CareerRecommendationResponse] = final_state.get("recommendation_response")
    recommendations_list = rec_response.recommendations if rec_response else []
    eval_response: Optional[SkillGapResponse] = final_state.get("evaluation_response")
    int_response: Optional[InterviewResponse] = final_state.get("interview_response")
    interview_questions_list = int_response.questions if int_response else []
    multi_response: Optional[MultiAgentResponse] = final_state.get("multi_agent_response")
    agents_used = final_state.get("agents_used", [])

    response_lang = final_state.get("response_language") or "en"
    lang_metadata = final_state.get("language_metadata")

    return CareerIntelligenceResponse(
        candidate_id=final_state.get("candidate_id"),
        query=final_state.get("user_query", query),
        language=response_lang,
        language_metadata=lang_metadata,
        intent=final_state.get("intent", "unknown"),
        target_role=final_state.get("target_role"),
        status=final_state.get("status", "unknown"),
        retrieval_status=retrieval_status,
        generated_answer=generated_answer,
        recommendations=recommendations_list,
        recommendation_details=rec_response,
        evaluation_details=eval_response,
        interview_questions=interview_questions_list,
        interview_details=int_response,
        multi_agent_details=multi_response,
        agents_used=agents_used,
        model_name=final_state.get("model_name"),
        retrieval_metadata=final_state.get("retrieval_metadata", {}),
        metadata=final_state.get("metadata", {}),
        errors=final_state.get("errors", []),
    )


def run_multi_agent_career_intelligence(
    candidate_id: int,
    query: str,
    target_role: Optional[str] = None,
    language: Optional[str] = None,
    orchestrator: Optional[CareerOrchestrator] = None,
) -> MultiAgentResponse:
    """
    Executes the multi-agent coordination workflow and returns a structured MultiAgentResponse.

    Args:
        candidate_id: Integer candidate user ID
        query: User query (e.g. combined career planning question)
        target_role: Optional explicit target job role
        language: Optional explicit target language override
        orchestrator: Optional custom CareerOrchestrator instance

    Returns:
        MultiAgentResponse with synthesized summary, recommendations, skill gaps, interview prep, and guidance
    """
    engine = orchestrator or career_orchestrator
    final_state = engine.run(
        candidate_id=candidate_id,
        query=query,
        target_role=target_role,
        language=language,
    )

    multi_res: Optional[MultiAgentResponse] = final_state.get("multi_agent_response")
    if multi_res is not None:
        return multi_res

    # Fallback if graph exited early or failed validation
    rec_res = final_state.get("recommendation_response")
    eval_res = final_state.get("evaluation_response")
    int_res = final_state.get("interview_response")
    status = final_state.get("status", "completed")
    errors = final_state.get("errors", [])
    answer = final_state.get("generated_answer") or (f"Error: {'; '.join(errors)}" if errors else "")
    response_lang = final_state.get("response_language") or "en"
    lang_metadata = final_state.get("language_metadata")

    return MultiAgentResponse(
        candidate_id=final_state.get("candidate_id"),
        query=final_state.get("user_query", query),
        language=response_lang,
        language_metadata=lang_metadata,
        target_role=final_state.get("target_role"),
        agents_used=final_state.get("agents_used", []),
        summary=answer,
        recommendations=rec_res.recommendations if rec_res else [],
        recommendation_details=rec_res,
        skill_gaps=eval_res.skill_gaps if eval_res else [],
        evaluation_details=eval_res,
        interview_preparation=int_res.questions if int_res else [],
        interview_details=int_res,
        final_guidance="",
        evidence={},
        agent_results=final_state.get("agent_results", {}),
        model_name=final_state.get("model_name"),
        status=status,
        errors=errors,
    )


def run_interview_preparation(
    candidate_id: int,
    query: Optional[str] = None,
    target_role: Optional[str] = None,
    language: Optional[str] = None,
    orchestrator: Optional[CareerOrchestrator] = None,
) -> InterviewResponse:
    """
    Convenience wrapper to run personalized interview preparation via LangGraph.
    """
    effective_query = query or (
        f"Prepare me for a {target_role} interview." if target_role else "Give me personalized interview questions based on my profile."
    )
    ci_res = run_career_intelligence(
        candidate_id=candidate_id,
        query=effective_query,
        target_role=target_role,
        language=language,
        orchestrator=orchestrator,
    )

    if ci_res.interview_details:
        return ci_res.interview_details

    return InterviewResponse(
        candidate_id=candidate_id,
        target_role=target_role,
        query=effective_query,
        interview_mode="general",
        questions=[],
        preparation_summary=ci_res.generated_answer,
        model_name=ci_res.model_name,
        status=ci_res.status,
        errors=ci_res.errors,
    )


run_mock_interview = run_interview_preparation


def run_career_recommendation(
    candidate_id: int,
    query: str,
    language: Optional[str] = None,
    orchestrator: Optional[CareerOrchestrator] = None,
) -> CareerIntelligenceResponse:
    """
    Convenience wrapper to run career role recommendation via LangGraph.
    """
    return run_career_intelligence(
        candidate_id=candidate_id,
        query=query,
        language=language,
        orchestrator=orchestrator,
    )


def run_skill_gap_evaluation(
    candidate_id: int,
    target_role: str,
    query: Optional[str] = None,
    language: Optional[str] = None,
    orchestrator: Optional[CareerOrchestrator] = None,
) -> SkillGapResponse:
    """
    Convenience wrapper to run structured skill-gap evaluation via LangGraph.
    """
    effective_query = query or f"What skills am I missing for a {target_role} role?"
    ci_res = run_career_intelligence(
        candidate_id=candidate_id,
        query=effective_query,
        target_role=target_role,
        language=language,
        orchestrator=orchestrator,
    )

    if ci_res.evaluation_details:
        return ci_res.evaluation_details

    return SkillGapResponse(
        candidate_id=candidate_id,
        target_role=target_role,
        query=effective_query,
        strengths=[],
        skill_gaps=[],
        summary=ci_res.generated_answer,
        improvement_areas=[],
        model_name=ci_res.model_name,
        status=ci_res.status,
        errors=ci_res.errors,
    )


run_career_evaluation = run_skill_gap_evaluation

