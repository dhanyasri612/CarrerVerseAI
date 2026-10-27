"""
Tests for CareerVerse AI LangGraph Teaching Agent — Phase 3.3: Adaptive Teaching Decisions.

Validates:
1. Every pedagogical decision:
   - clarify
   - explain
   - socratic_hint
   - code_demonstration
   - evaluate_response
   - general_overview
2. Conditional graph routing via route_pedagogical_strategy to each dedicated handler.
3. Ambiguous and insufficient evidence overriding unsafe strategies.
4. Code demonstrations retaining source grounding and citations.
5. Socratic hints guiding the learner without revealing full solutions unnecessarily.
6. Answer evaluation using the learner's actual submitted answer and workspace code.
7. Citation preservation and schema compatibility with TeachingChatResponse.
8. Provider errors, exceptions, and malformed model output with safe fallback.
"""

from unittest.mock import MagicMock, patch
import pytest

from app.ai.agents.teaching_agent import (
    TeachingAgentWorkflow,
    analyze_query_node,
    prepare_teaching_decision_node,
    route_pedagogical_strategy,
    teach_clarify_node,
    teach_code_demonstration_node,
    teach_evaluate_response_node,
    teach_explain_node,
    teach_general_overview_node,
    teach_socratic_hint_node,
)
from app.ai.agents.teaching_state import TeachingState
from app.schemas.teaching import TeachingChatRequest, TeachingChatResponse
from app.services.teaching_agent_service import execute_teaching_agent_workflow


@pytest.fixture
def sample_grounded_evidence():
    """Sample verified evidence from course materials and technical references."""
    return [
        {
            "source_type": "course_material",
            "title": "Algorithms_and_Data_Structures.pdf",
            "filename": "Algorithms_and_Data_Structures.pdf",
            "document_id": 10,
            "page_number": 42,
            "section_heading": "Binary Search Invariants",
            "similarity": 0.91,
            "similarity_score": 0.91,
            "excerpt": "Binary search maintains the invariant that the target element must lie in data[left..right]. Midpoint is computed as (left + right) // 2.",
        },
        {
            "source_type": "technical_source",
            "id": "ref-binary-search-opt",
            "title": "Python Bisect Implementation Guide",
            "canonical_url": "https://docs.python.org/3/library/bisect.html",
            "section_heading": "Searching Sorted Lists",
            "similarity": 0.86,
            "similarity_score": 0.86,
            "excerpt": "Bisect locates insertion points with O(log n) comparisons using boundary checks.",
            "source": "Python Official Documentation",
            "freshness_status": "fresh",
        },
    ]


