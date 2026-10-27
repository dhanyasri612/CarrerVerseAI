"""
Phase 3.1 Tests: LangGraph Teaching Agent Foundation.

Coverage:
1. State initialization and type structure.
2. Graph execution for a normal technical question.
3. Ambiguous-question conditional routing without hallucinated citations.
4. Missing / insufficient evidence handling (no fake citations).
5. Code intent detection & Socratic hints.
6. Graph exception handling and safe error reporting.
7. Service interface contract compatibility (TeachingChatResponse).
8. Existing teaching service regression compatibility.
"""

from unittest.mock import MagicMock, patch
import pytest

from app.ai.agents.teaching_state import TeachingState
from app.ai.agents.teaching_agent import (
    TeachingAgentWorkflow,
    analyze_query_node,
    prepare_teaching_decision_node,
    finalize_response_node,
    route_after_query_analysis,
    teaching_agent_workflow,
)
from app.services.teaching_agent_service import (
    execute_teaching_graph_state,
    execute_teaching_agent_workflow,
)
from app.schemas.teaching import TeachingChatRequest, TeachingChatResponse


class TestTeachingAgentFoundation:
    """Phase 3.1 LangGraph Teaching Agent Foundation Tests."""

    def test_teaching_state_initialization_and_typing(self):
        """Test 1: TeachingState initializes correctly with optional keys."""
        state: TeachingState = {
            "learner_query": "Explain how React reconciler works",
            "mode": "skill",
            "target_id": "React",
            "status": "initialized",
            "errors": [],
        }
        assert state["learner_query"] == "Explain how React reconciler works"
        assert state["mode"] == "skill"
        assert state["target_id"] == "React"
        assert state["status"] == "initialized"
        assert len(state["errors"]) == 0

    def test_normal_question_execution_flow(self):
        """Test 2: Normal technical question traverses all nodes and completes."""
        initial_state: TeachingState = {
            "learner_query": "Explain how React useEffect cleanup functions prevent memory leaks",
            "target_id": "React",
            "mode": "skill",
            "retrieved_evidence": [
                {
                    "title": "react_hooks_reference.pdf",
                    "page_number": 14,
                    "section_heading": "Cleanup Invariants",
                    "similarity": 0.88,
                    "excerpt": "Cleanup functions run before the component unmounts and before re-running the effect.",
                }
            ],
            "status": "initialized",
        }

        workflow = TeachingAgentWorkflow()
        result = workflow.run(initial_state)

        assert result["status"] == "completed"
        assert result["is_ambiguous"] is False
        assert result["pedagogical_decision"] == "explain"
        assert result["evidence_sufficiency"] == "sufficient"
        assert len(result["citations"]) == 1
        assert result["citations"][0]["title"] == "react_hooks_reference.pdf"
        assert "execution_time_ms" in result
        assert result["execution_time_ms"] >= 0

        # Verify structured response adheres to TeachingChatResponse contract
        resp = result["structured_response"]
        assert resp is not None
        assert "React" in resp["reply"] or "foundational" in resp["reply"]
        assert resp["teaching_mode"] == "skill"
        assert len(resp["suggested_follow_ups"]) > 0

    def test_ambiguous_question_conditional_routing(self):
        """Test 3: Broad, vague queries short-circuit to clarification without fabricated citations."""
        initial_state: TeachingState = {
            "learner_query": "performance?",
            "target_id": "General",
            "mode": "skill",
            "status": "initialized",
        }

        workflow = TeachingAgentWorkflow()
        result = workflow.run(initial_state)

        assert result["status"] == "completed"
        assert result["is_ambiguous"] is True
        assert result["pedagogical_decision"] == "clarify"
        assert result["evidence_sufficiency"] == "ambiguous"
        # Anti-hallucination check: Citations MUST be empty
        assert result["citations"] == []
        assert len(result["structured_response"]["citations"]) == 0
        assert "clarify" in result["tutor_reply"].lower() or "broad" in result["tutor_reply"].lower()

    def test_route_after_query_analysis_decision(self):
        """Test 4: Routing helper correctly branches on ambiguity flag."""
        ambiguous_state: TeachingState = {"is_ambiguous": True}
        clear_state: TeachingState = {"is_ambiguous": False}

        assert route_after_query_analysis(ambiguous_state) == "finalize_response"
        assert route_after_query_analysis(clear_state) == "retrieve_evidence"

    def test_missing_or_insufficient_evidence_flow(self):
        """Test 5: Questions lacking evidence trigger honest course-materials notice and zero fake citations."""
        initial_state: TeachingState = {
            "learner_query": "Explain quantum teleportation entanglement algorithms",
            "target_id": "Quantum Computing",
            "mode": "skill",
            "retrieved_evidence": [],  # No evidence in syllabus
            "status": "initialized",
        }

        workflow = TeachingAgentWorkflow()
        result = workflow.run(initial_state)

        assert result["status"] == "completed"
        assert result["evidence_sufficiency"] == "insufficient"
        assert result["pedagogical_decision"] == "general_overview"
        # Citations must remain empty
        assert result["citations"] == []
        assert "Course Materials Notice" in result["tutor_reply"]
        assert "General Software Engineering Overview" in result["tutor_reply"]

    def test_code_intent_detection(self):
        """Test 6: Inquiries containing code cues set code_walkthrough intent and code_demonstration action."""
        initial_state: TeachingState = {
            "learner_query": "Show me Python code implementation for binary search",
            "target_id": "Binary Search",
            "mode": "skill",
            "retrieved_evidence": [{"title": "algorithms.md"}],
            "status": "initialized",
        }

        workflow = TeachingAgentWorkflow()
        result = workflow.run(initial_state)

        assert result["learner_intent"] == "code_walkthrough"
        assert result["pedagogical_decision"] == "code_demonstration"
        assert "```python" in result["tutor_reply"]

    def test_graph_exception_and_safe_error_handling(self):
        """Test 7: Unexpected exceptions during graph execution log safely and return a compliant fallback."""
        workflow = TeachingAgentWorkflow()

        # Patch internal node to trigger unexpected exception
        with patch("app.ai.agents.teaching_agent.analyze_query_node", side_effect=RuntimeError("Test crash")):
            result = workflow.run({"learner_query": "Any query", "mode": "skill", "target_id": "Test"})

        assert result["status"] == "error"
        assert len(result["errors"]) > 0
        assert "error" in result["errors"][0].lower()
        # Fallback response is still structurally valid and helpful
        assert result["structured_response"] is not None
        assert result["structured_response"]["evidence_sufficiency"] == "insufficient"
        assert result["structured_response"]["citations"] == []
        assert "temporary issue" in result["tutor_reply"]

    def test_service_interface_contract_compatibility(self):
        """Test 8: Service interface returns a valid TeachingChatResponse instance."""
        req = TeachingChatRequest(
            mode="skill",
            target_id="FastAPI",
            message="How do dependency injection providers work in FastAPI?",
            chat_history=[],
        )

        res = execute_teaching_agent_workflow(
            req=req,
            user_id=1,
            user_name="Alice",
            retrieved_evidence=[{"title": "fastapi_guide.md"}],
        )

        assert isinstance(res, TeachingChatResponse)
        assert res.teaching_mode == "skill"
        assert res.target_id == "FastAPI"
        assert res.evidence_sufficiency == "sufficient"
        assert isinstance(res.citations, list)
        assert len(res.citations) == 1
        assert res.citations[0]["title"] == "fastapi_guide.md"

    def test_service_interface_ambiguous_contract(self):
        """Test 9: Service interface returns clarification response on ambiguous query."""
        req = TeachingChatRequest(
            mode="skill",
            target_id="General",
            message="help me",
            chat_history=[],
        )

        res = execute_teaching_agent_workflow(req=req)

        assert isinstance(res, TeachingChatResponse)
        assert res.evidence_sufficiency == "ambiguous"
        assert res.citations == []
        assert "clarify" in res.reply.lower() or "detail" in res.reply.lower()

    def test_empty_query_safe_handling(self):
        """Test 10: Empty query string is safely flagged as ambiguous with no crash."""
        state = analyze_query_node({"learner_query": "   "})
        assert state["is_ambiguous"] is True
        assert state["pedagogical_decision"] == "clarify"
        assert state["evidence_sufficiency"] == "ambiguous"
