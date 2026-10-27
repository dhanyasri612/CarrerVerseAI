"""
Tests for CareerVerse AI LangGraph Teaching Agent — Phase 3.2: Retrieval & Evidence Gate Connection.

Validates:
1. Retrieval node with relevant course material.
2. Retrieval node with relevant technical resources.
3. No matching sources (empty results vs insufficient evidence).
4. Ambiguous question routing without unnecessary retrieval.
5. Retrieval exception and safe error state (graceful degradation without secret leakage).
6. Cross-user isolation (strictly scoped by authenticated user_id).
7. Citation metadata preservation (source_type, title, page_number, url, section_heading, similarity).
8. Evidence gate receives the actual retrieval results.
9. Service interface integration with authenticated user retrieval.
"""

from unittest.mock import MagicMock, patch
import pytest

from app.ai.agents.teaching_agent import (
    TeachingAgentWorkflow,
    retrieve_evidence_node,
    route_after_query_analysis,
)
from app.ai.agents.teaching_state import TeachingState
from app.schemas.course_document import CourseMaterialSearchResult
from app.schemas.teaching import TeachingChatRequest, TeachingChatResponse
from app.services.teaching_agent_service import execute_teaching_agent_workflow


class TestTeachingAgentRetrievalConnection:
    """Test suite for Phase 3.2 Retrieval Node and Evidence Gate orchestration."""

    def test_retrieval_node_with_course_material(self):
        """Test 1: Retrieval node finds relevant course material, marks evidence sufficient, and formats citation."""
        mock_cm = [
            CourseMaterialSearchResult(
                document_id=101,
                filename="Distributed_Systems_Course.pdf",
                page_number=42,
                section_heading="Paxos Consensus Invariants",
                similarity_score=0.89,
                excerpt="Paxos ensures safety and consensus across distributed learner nodes.",
                chunk_index=3,
            )
        ]

        with patch("app.services.course_document_service.search_course_materials", return_value=mock_cm) as mock_cm_search, \
             patch("app.services.teaching_resource_service.retrieve_teaching_resource_bundle", return_value={"technical_sources": {"status": "unavailable", "sources": []}, "resources": []}):

            initial_state: TeachingState = {
                "learner_query": "Explain how Paxos guarantees consensus across distributed nodes",
                "target_id": "Distributed Systems",
                "mode": "materials",
                "user_id": 42,
                "status": "initialized",
            }

            workflow = TeachingAgentWorkflow()
            result = workflow.run(initial_state)

            assert mock_cm_search.called
            assert mock_cm_search.call_args.kwargs["user_id"] == 42
            assert result["status"] == "completed"
            assert result["retrieval_status"] == "success"
            assert result["course_materials_status"] == "found"
            assert result["evidence_sufficiency"] == "sufficient"
            assert result["grounding_type"] == "course_material_grounded"
            assert len(result["citations"]) == 1

            cit = result["citations"][0]
            assert cit["source_type"] == "course_material"
            assert cit["filename"] == "Distributed_Systems_Course.pdf"
            assert cit["page_number"] == 42
            assert cit["section_heading"] == "Paxos Consensus Invariants"
            assert cit["similarity"] == 0.89
            assert "Paxos" in cit["excerpt"]

    def test_retrieval_node_with_technical_resources(self):
        """Test 2: Retrieval node finds fresh technical reference, preserves canonical URL and section heading."""
        mock_tech = {
            "technical_sources": {
                "status": "fresh",
                "sources": [
                    {
                        "id": "res-fastapi-di",
                        "title": "FastAPI Dependency Injection Guide",
                        "canonical_url": "https://fastapi.tiangolo.com/tutorial/dependencies/",
                        "section_heading": "Dependencies with Yield",
                        "similarity_score": 0.85,
                        "source": "FastAPI Official Docs",
                        "freshness_status": "fresh",
                        "excerpt": "Dependencies with yield allow teardown operations in finally blocks.",
                    }
                ],
            },
            "resources": [],
        }

        with patch("app.services.course_document_service.search_course_materials", return_value=[]), \
             patch("app.services.teaching_resource_service.retrieve_teaching_resource_bundle", return_value=mock_tech):

            initial_state: TeachingState = {
                "learner_query": "How do dependencies with yield manage transaction cleanups in FastAPI?",
                "target_id": "FastAPI",
                "mode": "skill",
                "user_id": 10,
                "status": "initialized",
            }

            workflow = TeachingAgentWorkflow()
            result = workflow.run(initial_state)

            assert result["status"] == "completed"
            assert result["retrieval_status"] == "success"
            assert result["technical_sources_status"] == "fresh"
            assert result["evidence_sufficiency"] == "sufficient"
            assert result["grounding_type"] == "source_grounded"
            assert len(result["citations"]) == 1

            cit = result["citations"][0]
            assert cit["source_type"] == "technical_source"
            assert cit["canonical_url"] == "https://fastapi.tiangolo.com/tutorial/dependencies/"
            assert cit["section_heading"] == "Dependencies with Yield"
            assert cit["similarity"] == 0.85
            assert cit["freshness_status"] == "fresh"

    def test_no_matching_sources_triggers_insufficient_notice_and_zero_citations(self):
        """Test 3: When retrieval returns zero matching sources, evidence gate sets insufficient and citations stay empty."""
        empty_tech = {
            "technical_sources": {"status": "not_refreshed", "sources": []},
            "resources": [],
        }

        with patch("app.services.course_document_service.search_course_materials", return_value=[]), \
             patch("app.services.teaching_resource_service.retrieve_teaching_resource_bundle", return_value=empty_tech):

            initial_state: TeachingState = {
                "learner_query": "Explain quantum entanglement teleportation algorithms",
                "target_id": "Quantum Teleportation",
                "mode": "skill",
                "user_id": 5,
                "status": "initialized",
            }

            workflow = TeachingAgentWorkflow()
            result = workflow.run(initial_state)

            assert result["status"] == "completed"
            assert result["retrieval_status"] == "no_results"
            assert result["evidence_sufficiency"] == "insufficient"
            assert result["pedagogical_decision"] == "general_overview"
            # Anti-hallucination check: Citations MUST be empty
            assert result["citations"] == []
            assert result["structured_response"]["citations"] == []
            assert "Course Materials Notice" in result["tutor_reply"] or "Scope Notice" in result["tutor_reply"]

    def test_ambiguous_question_routing_bypasses_retrieval_completely(self):
        """Test 4: Ambiguous queries short-circuit to clarification and bypass retrieval entirely."""
        with patch("app.services.course_document_service.search_course_materials") as mock_cm, \
             patch("app.services.teaching_resource_service.retrieve_teaching_resource_bundle") as mock_tech:

            initial_state: TeachingState = {
                "learner_query": "performance?",
                "target_id": "General",
                "mode": "skill",
                "user_id": 12,
                "status": "initialized",
            }

            workflow = TeachingAgentWorkflow()
            result = workflow.run(initial_state)

            # Neither retrieval function should ever be invoked
            mock_cm.assert_not_called()
            mock_tech.assert_not_called()

            assert result["status"] == "completed"
            assert result["is_ambiguous"] is True
            assert result["pedagogical_decision"] == "clarify"
            assert result["evidence_sufficiency"] == "ambiguous"
            assert result["citations"] == []

    def test_retrieval_exception_and_safe_error_handling(self):
        """Test 5: Vector DB or network failures log safely and degrade gracefully without crashing the workflow."""
        with patch("app.services.course_document_service.search_course_materials", side_effect=RuntimeError("ChromaDB socket timeout")), \
             patch("app.services.teaching_resource_service.retrieve_teaching_resource_bundle", side_effect=OSError("Network unreachable")):

            initial_state: TeachingState = {
                "learner_query": "How do database index lookups execute on B-trees?",
                "target_id": "PostgreSQL",
                "mode": "skill",
                "user_id": 99,
                "status": "initialized",
            }

            workflow = TeachingAgentWorkflow()
            result = workflow.run(initial_state)

            # The graph must not crash; it degrades gracefully to general overview
            assert result["status"] == "completed"
            assert result["retrieval_status"] == "error"
            assert result["course_materials_status"] == "error"
            assert result["technical_sources_status"] == "error"
            assert result["evidence_sufficiency"] == "insufficient"
            assert result["citations"] == []
            assert len(result["errors"]) >= 2
            assert any("RuntimeError" in err for err in result["errors"])
            assert any("OSError" in err for err in result["errors"])

    def test_cross_user_isolation(self):
        """Test 6: User A's query strictly queries User A's user_id, never User B's documents."""
        with patch("app.services.course_document_service.search_course_materials", return_value=[]) as mock_cm, \
             patch("app.services.teaching_resource_service.retrieve_teaching_resource_bundle", return_value={"technical_sources": {}, "resources": []}):

            initial_state: TeachingState = {
                "learner_query": "Explain microservices transaction boundaries",
                "target_id": "Architecture",
                "mode": "materials",
                "user_id": 777,
                "status": "initialized",
            }

            workflow = TeachingAgentWorkflow()
            workflow.run(initial_state)

            assert mock_cm.called
            called_user_id = mock_cm.call_args.kwargs.get("user_id")
            assert called_user_id == 777

    def test_unauthenticated_request_skips_course_materials(self):
        """Test 7: When user_id is None, course materials search is skipped to prevent cross-tenant exposure."""
        with patch("app.services.course_document_service.search_course_materials") as mock_cm, \
             patch("app.services.teaching_resource_service.retrieve_teaching_resource_bundle", return_value={"technical_sources": {}, "resources": []}):

            initial_state: TeachingState = {
                "learner_query": "Explain REST vs gRPC trade-offs",
                "target_id": "APIs",
                "mode": "skill",
                "user_id": None,
                "status": "initialized",
            }

            workflow = TeachingAgentWorkflow()
            result = workflow.run(initial_state)

            mock_cm.assert_not_called()
            assert result["course_materials_status"] == "skipped"

    def test_evidence_gate_receives_actual_retrieval_results(self):
        """Test 8: Verify evaluate_teaching_evidence_sufficiency receives the actual retrieved objects."""
        mock_cm = [
            CourseMaterialSearchResult(
                document_id=202,
                filename="react_state.md",
                page_number=None,
                section_heading="Immutability",
                similarity_score=0.75,
                excerpt="State should be treated as immutable.",
                chunk_index=1,
            )
        ]

        with patch("app.services.course_document_service.search_course_materials", return_value=mock_cm), \
             patch("app.services.teaching_resource_service.retrieve_teaching_resource_bundle", return_value={"technical_sources": {}, "resources": []}), \
             patch("app.ai.rag.evidence_gate.evaluate_teaching_evidence_sufficiency") as mock_gate:

            mock_gate.return_value = MagicMock(
                is_sufficient=True,
                status="sufficient",
                grounding_type="course_material_grounded",
                best_similarity=0.75,
                matched_sources=mock_cm,
                insufficient_evidence_notice=None,
            )

            initial_state: TeachingState = {
                "learner_query": "Why is state immutable in React?",
                "target_id": "React",
                "mode": "skill",
                "user_id": 55,
                "status": "initialized",
            }

            workflow = TeachingAgentWorkflow()
            workflow.run(initial_state)

            assert mock_gate.called
            gate_call_kwargs = mock_gate.call_args.kwargs
            assert gate_call_kwargs["course_materials"] == mock_cm
            assert "React" in gate_call_kwargs["target_topic"]

    def test_service_interface_authenticated_retrieval(self):
        """Test 9: execute_teaching_agent_workflow runs retrieval for authenticated user and returns TeachingChatResponse."""
        mock_cm = [
            CourseMaterialSearchResult(
                document_id=303,
                filename="python_concurrency.pdf",
                page_number=5,
                section_heading="Asyncio Tasks",
                similarity_score=0.82,
                excerpt="asyncio.create_task schedules coroutines concurrently.",
                chunk_index=0,
            )
        ]

        with patch("app.services.course_document_service.search_course_materials", return_value=mock_cm), \
             patch("app.services.teaching_resource_service.retrieve_teaching_resource_bundle", return_value={"technical_sources": {}, "resources": []}):

            req = TeachingChatRequest(
                mode="materials",
                target_id="Python Concurrency",
                message="How does asyncio.create_task schedule work?",
                chat_history=[],
            )

            res = execute_teaching_agent_workflow(
                req=req,
                user_id=88,
                user_name="Developer Dave",
            )

            assert isinstance(res, TeachingChatResponse)
            assert res.evidence_sufficiency == "sufficient"
            assert len(res.citations) == 1
            assert res.citations[0]["filename"] == "python_concurrency.pdf"
            assert res.citations[0]["page_number"] == 5
            assert res.citations[0]["similarity"] == 0.82
