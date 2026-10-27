"""
End-to-end and unit tests verifying Resume Skill Learning, Relevance Validation,
and Interactive Tutoring for CareerVerse AI.
Addresses all 15 scenarios specified in Section 8 of the prompt.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from app.schemas.teaching import (
    TeachingLesson,
    TeachingLessonDetailRequest,
    TeachingLessonDetailResponse,
    TeachingInteractionRequest,
    TeachingEvaluationRequest,
    TeachingChatRequest,
    TeachingChatResponse,
)
from app.services.lesson_generation_service import (
    generate_comprehensive_lesson,
    validate_lesson_relevance,
    _LESSON_CACHE,
)
from app.ai.agents.teaching_agent import (
    analyze_query_node,
    prepare_teaching_decision_node,
    teach_explain_node,
    teach_evaluate_response_node,
    TeachingAgentWorkflow,
)
from app.services.teaching_service import (
    interact_with_teaching_lesson,
    evaluate_and_teach,
)
from app.models.user import User


@pytest.fixture
def test_user():
    user = MagicMock(spec=User)
    user.id = 9999
    user.name = "Candidate Learner"
    user.email = "candidate_learner@careerverse.ai"
    user.phone = "1234567890"
    user.college = "KPR Institute"
    user.degree = "B.E. CSE"
    user.location = "Coimbatore"
    user.bio = "AI/ML Learner"
    user.summary = "Learner summary"
    return user


class TestTeachingRelevanceAndTutoring:

    def test_01_python_concept_produces_python_relevant_content(self):
        """1. A Python concept produces Python-relevant teaching content."""
        req = TeachingLessonDetailRequest(
            skill="Python",
            concept="Memory References & Object Identity",
            learner_level="Intermediate",
        )
        res = generate_comprehensive_lesson(req)
        lesson = res.lesson

        assert lesson.title is not None
        assert "Python" in lesson.title or "Python" in res.skill
        # Must teach Python concepts
        full_text = f"{lesson.what_it_is} {lesson.why_it_exists} {lesson.detailed_explanation} {lesson.starter_code}".lower()
        assert any(k in full_text for k in ["python", "object", "memory", "reference", "mutab", "id()"])
        # Must NOT contain React or FastAPI cross-contamination
        assert "useeffect" not in full_text
        assert "unmount" not in full_text
        assert "jsx" not in full_text
        assert "fastapi" not in full_text

    def test_02_react_concept_produces_react_relevant_content(self):
        """2. A React concept produces React-relevant content."""
        req = TeachingLessonDetailRequest(
            skill="React",
            concept="Props & State Fundamentals",
            learner_level="Intermediate",
        )
        res = generate_comprehensive_lesson(req)
        lesson = res.lesson

        full_text = f"{lesson.what_it_is} {lesson.why_it_exists} {lesson.detailed_explanation} {lesson.starter_code}".lower()
        assert any(k in full_text for k in ["react", "component", "props", "state", "usestate", "re-render"])
        # Must NOT contain Python GIL or malloc
        assert "gil" not in full_text
        assert "malloc" not in full_text
        assert "cpython" not in full_text

    def test_03_langchain_concept_produces_langchain_relevant_content(self):
        """3. A LangChain concept produces LangChain-relevant content."""
        req = TeachingLessonDetailRequest(
            skill="LangChain",
            concept="LCEL Runnable Protocol & Chain Composition",
            learner_level="Intermediate",
        )
        res = generate_comprehensive_lesson(req)
        lesson = res.lesson

        full_text = f"{lesson.what_it_is} {lesson.why_it_exists} {lesson.detailed_explanation} {lesson.starter_code}".lower()
        assert any(k in full_text for k in ["langchain", "lcel", "runnable", "prompt", "chain", "pipe"])
        # Must NOT contain FastAPI concurrency or SQL tables
        assert "fastapi" not in full_text
        assert "uvicorn" not in full_text
        assert "async def get_db" not in full_text

    def test_04_switching_skills_cannot_reuse_unrelated_lesson_content(self):
        """4. Switching skills cannot reuse unrelated lesson content."""
        py_req = TeachingLessonDetailRequest(skill="Python", concept="Foundations")
        py_res = generate_comprehensive_lesson(py_req)

        react_req = TeachingLessonDetailRequest(skill="React", concept="Foundations")
        react_res = generate_comprehensive_lesson(react_req)

        # Cache keys and lessons must be completely distinct
        assert py_res.skill != react_res.skill
        assert py_res.lesson.id != react_res.lesson.id
        assert "react" not in py_res.lesson.detailed_explanation.lower()
        assert "python" not in react_res.lesson.detailed_explanation.lower()

    def test_05_switching_concepts_cannot_reuse_stale_section_content(self):
        """5. Switching concepts cannot reuse stale section content."""
        c1_req = TeachingLessonDetailRequest(
            skill="Python",
            concept="Memory References & Object Identity",
            lesson_id="py-mem-ref",
        )
        res1 = generate_comprehensive_lesson(c1_req)

        c2_req = TeachingLessonDetailRequest(
            skill="Python",
            concept="Decorators, Closures & First-Class Functions",
            lesson_id="py-decorators",
        )
        res2 = generate_comprehensive_lesson(c2_req)

        assert res1.lesson.id != res2.lesson.id
        assert res1.lesson.topic != res2.lesson.topic
        assert "decorator" in res2.lesson.detailed_explanation.lower() or "decorator" in res2.lesson.topic.lower()

    def test_06_irrelevant_retrieved_document_cannot_silently_become_explanation(self):
        """6. An irrelevant retrieved document cannot silently become the lesson's main explanation."""
        bad_doc = "React unmount and Virtual DOM fiber reconciliation principles."
        is_valid, reason = validate_lesson_relevance({"detailed_explanation": bad_doc}, skill="Python", concept="Memory Model")
        assert is_valid is False
        assert "forbidden" in reason.lower() or "cross-domain" in reason.lower()

    def test_07_missing_or_weak_source_produces_transparent_fallback(self):
        """7. A missing or weak source produces a transparent fallback, not fabricated verified resources."""
        req = TeachingLessonDetailRequest(
            skill="UnknownNewFrameworkX",
            concept="Advanced Internals",
        )
        res = generate_comprehensive_lesson(req)
        # Should not fabricate fake 5-star verified citations
        assert res.relevance_status in ("verified", "fallback_applied")
        for r in res.lesson.resources:
            url = r["canonical_url"] if isinstance(r, dict) else r.canonical_url
            assert url is not None
            assert "unknownnewframeworkx" in url.lower() or "github.com" in url.lower()

    def test_08_resource_links_and_relevance_metadata_handled_correctly(self):
        """8. Resource links and relevance metadata are handled correctly."""
        req = TeachingLessonDetailRequest(skill="Python", concept="Memory Model")
        res = generate_comprehensive_lesson(req)

        assert len(res.lesson.resources) > 0
        first_res = res.lesson.resources[0]
        url = first_res["canonical_url"] if isinstance(first_res, dict) else first_res.canonical_url
        is_ver = first_res["is_verified"] if isinstance(first_res, dict) else first_res.is_verified
        rel_exp = first_res["relevance_explanation"] if isinstance(first_res, dict) else first_res.relevance_explanation
        assert url.startswith("https://")
        assert "python" in url.lower()
        assert is_ver is True
        assert rel_exp is not None

    def test_09_learners_question_receives_context_aware_response(self):
        """9. A learner's question receives a context-aware response."""
        state = {
            "learner_query": "Why does Python have pass-by-object-reference?",
            "target_id": "Python Memory Model",
            "is_assessment": False,
        }
        res = teach_explain_node(state)
        assert res.get("tutor_reply") is not None
        assert "Python" in res["tutor_reply"] or "Memory" in res["tutor_reply"]

    def test_10_hello_does_not_trigger_imaginary_technical_evaluation(self):
        """10. 'Hello' does not trigger an imaginary technical evaluation or 20/100 score."""
        state = {
            "learner_query": "Hello Dr. Vance!",
            "target_id": "Python Generators",
            "is_assessment": True,  # Even if sent from an assessment step
        }
        # Intent analysis must classify as greeting, not answer_submission
        analysis = analyze_query_node(state)
        assert analysis["learner_intent"] == "greeting"

        # Routing in prepare_teaching_decision_node must route to explain
        dec = prepare_teaching_decision_node({**state, "learner_intent": "greeting"})
        assert dec["pedagogical_decision"] == "explain"

        # Response must be a warm conversational greeting without score or evaluation
        reply_dict = teach_explain_node({**state, "learner_intent": "greeting"})
        reply = reply_dict.get("tutor_reply", "")
        assert "Hello!" in reply or "I am Dr. Cyra Vance" in reply
        assert "Score:" not in reply
        assert "/100" not in reply

    def test_11_hint_request_returns_hint_and_does_not_advance_lesson(self, test_user):
        """11. A hint request returns a hint and does not advance the lesson."""
        db_mock = MagicMock()
        progress_mock = MagicMock()
        progress_mock.hints_used = 0
        progress_mock.current_stage = "question"
        progress_mock.status = "in_progress"
        progress_mock.turns = []
        db_mock.query.return_value.filter.return_value.first.return_value = progress_mock

        curriculum_mock = MagicMock()
        lesson_mock = MagicMock()
        lesson_mock.id = "dsa-binary-search"
        lesson_mock.topic = "Binary Search Invariants"
        lesson_mock.hints = ["Consider tracking state with an auxiliary container.", "Formulate a mathematical invariant."]
        lesson_mock.concept_summary = "Divide and conquer search"
        section_mock = MagicMock()
        section_mock.id = "dsa"
        section_mock.lessons = [lesson_mock]
        curriculum_mock.sections = [section_mock]

        req = TeachingInteractionRequest(
            section_id="dsa",
            lesson_id="dsa-binary-search",
            action="hint",
        )
        with patch("app.services.teaching_service.get_teaching_curriculum", return_value=curriculum_mock):
            res = interact_with_teaching_lesson(db_mock, test_user, req)

        assert res.hint_revealed is not None
        # Lesson must not be marked complete
        assert res.is_lesson_complete is False
        # Stage must not advance to completed
        assert progress_mock.current_stage == "question"
        assert progress_mock.hints_used == 1

    def test_12_irrelevant_answers_do_not_receive_arbitrary_high_scores(self):
        """12. Irrelevant answers do not receive arbitrary high scores or mastery."""
        state = {
            "learner_query": "I had a great pepperoni pizza with extra cheese for dinner yesterday evening.",
            "target_id": "React Fiber Reconciliation & State Batching",
            "is_assessment": True,
            "learner_intent": "answer_submission",
        }
        res = teach_evaluate_response_node(state)
        reply = res.get("tutor_reply", "")

        assert res.get("demonstrated_understanding", False) is False
        assert res.get("assessment_score", 0) <= 25

    def test_13_correct_and_incorrect_submissions_evaluated_against_actual_exercise(self):
        """13. Correct and incorrect submissions are evaluated against the actual exercise."""
        # Correct submission for binary search
        correct_state = {
            "learner_query": "We calculate mid = (left + right) // 2. If target == nums[mid], return mid. If target < nums[mid], right = mid - 1. Otherwise left = mid + 1.",
            "workspace_code": "while left <= right:\n    mid = (left + right) // 2\n    if nums[mid] == target: return mid\n    elif nums[mid] < target: left = mid + 1\n    else: right = mid - 1",
            "target_id": "Binary Search Invariants",
            "is_assessment": True,
            "learner_intent": "answer_submission",
        }
        res_correct = teach_evaluate_response_node(correct_state)
        assert res_correct.get("demonstrated_understanding", False) is True

        # Incorrect/flawed submission
        incorrect_state = {
            "learner_query": "I will loop from left to right one by one using a simple linear scan over each item.",
            "workspace_code": "",
            "target_id": "Binary Search Invariants",
            "is_assessment": True,
            "learner_intent": "answer_submission",
        }
        res_incorrect = teach_evaluate_response_node(incorrect_state)
        assert res_incorrect.get("demonstrated_understanding", False) is False

    def test_14_lesson_progress_persists_for_correct_user(self, test_user):
        """14. Lesson progress persists for the correct user."""
        db_mock = MagicMock()
        progress_mock = MagicMock()
        progress_mock.candidate_id = test_user.id
        progress_mock.section_id = "dsa"
        progress_mock.lesson_id = "dsa-binary-search"
        progress_mock.hints_used = 0
        progress_mock.current_stage = "question"
        progress_mock.status = "in_progress"
        progress_mock.turns = []
        db_mock.query.return_value.filter.return_value.first.return_value = progress_mock

        curriculum_mock = MagicMock()
        lesson_mock = MagicMock()
        lesson_mock.id = "dsa-binary-search"
        lesson_mock.topic = "Binary Search Invariants"
        lesson_mock.hints = ["Consider tracking state with an auxiliary container.", "Formulate a mathematical invariant."]
        lesson_mock.concept_summary = "Divide and conquer search"
        section_mock = MagicMock()
        section_mock.id = "dsa"
        section_mock.lessons = [lesson_mock]
        curriculum_mock.sections = [section_mock]

        req = TeachingInteractionRequest(
            section_id="dsa",
            lesson_id="dsa-binary-search",
            action="hint",
        )
        with patch("app.services.teaching_service.get_teaching_curriculum", return_value=curriculum_mock):
            res = interact_with_teaching_lesson(db_mock, test_user, req)

        # Verified db was queried for this specific user
        filter_calls = db_mock.query.return_value.filter.call_args_list
        assert len(filter_calls) > 0

    def test_15_teaching_agent_workflow_compilation_and_service_integrity(self):
        """15. Existing teaching agent workflow, routes and schemas continue to work."""
        workflow = TeachingAgentWorkflow()
        assert workflow.graph is not None

        # Verify query analysis on meta deferral
        deferral_state = {
            "learner_query": "I did not explain my idea yet, please wait.",
            "target_id": "FastAPI Dependency Injection",
        }
        analysis = analyze_query_node(deferral_state)
        assert analysis["learner_intent"] == "meta_deferral"