class TestTeachingAgentAdaptiveDecisions:
    """Test suite for Phase 3.3 Adaptive Pedagogical Decisions in LangGraph."""

    # ─────────────────────────────────────────────────────────────────────────
    # 1. PEDAGOGICAL DECISION LOGIC TESTS
    # ─────────────────────────────────────────────────────────────────────────

    def test_decision_ambiguous_query_yields_clarify(self):
        """Ambiguous query selects 'clarify' and clears citations."""
        state: TeachingState = {
            "learner_query": "help?",
            "is_ambiguous": True,
            "ambiguity_reason": "Query is too brief and vague",
            "status": "analyzed",
        }
        decision_out = prepare_teaching_decision_node(state)

        assert decision_out["pedagogical_decision"] == "clarify"
        assert decision_out["evidence_sufficiency"] == "ambiguous"
        assert decision_out["citations"] == []
        assert route_pedagogical_strategy({**state, **decision_out}) == "teach_clarify"

    def test_decision_insufficient_evidence_yields_general_overview(self):
        """Insufficient evidence triggers 'general_overview' with explicit scope notice and zero citations."""
        state: TeachingState = {
            "learner_query": "Explain quantum flux capacitors",
            "target_id": "Quantum Mechanics",
            "is_ambiguous": False,
            "evidence_sufficiency": "insufficient",
            "retrieved_evidence": [],
            "status": "retrieved",
        }
        decision_out = prepare_teaching_decision_node(state)

        assert decision_out["pedagogical_decision"] == "general_overview"
        assert decision_out["evidence_sufficiency"] == "insufficient"
        assert decision_out["citations"] == []
        assert "Course Materials Notice" in decision_out["insufficient_evidence_notice"]
        assert route_pedagogical_strategy({**state, **decision_out}) == "teach_general_overview"

    def test_decision_insufficient_evidence_overrides_unsafe_code_request(self):
        """When evidence is insufficient, code walkthrough requests are safely downgraded to general_overview."""
        state: TeachingState = {
            "learner_query": "Show me python code for quantum teleportation teleport()",
            "learner_intent": "code_walkthrough",
            "target_id": "Quantum Teleportation",
            "evidence_sufficiency": "insufficient",
            "retrieved_evidence": [],
            "status": "retrieved",
        }
        decision_out = prepare_teaching_decision_node(state)

        # Safety override: Insufficient evidence must NOT allow code demonstration
        assert decision_out["pedagogical_decision"] == "general_overview"
        assert decision_out["citations"] == []
        assert route_pedagogical_strategy({**state, **decision_out}) == "teach_general_overview"

    def test_decision_insufficient_evidence_overrides_unsafe_socratic_hint(self):
        """When evidence is insufficient, socratic hints without evidence are safely routed to general_overview."""
        state: TeachingState = {
            "learner_query": "Give me a hint for solving cold fusion",
            "learner_intent": "socratic_hint",
            "target_id": "Cold Fusion",
            "evidence_sufficiency": "insufficient",
            "retrieved_evidence": [],
            "status": "retrieved",
        }
        decision_out = prepare_teaching_decision_node(state)

        assert decision_out["pedagogical_decision"] == "general_overview"
        assert decision_out["citations"] == []

    def test_decision_code_walkthrough_with_evidence_yields_code_demonstration(self, sample_grounded_evidence):
        """Learner requesting code walkthrough with sufficient evidence selects 'code_demonstration'."""
        state: TeachingState = {
            "learner_query": "Show code example for binary search in Python",
            "learner_intent": "code_walkthrough",
            "target_id": "Binary Search",
            "evidence_sufficiency": "sufficient",
            "retrieved_evidence": sample_grounded_evidence,
            "status": "retrieved",
        }
        decision_out = prepare_teaching_decision_node(state)

        assert decision_out["pedagogical_decision"] == "code_demonstration"
        assert len(decision_out["citations"]) >= 1
        assert route_pedagogical_strategy({**state, **decision_out}) == "teach_code_demonstration"

    def test_decision_socratic_hint_with_evidence_yields_socratic_hint(self, sample_grounded_evidence):
        """Learner requesting a hint with sufficient evidence selects 'socratic_hint'."""
        state: TeachingState = {
            "learner_query": "I am stuck on binary search, give me a small hint without spoiling it",
            "learner_intent": "socratic_hint",
            "target_id": "Binary Search",
            "evidence_sufficiency": "sufficient",
            "retrieved_evidence": sample_grounded_evidence,
            "status": "retrieved",
        }
        decision_out = prepare_teaching_decision_node(state)

        assert decision_out["pedagogical_decision"] == "socratic_hint"
        assert len(decision_out["citations"]) >= 1
        assert route_pedagogical_strategy({**state, **decision_out}) == "teach_socratic_hint"

    def test_decision_answer_submission_yields_evaluate_response(self, sample_grounded_evidence):
        """Learner submitting an answer selects 'evaluate_response'."""
        state: TeachingState = {
            "learner_query": "Here is my answer: We maintain left and right pointers and move left to mid + 1.",
            "learner_intent": "answer_submission",
            "target_id": "Binary Search",
            "evidence_sufficiency": "sufficient",
            "retrieved_evidence": sample_grounded_evidence,
            "status": "retrieved",
        }
        decision_out = prepare_teaching_decision_node(state)

        assert decision_out["pedagogical_decision"] == "evaluate_response"
        assert route_pedagogical_strategy({**state, **decision_out}) == "teach_evaluate_response"

    def test_decision_assessment_mode_yields_evaluate_response(self, sample_grounded_evidence):
        """When is_assessment is True, decision selects 'evaluate_response' regardless of generic intent."""
        state: TeachingState = {
            "learner_query": "My solution computes mid = (left + right) // 2",
            "is_assessment": True,
            "target_id": "Binary Search",
            "evidence_sufficiency": "sufficient",
            "retrieved_evidence": sample_grounded_evidence,
            "status": "retrieved",
        }
        decision_out = prepare_teaching_decision_node(state)

        assert decision_out["pedagogical_decision"] == "evaluate_response"
        assert route_pedagogical_strategy({**state, **decision_out}) == "teach_evaluate_response"

    def test_decision_clear_conceptual_question_yields_explain(self, sample_grounded_evidence):
        """Clear conceptual question with sufficient evidence selects 'explain'."""
        state: TeachingState = {
            "learner_query": "Explain how binary search invariants prevent infinite loops",
            "learner_intent": "concept_explanation",
            "target_id": "Binary Search",
            "evidence_sufficiency": "sufficient",
            "retrieved_evidence": sample_grounded_evidence,
            "status": "retrieved",
        }
        decision_out = prepare_teaching_decision_node(state)

        assert decision_out["pedagogical_decision"] == "explain"
        assert len(decision_out["citations"]) >= 1
        assert route_pedagogical_strategy({**state, **decision_out}) == "teach_explain"

    # ─────────────────────────────────────────────────────────────────────────
    # 2. STRATEGY HANDLER AND ROUTING EXECUTION TESTS
    # ─────────────────────────────────────────────────────────────────────────

    def test_teach_clarify_handler_sets_clean_prompt_and_zero_citations(self):
        """teach_clarify_node returns focused prompt with empty citations."""
        state: TeachingState = {
            "target_id": "System Architecture",
            "clarification_prompt": "Could you clarify if you mean monolithic or microservice architecture?",
        }
        res = teach_clarify_node(state)

        assert "monolithic or microservice" in res["tutor_reply"]
        assert res["citations"] == []
        assert res["technical_source_status"] == "ambiguous_query"
        assert res["status"] == "clarified"

    def test_teach_general_overview_handler_has_scope_notice_and_zero_citations(self):
        """teach_general_overview_node provides explicit scope notice without unsupported citations."""
        state: TeachingState = {
            "learner_query": "Describe advanced neural quantum entanglement",
            "target_id": "Quantum Computing",
            "insufficient_evidence_notice": "📚 **Course Materials Notice**: The topic `Describe advanced neural...` is not covered.",
        }
        res = teach_general_overview_node(state)

        assert "Course Materials Notice" in res["tutor_reply"]
        assert "General Software Engineering Overview" in res["tutor_reply"]
        assert res["citations"] == []
        assert res["status"] == "overview_prepared"

    def test_teach_explain_handler_with_llm_response(self, sample_grounded_evidence):
        """teach_explain_node uses LLM provider when available and preserves citations."""
        mock_provider = MagicMock()
        mock_provider.generate_text.return_value = MagicMock(
            content="Binary search operates by maintaining an invariant interval [left, right] that contains the target."
        )

        with patch("app.ai.providers.get_model_provider", return_value=mock_provider):
            state: TeachingState = {
                "learner_query": "Explain binary search",
                "target_id": "Binary Search",
                "citations": sample_grounded_evidence,
                "grounding_type": "course_material_grounded",
            }
            res = teach_explain_node(state)

            assert "invariant interval" in res["tutor_reply"]
            assert len(res["citations"]) == 2
            assert res["status"] == "explained"
            mock_provider.generate_text.assert_called_once()

    def test_teach_explain_handler_fallback_on_provider_error(self, sample_grounded_evidence):
        """teach_explain_node safely falls back to deterministic grounded explanation when provider throws."""
        with patch("app.ai.providers.get_model_provider", side_effect=RuntimeError("Provider API timeout")):
            state: TeachingState = {
                "learner_query": "Explain binary search",
                "target_id": "Binary Search",
                "citations": sample_grounded_evidence,
                "grounding_type": "course_material_grounded",
            }
            res = teach_explain_node(state)

            assert "Based on your uploaded course materials" in res["tutor_reply"]
            assert "Binary Search" in res["tutor_reply"]
            assert len(res["citations"]) == 2
            assert res["status"] == "explained"

    def test_teach_code_demonstration_grounded_with_code_block(self, sample_grounded_evidence):
        """teach_code_demonstration_node delivers structured python code grounded in references."""
        with patch("app.ai.providers.get_model_provider", side_effect=RuntimeError("Provider offline")):
            state: TeachingState = {
                "learner_query": "Write binary search code",
                "target_id": "Binary Search",
                "citations": sample_grounded_evidence,
            }
            res = teach_code_demonstration_node(state)

            assert "```python" in res["tutor_reply"]
            assert "def binary_search" in res["tutor_reply"]
            assert len(res["citations"]) == 2
            assert res["status"] == "code_demonstrated"

    def test_teach_socratic_hint_does_not_reveal_full_solution(self, sample_grounded_evidence):
        """teach_socratic_hint_node nudges learner with questions and does NOT dump full code blocks."""
        state: TeachingState = {
            "learner_query": "Give me a hint on how to search",
            "target_id": "Binary Search",
            "citations": sample_grounded_evidence,
        }
        res = teach_socratic_hint_node(state)

        assert "Socratic Guidance" in res["tutor_reply"]
        # Hint should not give away full complete code blocks
        assert "```python\ndef " not in res["tutor_reply"]
        assert res["socratic_stage"] == "practice"
        assert len(res["citations"]) == 2
        assert res["status"] == "hint_prepared"

    # ─────────────────────────────────────────────────────────────────────────
    # 3. ANSWER EVALUATION LOGIC TESTS
    # ─────────────────────────────────────────────────────────────────────────

    def test_teach_evaluate_response_with_correct_answer(self, sample_grounded_evidence):
        """Rigorous evaluation awards passing score and marks demonstrated_understanding=True for correct logic."""
        state: TeachingState = {
            "learner_query": "I use two pointers, left and right. In the loop, mid = (left + right) // 2. If target > mid, left = mid + 1.",
            "workspace_code": "left, right = 0, len(arr) - 1\nwhile left <= right:\n    mid = (left + right) // 2\n    if arr[mid] == target: return mid\n    elif arr[mid] < target: left = mid + 1\n    else: right = mid - 1",
            "target_id": "Binary Search",
            "citations": sample_grounded_evidence,
        }
        res = teach_evaluate_response_node(state)

        assert res["demonstrated_understanding"] is True
        assert res["assessment_score"] >= 80
        assert res["assessment_evaluation"]["score"] >= 80
        assert res["assessment_evaluation"]["demonstrated"] is True
        assert "What You Got Right" in res["tutor_reply"]
        assert "Score" in res["tutor_reply"]
        assert res["socratic_stage"] == "completed"

    def test_teach_evaluate_response_with_suboptimal_linear_answer(self, sample_grounded_evidence):
        """Evaluation recognizes suboptimal brute-force logic and marks demonstrated_understanding=False."""
        state: TeachingState = {
            "learner_query": "I will loop all items one by one in a linear scan using a brute force check.",
            "target_id": "Binary Search",
            "citations": sample_grounded_evidence,
        }
        res = teach_evaluate_response_node(state)

        assert res["demonstrated_understanding"] is False
        assert res["assessment_score"] < 80
        assert any(k in res["tutor_reply"].lower() for k in ["linear or brute-force approach does not meet optimal complexity", "linear", "brute force", "o(n)"])
        assert res["socratic_stage"] == "practice"

    def test_teach_evaluate_response_with_trivial_or_idk_answer(self, sample_grounded_evidence):
        """Evaluation flags trivial or missing answers with low score and targeted feedback."""
        state: TeachingState = {
            "learner_query": "i don't know",
            "target_id": "Binary Search",
            "citations": sample_grounded_evidence,
        }
        res = teach_evaluate_response_node(state)

        assert res["demonstrated_understanding"] is False
        assert res["assessment_score"] <= 30
        assert res["assessment_evaluation"]["demonstrated"] is False
        assert any(k in res["tutor_reply"].lower() for k in ["no concrete algorithmic reasoning", "does not address", "no reasoning", "blank response", "not address the question"])

    # ─────────────────────────────────────────────────────────────────────────
    # 4. END-TO-END GRAPH WORKFLOW ROUTING INTEGRATION TESTS
    # ─────────────────────────────────────────────────────────────────────────

    def test_full_workflow_routes_to_code_demonstration(self, sample_grounded_evidence):
        """Full graph execution routes code walkthrough query to code_demonstration handler."""
        initial_state: TeachingState = {
            "learner_query": "Please provide a python code implementation for binary search",
            "target_id": "Binary Search",
            "mode": "skill",
            "retrieved_evidence": sample_grounded_evidence,
            "evidence_sufficiency": "sufficient",
            "skip_retrieval": True,
            "status": "initialized",
        }
        workflow = TeachingAgentWorkflow()
        result = workflow.run(initial_state)

        assert result["status"] == "completed"
        assert result["pedagogical_decision"] == "code_demonstration"
        assert "```python" in result["tutor_reply"]
        assert len(result["citations"]) == 2

        # Schema compatibility check
        resp = TeachingChatResponse.model_validate(result["structured_response"])
        assert resp.target_id == "Binary Search"
        assert len(resp.citations) == 2

    def test_full_workflow_routes_to_socratic_hint(self, sample_grounded_evidence):
        """Full graph execution routes hint request to socratic_hint handler."""
        initial_state: TeachingState = {
            "learner_query": "I am stuck, could you give me a small hint on how to divide the array?",
            "target_id": "Binary Search",
            "mode": "skill",
            "retrieved_evidence": sample_grounded_evidence,
            "evidence_sufficiency": "sufficient",
            "skip_retrieval": True,
            "status": "initialized",
        }
        workflow = TeachingAgentWorkflow()
        result = workflow.run(initial_state)

        assert result["status"] == "completed"
        assert result["pedagogical_decision"] == "socratic_hint"
        assert "Socratic Guidance" in result["tutor_reply"]
        assert result["structured_response"]["current_stage"] == "practice"

    def test_full_workflow_routes_to_evaluate_response(self, sample_grounded_evidence):
        """Full graph execution routes answer submission to evaluate_response handler and sets assessment fields."""
        initial_state: TeachingState = {
            "learner_query": "Here is my answer: We set mid = (left + right) // 2 and halve the pointer boundaries.",
            "workspace_code": "left, right = 0, len(arr) - 1\nwhile left <= right:\n    mid = (left + right) // 2\n    if arr[mid] == target: return mid\n    elif arr[mid] < target: left = mid + 1\n    else: right = mid - 1",
            "target_id": "Binary Search",
            "mode": "assessment",
            "is_assessment": True,
            "retrieved_evidence": sample_grounded_evidence,
            "evidence_sufficiency": "sufficient",
            "skip_retrieval": True,
            "status": "initialized",
        }
        workflow = TeachingAgentWorkflow()
        result = workflow.run(initial_state)

        assert result["status"] == "completed"
        assert result["pedagogical_decision"] == "evaluate_response"
        assert result["demonstrated_understanding"] is True
        assert result["assessment_score"] >= 80

        # Structured response contract adherence
        resp = TeachingChatResponse.model_validate(result["structured_response"])
        assert resp.is_assessment is True
        assert resp.demonstrated_understanding is True
        assert resp.assessment_evaluation is not None
        assert resp.assessment_evaluation["score"] >= 80

    def test_full_workflow_routes_to_general_overview_on_insufficient_evidence(self):
        """Full graph execution routes missing evidence to general_overview with zero citations."""
        empty_tech = {"technical_sources": {"status": "unavailable", "sources": []}, "resources": []}
        with patch("app.services.course_document_service.search_course_materials", return_value=[]), \
             patch("app.services.teaching_resource_service.retrieve_teaching_resource_bundle", return_value=empty_tech):

            initial_state: TeachingState = {
                "learner_query": "Teach me advanced hyperspace teleportation mechanics",
                "target_id": "Hyperspace",
                "mode": "skill",
                "user_id": 99,
                "status": "initialized",
            }
            workflow = TeachingAgentWorkflow()
            result = workflow.run(initial_state)

            assert result["status"] == "completed"
            assert result["pedagogical_decision"] == "general_overview"
            assert result["evidence_sufficiency"] == "insufficient"
            assert result["citations"] == []
            assert result["structured_response"]["citations"] == []
            assert "Course Materials Notice" in result["tutor_reply"]

    # ─────────────────────────────────────────────────────────────────────────
    # 5. SERVICE INTERFACE INTEGRATION WITH WORKSPACE CODE
    # ─────────────────────────────────────────────────────────────────────────

    def test_service_interface_passes_workspace_code_and_evaluates(self, sample_grounded_evidence):
        """TeachingAgentService passes workspace code to the graph and returns structured TeachingChatResponse."""
        with patch("app.services.course_document_service.search_course_materials", return_value=[]), \
             patch("app.services.teaching_resource_service.retrieve_teaching_resource_bundle", return_value={"technical_sources": {"status": "fresh", "sources": sample_grounded_evidence}, "resources": []}), \
             patch("app.ai.providers.get_model_provider", side_effect=RuntimeError("Provider offline")):

            req = TeachingChatRequest(
                message="Did I get this right? Check my binary search.",
                target_id="Binary Search",
                mode="assessment",
                code_workspace="def search(nums, target):\n    l, r = 0, len(nums) - 1\n    while l <= r:\n        m = (l + r) // 2\n        if nums[m] == target: return m\n        elif nums[m] < target: l = m + 1\n        else: r = m - 1",
            )

            res = execute_teaching_agent_workflow(req, user_id=42)

            assert isinstance(res, TeachingChatResponse)
            assert res.demonstrated_understanding is True
            assert res.assessment_evaluation is not None
            assert res.assessment_evaluation["score"] >= 80
            assert "✅ What You Got Right" in res.reply or "Score" in res.reply

    # ─────────────────────────────────────────────────────────────────────────
    # 6. PHASE 3.3.1 REGRESSION TESTS: FIX 1, FIX 2, FIX 3
    # ─────────────────────────────────────────────────────────────────────────

    def test_teach_evaluate_response_irrelevant_lengthy_tennis_answer(self, sample_grounded_evidence):
        """Fix 1: Lengthy irrelevant answer about tennis gets low score and demonstrated_understanding=False."""
        with patch("app.ai.providers.get_model_provider", side_effect=RuntimeError("Provider offline")):
            state: TeachingState = {
                "learner_query": "I enjoy playing tennis on Sunday mornings with friends when the sun is shining brightly in the sky.",
                "target_id": "Binary Search",
                "citations": sample_grounded_evidence,
            }
            res = teach_evaluate_response_node(state)

            assert res["demonstrated_understanding"] is False
            assert res["assessment_score"] <= 30
            assert "does not appear to address the technical requirements" in res["tutor_reply"]

    def test_teach_evaluate_response_incorrect_linear_with_left_and_right(self, sample_grounded_evidence):
        """Fix 1: Incorrect linear-search answer containing 'left' and 'right' is NOT awarded passing score."""
        with patch("app.ai.providers.get_model_provider", side_effect=RuntimeError("Provider offline")):
            state: TeachingState = {
                "learner_query": "We scan each element from left to right one by one using a linear loop until we find the item.",
                "target_id": "Binary Search",
                "citations": sample_grounded_evidence,
            }
            res = teach_evaluate_response_node(state)

            assert res["demonstrated_understanding"] is False
            assert res["assessment_score"] <= 50
            assert "linear or brute-force" in res["tutor_reply"].lower()

    def test_teach_evaluate_response_partially_correct_answer(self, sample_grounded_evidence):
        """Fix 1: Partially correct answer with halving but missing/uncertain pointer updates gets non-passing score."""
        with patch("app.ai.providers.get_model_provider", side_effect=RuntimeError("Provider offline")):
            state: TeachingState = {
                "learner_query": "We compute mid = (left + right) // 2 and look at the middle item, but I don't know how to move the left and right pointers properly.",
                "target_id": "Binary Search",
                "citations": sample_grounded_evidence,
            }
            res = teach_evaluate_response_node(state)

            assert res["demonstrated_understanding"] is False
            assert 50 <= res["assessment_score"] <= 70
            assert "Pointer boundary updates were missing or incomplete" in res["tutor_reply"]

    def test_teach_evaluate_response_empty_and_skip_answers(self, sample_grounded_evidence):
        """Fix 1: Empty and skip answers receive low baseline score and demonstrated_understanding=False."""
        with patch("app.ai.providers.get_model_provider", side_effect=RuntimeError("Provider offline")):
            for phrase in ["", "idk", "pass", "skip", "i don't know"]:
                state: TeachingState = {
                    "learner_query": phrase,
                    "target_id": "Binary Search",
                    "citations": sample_grounded_evidence,
                }
                res = teach_evaluate_response_node(state)
                assert res["demonstrated_understanding"] is False
                assert res["assessment_score"] <= 25

    def test_teach_evaluate_response_provider_timeout_and_malformed_output(self, sample_grounded_evidence):
        """Fix 1: Provider timeout or malformed output without score engages safe offline evaluation."""
        # Timeout case
        with patch("app.ai.providers.get_model_provider", side_effect=TimeoutError("Request timed out")):
            state: TeachingState = {
                "learner_query": "I divide the array by finding mid and adjusting pointer boundaries left = mid + 1",
                "target_id": "Binary Search",
                "citations": sample_grounded_evidence,
            }
            res = teach_evaluate_response_node(state)
            assert res["assessment_score"] is not None
            assert res["assessment_evaluation"] is not None

        # Malformed output without score: [0-100]
        mock_provider = MagicMock()
        mock_provider.generate_text.return_value = MagicMock(content="Good work! Your approach is interesting but keep practicing.")
        with patch("app.ai.providers.get_model_provider", return_value=mock_provider):
            res_malformed = teach_evaluate_response_node(state)
            assert res_malformed["assessment_score"] is not None
            assert res_malformed["assessment_evaluation"]["score"] is not None

    def test_skip_retrieval_with_low_similarity_evidence_enforces_gate(self):
        """Fix 2: skip_retrieval=True with low-similarity evidence does NOT authorize grounded explanation."""
        low_sim_evidence = [
            {
                "source_type": "technical_source",
                "title": "Random Recipe for Pancakes",
                "similarity": 0.10,
                "similarity_score": 0.10,
                "excerpt": "Mix flour, eggs, and milk.",
            }
        ]
        state: TeachingState = {
            "learner_query": "Explain quantum flux capacitors",
            "target_id": "Quantum Flux",
            "skip_retrieval": True,
            "retrieved_evidence": low_sim_evidence,
            "status": "initialized",
        }
        workflow = TeachingAgentWorkflow()
        res = workflow.run(state)

        # Gate must evaluate low similarity as insufficient and route to general_overview
        assert res["pedagogical_decision"] == "general_overview"
        assert res["evidence_sufficiency"] == "insufficient"
        assert res["citations"] == []
        assert "Course Materials Notice" in res["tutor_reply"]

    def test_skip_retrieval_with_unrelated_evidence_enforces_gate(self):
        """Fix 2: skip_retrieval=True with unrelated evidence cannot authorize code demonstration."""
        unrelated_evidence = [
            {
                "source_type": "course_material",
                "title": "Ancient_History_101.pdf",
                "filename": "Ancient_History_101.pdf",
                "page_number": 5,
                "similarity": 0.15,
                "similarity_score": 0.15,
                "excerpt": "The Roman Empire expanded across the Mediterranean.",
            }
        ]
        state: TeachingState = {
            "learner_query": "Show me python code for distributed consensus Paxos",
            "learner_intent": "code_walkthrough",
            "target_id": "Paxos",
            "skip_retrieval": True,
            "retrieved_evidence": unrelated_evidence,
            "status": "initialized",
        }
        workflow = TeachingAgentWorkflow()
        res = workflow.run(state)

        assert res["pedagogical_decision"] == "general_overview"
        assert res["citations"] == []

    def test_valid_evidence_meets_gate_threshold(self, sample_grounded_evidence):
        """Fix 2: Valid evidence meeting gate threshold authorizes grounded explanation."""
        state: TeachingState = {
            "learner_query": "Explain binary search invariants",
            "target_id": "Binary Search",
            "skip_retrieval": True,
            "retrieved_evidence": sample_grounded_evidence,
            "status": "initialized",
        }
        workflow = TeachingAgentWorkflow()
        res = workflow.run(state)

        assert res["pedagogical_decision"] == "explain"
        assert res["evidence_sufficiency"] == "sufficient"
        assert len(res["citations"]) >= 1

    def test_missing_evidence_and_missing_sufficiency_fails_safely(self):
        """Fix 2: When evidence and sufficiency metadata are both missing, fails safely to general_overview."""
        state: TeachingState = {
            "learner_query": "Explain microservices transaction boundaries",
            "target_id": "Saga Pattern",
            "retrieved_evidence": [],
            "status": "retrieved",
        }
        dec_out = prepare_teaching_decision_node(state)

        assert dec_out["pedagogical_decision"] == "general_overview"
        assert dec_out["evidence_sufficiency"] == "insufficient"
        assert dec_out["citations"] == []

    def test_ambiguous_query_suppresses_citations_and_clarifies(self, sample_grounded_evidence):
        """Fix 2: Ambiguous query short-circuits directly to clarification with zero citations."""
        state: TeachingState = {
            "learner_query": "code?",
            "target_id": "General",
            "is_ambiguous": True,
            "retrieved_evidence": sample_grounded_evidence,
            "status": "analyzed",
        }
        dec_out = prepare_teaching_decision_node(state)

        assert dec_out["pedagogical_decision"] == "clarify"
        assert dec_out["evidence_sufficiency"] == "ambiguous"
        assert dec_out["citations"] == []

    def test_citation_suppression_when_evidence_is_insufficient(self):
        """Fix 2: Citations are strictly empty in final response when evidence is insufficient."""
        state: TeachingState = {
            "learner_query": "How do hyperspace engines work?",
            "target_id": "Hyperspace",
            "evidence_sufficiency": "insufficient",
            "retrieved_evidence": [],
            "status": "retrieved",
        }
        workflow = TeachingAgentWorkflow()
        res = workflow.run(state)

        assert res["pedagogical_decision"] == "general_overview"
        assert res["citations"] == []
        assert res["structured_response"]["citations"] == []

    def test_assessment_with_sufficient_evidence_grounded(self, sample_grounded_evidence):
        """Fix 3: Assessment with sufficient course evidence evaluates answer and retains course citations."""
        state: TeachingState = {
            "learner_query": "Here is my answer: We set mid = (left + right) // 2 and move left = mid + 1",
            "workspace_code": "left, right = 0, len(arr) - 1\nwhile left <= right:\n    mid = (left + right) // 2\n    if arr[mid] == target: return mid\n    elif arr[mid] < target: left = mid + 1\n    else: right = mid - 1",
            "target_id": "Binary Search",
            "mode": "assessment",
            "is_assessment": True,
            "retrieved_evidence": sample_grounded_evidence,
            "evidence_sufficiency": "sufficient",
            "status": "retrieved",
        }
        dec_out = prepare_teaching_decision_node(state)

        assert dec_out["pedagogical_decision"] == "evaluate_response"
        assert dec_out["evidence_sufficiency"] == "sufficient"
        assert dec_out["grounding_type"] in ("course_material_grounded", "source_grounded")
        assert len(dec_out["citations"]) >= 1

    def test_assessment_without_course_evidence_evaluates_general_technical(self):
        """Fix 3: Assessment without course evidence evaluates against general technical principles with zero course citations."""
        state: TeachingState = {
            "learner_query": "Here is my answer: We set mid = (left + right) // 2 and move left = mid + 1",
            "workspace_code": "left, right = 0, len(arr) - 1\nwhile left <= right:\n    mid = (left + right) // 2\n    if arr[mid] == target: return mid\n    elif arr[mid] < target: left = mid + 1\n    else: right = mid - 1",
            "target_id": "Binary Search",
            "mode": "assessment",
            "is_assessment": True,
            "retrieved_evidence": [],
            "evidence_sufficiency": "insufficient",
            "status": "retrieved",
        }
        workflow = TeachingAgentWorkflow()
        with patch("app.ai.providers.get_model_provider", side_effect=RuntimeError("Provider offline")):
            res = workflow.run(state)

        assert res["status"] == "completed"
        assert res["pedagogical_decision"] == "evaluate_response"
        assert res["demonstrated_understanding"] is True
        assert res["assessment_score"] >= 80
        # No course materials -> Citations must be strictly empty (no fabricated citations)
        assert res["citations"] == []
        assert res["structured_response"]["citations"] == []

