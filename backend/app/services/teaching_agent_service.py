"""
Isolated Service Interface for LangGraph Teaching Agent (Phase 3.1).

Integrates the LangGraph teaching workflow behind an isolated service interface
without altering existing Teaching Room production routes, schemas, or database writes.
Production traffic continues to use the existing procedural service until Phase 3.4.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.ai.agents.teaching_agent import (
    TeachingAgentWorkflow,
    teaching_agent_workflow,
)
from app.ai.agents.teaching_state import TeachingState
from app.schemas.teaching import TeachingChatRequest, TeachingChatResponse

logger = logging.getLogger("careerverse.ai.teaching_agent_service")


def execute_teaching_graph_state(
    initial_state: TeachingState,
    workflow: Optional[TeachingAgentWorkflow] = None,
) -> TeachingState:
    """
    Direct graph state executor for testing and standalone inspection.
    """
    runner = workflow or teaching_agent_workflow
    return runner.run(initial_state)


def execute_teaching_agent_workflow(
    req: TeachingChatRequest,
    user_id: Optional[int] = None,
    user_name: Optional[str] = None,
    retrieved_evidence: Optional[List[Dict[str, Any]]] = None,
    workflow: Optional[TeachingAgentWorkflow] = None,
) -> TeachingChatResponse:
    """
    Service entrypoint: Transforms a TeachingChatRequest into TeachingState,
    executes the LangGraph workflow, and returns a verified TeachingChatResponse.
    Does not touch database or progress tracking (reserved for Phase 3.4).
    """
    runner = workflow or teaching_agent_workflow

    # Transform request to typed TeachingState
    chat_history_list = []
    if req.chat_history:
        for turn in req.chat_history:
            if hasattr(turn, "model_dump"):
                chat_history_list.append(turn.model_dump())
            elif isinstance(turn, dict):
                chat_history_list.append(turn)

    initial_state: TeachingState = {
        "learner_query": req.message,
        "original_query": req.message,
        "user_id": user_id,
        "user_name": user_name,
        "mode": req.mode or "skill",
        "target_id": req.target_id,
        "lesson_id": req.lesson_id,
        "chat_history": chat_history_list,
        "language": req.language or "en",
        "is_assessment": bool(req.is_assessment),
        "workspace_code": req.code_workspace,
        "retrieved_evidence": retrieved_evidence,
        "errors": [],
        "status": "initialized",
    }

    final_state = runner.run(initial_state)
    structured = final_state.get("structured_response") or {}

    # Convert to standard response schema
    return TeachingChatResponse(
        reply=structured.get("reply", "I am ready to help you learn!"),
        teaching_mode=structured.get("teaching_mode", req.mode or "skill"),
        target_id=structured.get("target_id", req.target_id),
        lesson_id=structured.get("lesson_id", req.lesson_id),
        current_stage=structured.get("current_stage", "explanation"),
        citations=structured.get("citations", []),
        technical_source_status=structured.get("technical_source_status", "not_refreshed"),
        suggested_follow_ups=structured.get("suggested_follow_ups", []),
        is_assessment=structured.get("is_assessment", False),
        assessment_evaluation=structured.get("assessment_evaluation"),
        demonstrated_understanding=structured.get("demonstrated_understanding", False),
        recommended_next_action=structured.get("recommended_next_action"),
        audio_narrative=structured.get("audio_narrative"),
        evidence_sufficiency=structured.get("evidence_sufficiency", "sufficient"),
    )
