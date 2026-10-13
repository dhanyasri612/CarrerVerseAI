"""
Context Aggregator for CareerVerse AI Multi-Agent System.

Fuses candidate multi-modal graph context, semantic search evidence, and structured
outputs from specialized agents (Recommendation, Skill-Gap Evaluation, Interview Preparation)
into a unified aggregated context payload for the Final Synthesis Agent.
"""

import logging
from typing import Any, Dict, List, Optional

from app.ai.knowledge_graph.graph_queries import (
    GraphQueryService,
    graph_query_service,
)
from app.ai.rag.context_builder import RAGContextBuilder, rag_context_builder
from app.schemas.interview import InterviewResponse
from app.schemas.rag import RAGRetrievedContext
from app.schemas.recommendation import CareerRecommendationResponse
from app.schemas.skill_gap import SkillGapResponse

logger = logging.getLogger("careerverse.ai.agents.context_aggregator")


class ContextAggregator:
    """
    Combines candidate profile evidence with specialized agent results.
    Does not duplicate raw data unnecessarily; produces a clean, structured
    aggregation for multi-agent synthesis.
    """

    def __init__(
        self,
        context_builder: RAGContextBuilder = rag_context_builder,
        graph_queries: GraphQueryService = graph_query_service,
    ):
        self.context_builder = context_builder
        self.graph_queries = graph_queries

    def aggregate(
        self,
        candidate_id: int,
        user_query: str,
        target_role: Optional[str] = None,
        tasks: Optional[List[str]] = None,
        recommendation_response: Optional[CareerRecommendationResponse] = None,
        evaluation_response: Optional[SkillGapResponse] = None,
        interview_response: Optional[InterviewResponse] = None,
        agent_results: Optional[Dict[str, Any]] = None,
        retrieved_context: Optional[RAGRetrievedContext] = None,
        errors: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Builds a comprehensive structured dictionary aggregating all available evidence
        and specialized agent outputs.
        """
        logger.info(
            "ContextAggregator: Aggregating context for Candidate ID %d, Target Role: '%s'",
            candidate_id,
            target_role,
        )

        effective_tasks = tasks or []
        accumulated_errors = list(errors or [])

        # 1. Fetch or build retrieval context if not present
        effective_context = retrieved_context
        if effective_context is None and candidate_id > 0:
            try:
                effective_context = self.context_builder.build_retrieval_context(
                    candidate_id=candidate_id,
                    query=user_query,
                    top_k=5,
                )
            except Exception as exc:
                logger.warning("ContextAggregator: RAG retrieval issue: %s", str(exc))

        # 2. Extract verified candidate facts from graph
        candidate_profile: Dict[str, Any] = {
            "skills": [],
            "projects": [],
            "technologies": [],
            "experience": [],
            "certifications": [],
            "education": [],
        }

        if candidate_id > 0:
            try:
                skills = self.graph_queries.get_candidate_skills(candidate_id)
                projects = self.graph_queries.get_candidate_projects(candidate_id)
                techs = self.graph_queries.get_candidate_technologies(candidate_id)
                exp = self.graph_queries.get_candidate_experience(candidate_id)
                certs = self.graph_queries.get_candidate_certifications(candidate_id)
                edu = self.graph_queries.get_candidate_education(candidate_id)

                candidate_profile["skills"] = [
                    getattr(s, "name", None) or (s["name"] if isinstance(s, dict) else str(s))
                    for s in skills
                ]
                candidate_profile["projects"] = [
                    getattr(p, "title", None) or getattr(p, "name", None) or (p.get("title") if isinstance(p, dict) else (p.get("name") if isinstance(p, dict) else str(p)))
                    for p in projects
                ]
                candidate_profile["technologies"] = [
                    getattr(t, "name", None) or (t["name"] if isinstance(t, dict) else str(t))
                    for t in techs
                ]
                candidate_profile["experience"] = [
                    getattr(e, "company", None) or (e["company"] if isinstance(e, dict) else str(e))
                    for e in exp
                ]
                candidate_profile["certifications"] = [
                    getattr(c, "name", None) or (c["name"] if isinstance(c, dict) else str(c))
                    for c in certs
                ]
                candidate_profile["education"] = [
                    getattr(ed, "degree", None) or (ed["degree"] if isinstance(ed, dict) else str(ed))
                    for ed in edu
                ]
            except Exception as exc:
                logger.warning("ContextAggregator: Graph query issue: %s", str(exc))

        # 3. Format structured agent responses
        rec_data = None
        if recommendation_response is not None:
            rec_data = {
                "status": recommendation_response.status,
                "recommendations": [r.model_dump() for r in recommendation_response.recommendations],
                "explanation": recommendation_response.explanation,
                "evidence": recommendation_response.evidence,
                "errors": recommendation_response.errors,
            }

        eval_data = None
        if evaluation_response is not None:
            eval_data = {
                "status": evaluation_response.status,
                "target_role": evaluation_response.target_role,
                "strengths": evaluation_response.strengths,
                "skill_gaps": [g.model_dump() for g in evaluation_response.skill_gaps],
                "summary": evaluation_response.summary,
                "improvement_areas": evaluation_response.improvement_areas,
                "errors": evaluation_response.errors,
            }

        interview_data = None
        if interview_response is not None:
            interview_data = {
                "status": interview_response.status,
                "target_role": interview_response.target_role,
                "interview_mode": interview_response.interview_mode,
                "questions": [q.model_dump() for q in interview_response.questions],
                "preparation_summary": interview_response.preparation_summary,
                "errors": interview_response.errors,
            }

        aggregated = {
            "candidate_id": candidate_id,
            "user_query": user_query,
            "target_role": target_role,
            "tasks": effective_tasks,
            "candidate_profile": candidate_profile,
            "recommendation": rec_data,
            "evaluation": eval_data,
            "interview": interview_data,
            "agent_results": agent_results or {},
            "retrieval_sources": effective_context.metadata.get("sources", []) if effective_context else [],
            "errors": accumulated_errors,
        }

        return aggregated


context_aggregator = ContextAggregator()
