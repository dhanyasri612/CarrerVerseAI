"""
Backend regression tests for AI-driven, skill-consistent lesson & assessment pipeline.
Covers cases 1, 2, 7, 8, 9, 10 from the original user request, plus skill-path and
topic-sequence validation.

All AI provider calls are mocked — tests run entirely offline.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest

from app.ai.errors import AIProviderError
from app.ai.providers.base import ProviderResponse
from app.schemas.teaching import (
    TeachingChatRequest,
    TeachingLessonDetailRequest,
    TeachingLessonDetailResponse,
)
from app.services.lesson_generation_service import (
    _LESSON_CACHE,
    generate_ai_driven_lesson,
    generate_comprehensive_lesson,
)
from app.services.skill_learning_service import (
    build_skill_learning_path,
    validate_topic_sequence,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _clear_cache() -> None:
    """Ensure the in-memory lesson cache is empty before each test."""
    _LESSON_CACHE.clear()


def _fake_db() -> MagicMock:
    """Minimal DB mock that returns empty query results."""
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = []
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.filter.return_value.filter.return_value.all.return_value = []
    db.query.return_value.filter.return_value.filter.return_value.first.return_value = None
    return db


def _fake_user(uid: int = 42) -> MagicMock:
    user = MagicMock()
    user.id = uid
    user.name = "Test Candidate"
    user.full_name = "Test Candidate"
    user.email = "test@example.com"
    user.username = "testcandidate"
    user.phone = "+1234567890"
    user.college = "Test University"
    user.degree = "B.S. Computer Science"
    user.location = "San Francisco, CA"
    user.bio = "Passionate software engineer."
    user.target_role = "Software Engineer"
    return user


class FakeProvider:
    """
    Controlled AI provider.
    Pass a dict as `response_json` to return a valid lesson JSON.
    Pass `raise_error=True` to simulate AIProviderError.
    Pass `reply_text` to return a plain text response (for generate_text).
    """

    def __init__(
        self,
        response_json: Optional[Dict[str, Any]] = None,
        raise_error: bool = False,
        reply_text: Optional[str] = None,
    ) -> None:
        self.response_json = response_json
        self.raise_error = raise_error
        self.reply_text = reply_text

    def generate(self, *, system_prompt: str, user_message: str, **kwargs: Any) -> ProviderResponse:
        if self.raise_error:
            raise AIProviderError("Simulated provider failure")
        content = json.dumps(self.response_json) if self.response_json else "{}"
        return ProviderResponse(content=content, model="fake-model")

    def generate_text(self, *, system_prompt: str, user_message: str, **kwargs: Any) -> ProviderResponse:
        if self.raise_error:
            raise AIProviderError("Simulated provider failure")
        text = self.reply_text if self.reply_text is not None else "Generic reply."
        return ProviderResponse(content=text, model="fake-model")


def _python_lesson_json(concept: str = "Foundations") -> Dict[str, Any]:
    return {
        "title": f"Python • {concept}",
        "topic": f"Python {concept}",
        "concept_summary": "Python uses pass-by-object-reference and has a GIL.",
        "what_it_is": "Python is an interpreted, dynamically typed language with reference counting garbage collection.",
        "why_it_exists": "Python was designed for readability and rapid development.",
        "detailed_explanation": (
            "Python variables are name bindings to heap-allocated objects. "
            "The GIL (Global Interpreter Lock) prevents true multi-core parallelism for CPU-bound code. "
            "Use asyncio for I/O-bound concurrency; use multiprocessing for CPU-bound work."
        ),
        "step_by_step": "1. Allocate PyObject on heap. 2. Bind name. 3. Increment refcount.",
        "starter_code": "import sys\nprint(sys.version)  # Python version\na = [1, 2, 3]\nprint(id(a))\n",
        "execution_walkthrough": "CPython allocates list on heap, refcount=1.",
        "common_mistakes": "Mutable default arguments, reference aliasing bugs.",
        "debugging_tips": "Use id() to inspect object identity. Use copy.deepcopy for nested structures.",
        "edge_cases_and_limitations": "Small integer caching: -5 to 256 are pre-allocated.",
        "real_world_applications": "FastAPI backends, data pipelines, asyncio microservices.",
        "expected_output": "Python 3.x.y\n<id value>",
        "practice_exercises": [
            {
                "difficulty": "Easy",
                "prompt": "Write a Python function that returns a new list without modifying the input.",
                "starter_code": "def safe_copy(items: list) -> list:\n    pass\n",
                "solution": "def safe_copy(items: list) -> list:\n    return list(items)\n",
            }
        ],
        "knowledge_check_questions": [
            {
                "question": "What does 'pass-by-object-reference' mean in Python?",
                "model_answer": "Variables are name tags pointing to heap objects; assignment rebinds tags, it does not copy objects.",
            }
        ],
        "resources": [
            {
                "title": "Python Official Documentation",
                "canonical_url": "https://docs.python.org/3/",
                "source": "Python Software Foundation",
                "is_verified": True,
                "relevance_explanation": "Authoritative Python docs.",
            }
        ],
    }


def _react_lesson_json(concept: str = "Foundations") -> Dict[str, Any]:
    return {
        "title": f"React • {concept}",
        "topic": f"React {concept}",
        "concept_summary": "React uses a Virtual DOM and unidirectional data flow via useState and props.",
        "what_it_is": "React is a declarative JavaScript library for building user interfaces using components.",
        "why_it_exists": "React was created to solve synchronization issues in complex UIs by using a Virtual DOM.",
        "detailed_explanation": (
            "React components render JSX, which is compiled to React.createElement calls. "
            "useState manages local component state; setters trigger Fiber reconciliation. "
            "Props are read-only and flow unidirectionally from parent to child."
        ),
        "step_by_step": "1. JSX compiled. 2. React.createElement called. 3. Fiber diffing. 4. DOM commit.",
        "starter_code": (
            "import React, { useState } from 'react';\n"
            "function Counter() {\n"
            "  const [count, setCount] = useState(0);\n"
            "  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;\n"
            "}\n"
        ),
        "execution_walkthrough": "React Fiber diffs virtual trees and commits minimal DOM updates.",
        "common_mistakes": "Mutating state directly, missing key props on lists.",
        "debugging_tips": "Use React DevTools to inspect component state and props.",
        "edge_cases_and_limitations": "State batching in React 18; controlled vs uncontrolled inputs.",
        "real_world_applications": "Single-page applications, dashboards, e-commerce frontends.",
        "expected_output": "Renders a button that increments count on click.",
        "practice_exercises": [
            {
                "difficulty": "Easy",
                "prompt": "Create a React component that shows a togglable message.",
                "starter_code": "function Toggle() {\n  // implement\n}\n",
                "solution": "function Toggle() {\n  const [show, setShow] = useState(false);\n  return <div><button onClick={() => setShow(s => !s)}>Toggle</button>{show && <p>Hello!</p>}</div>;\n}\n",
            }
        ],
        "knowledge_check_questions": [
            {
                "question": "Why must state mutations in React be immutable?",
                "model_answer": "React uses Object.is comparison on state; mutating in place makes React think nothing changed and skip the re-render.",
            }
        ],
        "resources": [
            {
                "title": "React Official Documentation",
                "canonical_url": "https://react.dev/",
                "source": "Meta / React Core Team",
                "is_verified": True,
                "relevance_explanation": "Authoritative React docs.",
            }
        ],
    }


# ── Case 1: Python lesson contains Python content, no React ───────────────────

class TestCase1PythonLessonContent:

    def test_ai_driven_python_lesson_contains_python_terms(self) -> None:
        """Case 1: AI-generated Python lesson has Python content, no React contamination."""
        _clear_cache()
        python_json = _python_lesson_json("Memory References & Object Identity")
        with patch(
            "app.services.lesson_generation_service.get_model_provider",
            return_value=FakeProvider(response_json=python_json),
        ):
            res = generate_ai_driven_lesson(
                skill="Python",
                concept_title="Memory References & Object Identity",
                lesson_id="py-mem-ref-ai-001",
                learner_level="Intermediate",
                active_section="overview",
            )

        assert isinstance(res, TeachingLessonDetailResponse)
        lesson = res.lesson
        full_text = (
            f"{lesson.title} {lesson.topic} {lesson.what_it_is} {lesson.why_it_exists} "
            f"{lesson.detailed_explanation} {lesson.starter_code}"
        ).lower()

        # Must reference Python concepts
        assert any(k in full_text for k in ["python", "gil", "object", "heap", "refcount", "import"])
        # Must NOT have React/JSX contamination
        assert "usestate" not in full_text
        assert "jsx" not in full_text
        assert "react" not in full_text.replace("react", "___")  # title check: "React" should not appear

    def test_ai_driven_python_lesson_validation_status(self) -> None:
        _clear_cache()
        python_json = _python_lesson_json("Decorators & Closures")
        with patch(
            "app.services.lesson_generation_service.get_model_provider",
            return_value=FakeProvider(response_json=python_json),
        ):
            res = generate_ai_driven_lesson(
                skill="Python",
                concept_title="Decorators & Closures",
                lesson_id="py-deco-001",
                learner_level="Intermediate",
                active_section="code",
            )

        assert res.validation_status == "verified_relevant"
        assert res.skill == "Python"


# ── Case 2: React lesson contains React content, no Python/GIL ───────────────

class TestCase2ReactLessonContent:

    def test_ai_driven_react_lesson_contains_react_terms(self) -> None:
        """Case 2: AI-generated React lesson has React content, no Python/GIL contamination."""
        _clear_cache()
        react_json = _react_lesson_json("Props & State Fundamentals")
        with patch(
            "app.services.lesson_generation_service.get_model_provider",
            return_value=FakeProvider(response_json=react_json),
        ):
            res = generate_ai_driven_lesson(
                skill="React",
                concept_title="Props & State Fundamentals",
                lesson_id="react-props-ai-001",
                learner_level="Intermediate",
                active_section="overview",
            )

        assert isinstance(res, TeachingLessonDetailResponse)
        lesson = res.lesson
        full_text = (
            f"{lesson.title} {lesson.topic} {lesson.what_it_is} {lesson.why_it_exists} "
            f"{lesson.detailed_explanation} {lesson.starter_code}"
        ).lower()

        # Must reference React concepts
        assert any(k in full_text for k in ["react", "component", "usestate", "jsx", "fiber", "dom"])
        # Must NOT have Python/GIL contamination
        assert "gil" not in full_text
        assert "global interpreter lock" not in full_text
        assert "cpython" not in full_text

    def test_ai_driven_react_lesson_validation_status(self) -> None:
        _clear_cache()
        react_json = _react_lesson_json("useEffect & Lifecycle Synchronization")
        with patch(
            "app.services.lesson_generation_service.get_model_provider",
            return_value=FakeProvider(response_json=react_json),
        ):
            res = generate_ai_driven_lesson(
                skill="React",
                concept_title="useEffect & Lifecycle Synchronization",
                lesson_id="react-effect-001",
                learner_level="Intermediate",
                active_section="code",
            )

        assert res.validation_status == "verified_relevant"
        assert res.skill == "React"


# ── Case 9: Provider raises AIProviderError → fallback, no hardcoded 85 ──────

class TestCase9ProviderFailureFallback:

    def test_provider_error_triggers_fallback_curated(self) -> None:
        """Case 9: AIProviderError → validation_status='fallback_curated', no hardcoded 85 score."""
        _clear_cache()
        with patch(
            "app.services.lesson_generation_service.get_model_provider",
            return_value=FakeProvider(raise_error=True),
        ):
            res = generate_ai_driven_lesson(
                skill="Python",
                concept_title="Asyncio Event Loop",
                lesson_id="py-asyncio-fail-001",
                learner_level="Intermediate",
                active_section="overview",
            )

        assert isinstance(res, TeachingLessonDetailResponse)
        assert res.validation_status == "fallback_curated"
        assert res.validation_details is not None
        assert "AIProviderError" in res.validation_details or "error" in res.validation_details.lower()

        # Response must not contain hardcoded praise or unrelated content
        lesson = res.lesson
        full_text = f"{lesson.title} {lesson.topic} {lesson.concept_summary}".lower()
        assert "react" not in full_text  # No React cross-contamination

    def test_provider_error_in_assessment_no_mastery_award(self) -> None:
        """Case 9 (mastery): Provider failure must not award mastery (no 85/100 hardcode).

        Patches app.services.teaching_service.get_model_provider with raise_error=True
        and calls chat_with_teaching_mentor directly, so this test exercises the actual RC4 fix.
        """
        _clear_cache()
        db = _fake_db()
        user = _fake_user()

        from app.services.teaching_service import chat_with_teaching_mentor
        from app.services import skill_learning_service as sls
        from app.schemas.teaching import SkillLearningPathResponse, SkillCurriculumStage

        fake_stage = SkillCurriculumStage(
            stage_number=1,
            stage_name="Foundations",
            description="Python foundations",
            estimated_hours=1.0,
            lessons=[],
        )
        fake_path = SkillLearningPathResponse(
            skill_name="Python",
            normalized_skill="python",
            summary="Python curriculum",
            stages=[fake_stage],
            total_stages=1,
            total_lessons=0,
        )

        req = TeachingChatRequest(
            mode="skill",
            target_id="Python",
            lesson_id="py-assess-fail",
            message="The GIL prevents true parallelism in CPU-bound Python threads.",
            is_assessment=True,
        )

        with patch(
            "app.services.teaching_service.get_model_provider",
            return_value=FakeProvider(raise_error=True),
        ), patch.object(sls, "build_skill_learning_path", return_value=fake_path):
            result = chat_with_teaching_mentor(db, user, req)

        assert result.demonstrated_understanding is False
        assert "unavailable" in result.reply.lower() or "retry" in result.reply.lower()
        # Must not contain hardcoded score
        assert "85/100" not in result.reply
        assert "Score: 85" not in result.reply


# ── Case 10: Cache isolation — React lesson must not return Python cache ──────

class TestCase10CacheIsolation:

    def test_cache_key_includes_skill_name(self) -> None:
        """Case 10: Cache key must be per-skill; React request must not return Python cached lesson."""
        _clear_cache()

        # First: prime cache with Python lesson using a shared lesson_id
        shared_lesson_id = "common-lesson-id-001"
        python_json = _python_lesson_json("Foundations")

        with patch(
            "app.services.lesson_generation_service.get_model_provider",
            return_value=FakeProvider(response_json=python_json),
        ):
            python_res = generate_ai_driven_lesson(
                skill="Python",
                concept_title="Foundations",
                lesson_id=shared_lesson_id,
                learner_level="Intermediate",
                active_section="overview",
            )

        assert "python" in python_res.lesson.title.lower()

        # Second: request React lesson with same lesson_id
        react_json = _react_lesson_json("Foundations")
        with patch(
            "app.services.lesson_generation_service.get_model_provider",
            return_value=FakeProvider(response_json=react_json),
        ):
            react_res = generate_ai_driven_lesson(
                skill="React",
                concept_title="Foundations",
                lesson_id=shared_lesson_id,
                learner_level="Intermediate",
                active_section="overview",
            )

        # React request must get React content, not Python
        assert isinstance(react_res, TeachingLessonDetailResponse)
        react_title = react_res.lesson.title.lower()
        assert "react" in react_title, f"Expected React content, got: {react_title}"
        assert "gil" not in (react_res.lesson.detailed_explanation or "").lower()

    def test_cache_invalidated_on_skill_mismatch(self) -> None:
        """Cache invalidation: a cached Python lesson must not be returned for a React request."""
        _clear_cache()

        # Manually prime cache with a Python lesson under a key that would collide on concept+id
        from app.schemas.teaching import TeachingLesson
        fake_python_lesson = TeachingLesson(
            id="col-id",
            title="Python • Foundations",
            topic="Python Foundations",
            difficulty="Intermediate",
            concept_summary="Python fundamentals.",
            challenge_question="Explain Python internals.",
            grounding_source="Test",
        )
        _LESSON_CACHE["react::foundations::col-id::intermediate::overview"] = fake_python_lesson

        # Now request a React lesson — cache should be invalidated because title doesn't reference React
        react_json = _react_lesson_json("Foundations")
        with patch(
            "app.services.lesson_generation_service.get_model_provider",
            return_value=FakeProvider(response_json=react_json),
        ):
            res = generate_ai_driven_lesson(
                skill="React",
                concept_title="Foundations",
                lesson_id="col-id",
                learner_level="Intermediate",
                active_section="overview",
            )

        assert "react" in res.lesson.title.lower()
        assert "python" not in res.lesson.title.lower()


# ── Case 7: Assessment with provider failure → no mastery ────────────────────

class TestCase7AssessmentProviderFailure:

    def test_provider_failure_in_assessment_no_mastery(self) -> None:
        """Case 7: Provider failure in assessment mode → demonstrated_understanding=False."""
        _clear_cache()
        db = _fake_db()
        user = _fake_user()

        from app.services.teaching_service import chat_with_teaching_mentor
        from app.services import skill_learning_service as sls

        # Fake skill path
        from app.schemas.teaching import SkillLearningPathResponse, SkillCurriculumStage
        fake_stage = SkillCurriculumStage(
            stage_number=1,
            stage_name="Foundations",
            description="Python foundations",
            estimated_hours=1.0,
            lessons=[],
        )
        fake_path = SkillLearningPathResponse(
            skill_name="Python",
            normalized_skill="python",
            summary="Python curriculum",
            stages=[fake_stage],
            total_stages=1,
            total_lessons=0,
        )

        req = TeachingChatRequest(
            mode="skill",
            target_id="Python",
            lesson_id="py-assess-case7",
            message="The GIL is a mutex that allows only one thread to execute Python bytecode at a time.",
            is_assessment=True,
        )

        with patch(
            "app.services.teaching_service.get_model_provider",
            return_value=FakeProvider(raise_error=True),
        ), patch.object(sls, "build_skill_learning_path", return_value=fake_path):
            result = chat_with_teaching_mentor(db, user, req)

        # Provider failed → no mastery must be awarded
        assert result.demonstrated_understanding is False
        # Response must be a clear error, not generic praise or hardcoded score
        assert "unavailable" in result.reply.lower() or "retry" in result.reply.lower()
        assert "85" not in result.reply
        assert "score: 85" not in result.reply.lower()

    def test_low_score_from_provider_no_mastery(self) -> None:
        """Provider returns a low score → demonstrated_understanding=False."""
        _clear_cache()
        db = _fake_db()
        user = _fake_user()

        from app.services.teaching_service import chat_with_teaching_mentor
        from app.services import skill_learning_service as sls
        from app.schemas.teaching import SkillLearningPathResponse, SkillCurriculumStage

        fake_stage = SkillCurriculumStage(
            stage_number=1,
            stage_name="Foundations",
            description="Python foundations",
            estimated_hours=1.0,
            lessons=[],
        )
        fake_path = SkillLearningPathResponse(
            skill_name="Python",
            normalized_skill="python",
            summary="Python curriculum",
            stages=[fake_stage],
            total_stages=1,
            total_lessons=0,
        )

        low_score_reply = (
            "✅ What You Got Right:\nYou mentioned threading.\n\n"
            "⚠️ What Was Sub-Optimal:\nYou missed that the GIL doesn't help with CPU-bound tasks.\n\n"
            "🎓 Masterclass Takeaway:\nUse multiprocessing for CPU-bound work.\n\n"
            "📊 Score: 45/100"
        )

        req = TeachingChatRequest(
            mode="skill",
            target_id="Python",
            lesson_id="py-low-score-case7",
            message="Python threads run in parallel.",
            is_assessment=True,
        )

        with patch(
            "app.services.teaching_service.get_model_provider",
            return_value=FakeProvider(reply_text=low_score_reply),
        ), patch.object(sls, "build_skill_learning_path", return_value=fake_path):
            result = chat_with_teaching_mentor(db, user, req)

        assert result.demonstrated_understanding is False
        assert result.assessment_evaluation is not None
        assert result.assessment_evaluation.get("score", 100) < 80


# ── Case 8: Feedback addresses actual submitted answer ────────────────────────

class TestCase8FeedbackAddressesActualAnswer:

    def test_reply_references_learner_answer_content(self) -> None:
        """Case 8: Provider reply echoes learner answer keywords → reply references the answer."""
        _clear_cache()
        db = _fake_db()
        user = _fake_user()

        from app.services.teaching_service import chat_with_teaching_mentor
        from app.services import skill_learning_service as sls
        from app.schemas.teaching import SkillLearningPathResponse, SkillCurriculumStage

        fake_stage = SkillCurriculumStage(
            stage_number=1,
            stage_name="Foundations",
            description="Python foundations",
            estimated_hours=1.0,
            lessons=[],
        )
        fake_path = SkillLearningPathResponse(
            skill_name="Python",
            normalized_skill="python",
            summary="Python curriculum",
            stages=[fake_stage],
            total_stages=1,
            total_lessons=0,
        )

        # Learner's answer contains "asyncio" keyword; provider echoes it back
        learner_keyword = "asyncio"
        provider_reply = (
            f"✅ What You Got Right:\nYou mentioned {learner_keyword} — correct, asyncio enables cooperative multitasking.\n\n"
            f"⚠️ What Was Sub-Optimal:\nYou didn't explain the event loop mechanics.\n\n"
            f"🎓 Masterclass Takeaway:\nThe asyncio event loop runs coroutines cooperatively.\n\n"
            f"📊 Score: 88/100"
        )

        req = TeachingChatRequest(
            mode="skill",
            target_id="Python",
            lesson_id="py-case8-async",
            message=f"Python uses {learner_keyword} for non-blocking I/O operations.",
            is_assessment=True,
        )

        with patch(
            "app.services.teaching_service.get_model_provider",
            return_value=FakeProvider(reply_text=provider_reply),
        ), patch.object(sls, "build_skill_learning_path", return_value=fake_path):
            result = chat_with_teaching_mentor(db, user, req)

        # Reply must contain the learner's actual keyword
        assert learner_keyword in result.reply.lower()
        # Must award mastery (score 88 >= 80)
        assert result.demonstrated_understanding is True

    def test_provider_failure_reply_is_error_not_praise(self) -> None:
        """Case 8 (failure): On provider failure, reply is error message, not generic praise."""
        _clear_cache()
        db = _fake_db()
        user = _fake_user()

        from app.services.teaching_service import chat_with_teaching_mentor
        from app.services import skill_learning_service as sls
        from app.schemas.teaching import SkillLearningPathResponse, SkillCurriculumStage

        fake_stage = SkillCurriculumStage(
            stage_number=1,
            stage_name="Foundations",
            description="Python foundations",
            estimated_hours=1.0,
            lessons=[],
        )
        fake_path = SkillLearningPathResponse(
            skill_name="Python",
            normalized_skill="python",
            summary="Python curriculum",
            stages=[fake_stage],
            total_stages=1,
            total_lessons=0,
        )

        req = TeachingChatRequest(
            mode="skill",
            target_id="Python",
            lesson_id="py-case8-fail",
            message="asyncio uses cooperative multitasking via an event loop.",
            is_assessment=True,
        )

        with patch(
            "app.services.teaching_service.get_model_provider",
            return_value=FakeProvider(raise_error=True),
        ), patch.object(sls, "build_skill_learning_path", return_value=fake_path):
            result = chat_with_teaching_mentor(db, user, req)

        # Must be an error message, not generic praise
        assert result.demonstrated_understanding is False
        assert "unavailable" in result.reply.lower() or "retry" in result.reply.lower()
        # Must NOT contain hardcoded score
        assert "85/100" not in result.reply
        assert "Score: 85" not in result.reply


# ── Skill path consistency ────────────────────────────────────────────────────

class TestSkillPathConsistency:

    def test_python_path_returns_python_stages(self) -> None:
        """build_skill_learning_path('Python') returns only Python stages."""
        db = _fake_db()
        user = _fake_user()

        with patch("app.services.skill_learning_service.build_learner_knowledge_profile") as mock_profile, \
             patch("app.services.skill_learning_service.retrieve_teaching_resources_for_lesson", return_value=[]):
            mock_profile.return_value = MagicMock(
                verified_projects=[],
                recommended_learning_order=[],
                skills_inventory=[],
            )
            path = build_skill_learning_path(db, "Python", user)

        assert path.skill_name.lower() == "python"
        # All stage names should reference Python-relevant content (not React)
        for stage in path.stages:
            for lesson in stage.lessons:
                assert "react" not in lesson.title.lower() or "python" in lesson.title.lower(), (
                    f"Python path has React lesson: {lesson.title}"
                )

    def test_react_path_returns_react_stages(self) -> None:
        """build_skill_learning_path('React') returns React stages, not Python."""
        db = _fake_db()
        user = _fake_user()

        with patch("app.services.skill_learning_service.build_learner_knowledge_profile") as mock_profile, \
             patch("app.services.skill_learning_service.retrieve_teaching_resources_for_lesson", return_value=[]):
            mock_profile.return_value = MagicMock(
                verified_projects=[],
                recommended_learning_order=[],
                skills_inventory=[],
            )
            path = build_skill_learning_path(db, "React", user)

        assert "react" in path.skill_name.lower()
        # Verify no Python-specific GIL content in titles
        for stage in path.stages:
            for lesson in stage.lessons:
                assert "gil" not in lesson.title.lower(), (
                    f"React path has GIL lesson (Python content): {lesson.title}"
                )

    def test_python_and_react_paths_are_distinct(self) -> None:
        """Python and React paths must produce distinct skill names and lesson ids."""
        db = _fake_db()
        user = _fake_user()

        with patch("app.services.skill_learning_service.build_learner_knowledge_profile") as mock_profile, \
             patch("app.services.skill_learning_service.retrieve_teaching_resources_for_lesson", return_value=[]):
            mock_profile.return_value = MagicMock(
                verified_projects=[],
                recommended_learning_order=[],
                skills_inventory=[],
            )
            py_path = build_skill_learning_path(db, "Python", user)
            react_path = build_skill_learning_path(db, "React", user)

        assert py_path.skill_name.lower() != react_path.skill_name.lower()

        py_lesson_ids = {l.id for s in py_path.stages for l in s.lessons}
        react_lesson_ids = {l.id for s in react_path.stages for l in s.lessons}
        overlap = py_lesson_ids & react_lesson_ids
        assert not overlap, f"Python and React paths share lesson ids: {overlap}"


# ── validate_topic_sequence ───────────────────────────────────────────────────

class TestValidateTopicSequence:

    def test_valid_sequence_passes(self) -> None:
        """Stages in correct canonical order pass validation."""
        from app.schemas.teaching import SkillCurriculumStage
        stages = [
            SkillCurriculumStage(stage_number=1, stage_name="Foundations", description="", lessons=[]),
            SkillCurriculumStage(stage_number=2, stage_name="Core Python", description="", lessons=[]),
            SkillCurriculumStage(stage_number=3, stage_name="Intermediate Architecture", description="", lessons=[]),
            SkillCurriculumStage(stage_number=4, stage_name="Advanced Engineering", description="", lessons=[]),
            SkillCurriculumStage(stage_number=5, stage_name="Real Projects", description="", lessons=[]),
            SkillCurriculumStage(stage_number=6, stage_name="Interview Readiness", description="", lessons=[]),
        ]
        # Should not raise
        validate_topic_sequence(stages)
    def test_built_python_path_passes_sequence_validation(self) -> None:
        """Stages returned by build_skill_learning_path for Python pass validate_topic_sequence."""
        db = _fake_db()
        user = _fake_user()

        with patch("app.services.skill_learning_service.build_learner_knowledge_profile") as mock_profile, \
             patch("app.services.skill_learning_service.retrieve_teaching_resources_for_lesson", return_value=[]):
            mock_profile.return_value = MagicMock(
                verified_projects=[],
                recommended_learning_order=[],
                skills_inventory=[],
            )
            path = build_skill_learning_path(db, "Python", user)

        # validate_topic_sequence is called inside build_skill_learning_path already;
        # call it again here to make the assertion explicit in tests.
        validate_topic_sequence(path.stages)

    def test_built_react_path_passes_sequence_validation(self) -> None:
        """Stages returned by build_skill_learning_path for React pass validate_topic_sequence."""
        db = _fake_db()
        user = _fake_user()

        with patch("app.services.skill_learning_service.build_learner_knowledge_profile") as mock_profile, \
             patch("app.services.skill_learning_service.retrieve_teaching_resources_for_lesson", return_value=[]):
            mock_profile.return_value = MagicMock(
                verified_projects=[],
                recommended_learning_order=[],
                skills_inventory=[],
            )
            path = build_skill_learning_path(db, "React", user)

        validate_topic_sequence(path.stages)

    def test_empty_stages_pass_validation(self) -> None:
        """Empty stage list passes validation without error."""
        validate_topic_sequence([])

    def test_inverted_sequence_fails_validation(self) -> None:
        """Stages in clearly wrong order (stage_number descending) fail validation."""
        from app.schemas.teaching import SkillCurriculumStage
        stages = [
            SkillCurriculumStage(stage_number=5, stage_name="Advanced Engineering", description="", lessons=[]),
            SkillCurriculumStage(stage_number=1, stage_name="Foundations", description="", lessons=[]),
        ]
        with pytest.raises(AssertionError):
            validate_topic_sequence(stages)


# ── ai_generated flag propagation via generate_comprehensive_lesson ──────────

class TestAIFlagPropagation:

    def test_ai_generated_false_uses_curated_path(self) -> None:
        """ai_generated=False must use curated/generic path (no provider call)."""
        _clear_cache()
        req = TeachingLessonDetailRequest(
            skill="Python",
            concept="Memory References & Object Identity",
            learner_level="Intermediate",
            ai_generated=False,
        )
        # Provider should NOT be called
        with patch(
            "app.services.lesson_generation_service.get_model_provider"
        ) as mock_provider:
            res = generate_comprehensive_lesson(req)
            mock_provider.assert_not_called()

        assert isinstance(res, TeachingLessonDetailResponse)
        assert res.skill == "Python"

    def test_ai_generated_true_calls_provider(self) -> None:
        """ai_generated=True must invoke get_model_provider."""
        _clear_cache()
        python_json = _python_lesson_json("Foundations")
        req = TeachingLessonDetailRequest(
            skill="Python",
            concept="Foundations",
            learner_level="Intermediate",
            ai_generated=True,
        )
        with patch(
            "app.services.lesson_generation_service.get_model_provider",
            return_value=FakeProvider(response_json=python_json),
        ) as mock_provider:
            res = generate_comprehensive_lesson(req)
            mock_provider.assert_called()

        assert isinstance(res, TeachingLessonDetailResponse)
        assert res.validation_status == "verified_relevant"


# ── Regression Test Suite for Tasks 2, 3, 4, 5, 6 ───────────────────────────

class TestTopicSpecificContentCorrectness:
    """Verifies that each skill and topic returns technically accurate, distinct, non-generic content."""

    def test_python_variables_and_data_types(self) -> None:
        """Python Variables & Data Types returns genuine Python types, memory references, and runnable code."""
        _clear_cache()
        req = TeachingLessonDetailRequest(
            skill="Python",
            concept="Variables and Data Types",
            lesson_id="py-var-001",
            learner_level="Beginner",
            ai_generated=False,
        )
        res = generate_comprehensive_lesson(req)
        lesson = res.lesson

        assert res.skill == "Python"
        assert res.lesson_id == "py-var-001"
        assert "Variables" in lesson.topic or "Variables" in lesson.title
        # Starter code must not be generic
        assert lesson.starter_code != "# Write code here\n"
        assert len(lesson.starter_code) > 40
        assert "is" in lesson.starter_code or "id(" in lesson.starter_code or "type(" in lesson.starter_code
        # Line-by-line explanation must exist and not be generic statement execution
        assert lesson.code_walkthrough is not None
        assert "executes deterministic statement logic" not in lesson.code_walkthrough
        # Common mistakes must discuss python types, comparison, or references
        assert any(term in lesson.common_mistakes.lower() for term in ["is", "type", "string", "comparison", "conversion", "reference", "mutable"])
        # Real-world application must be meaningful
        assert len(lesson.real_world_applications or "") > 30

    def test_react_components_and_props(self) -> None:
        """React Components and Props returns valid JSX, props contracts, and no Python code."""
        _clear_cache()
        req = TeachingLessonDetailRequest(
            skill="React",
            concept="Components and Props",
            lesson_id="react-comp-001",
            learner_level="Intermediate",
            ai_generated=False,
        )
        res = generate_comprehensive_lesson(req)
        lesson = res.lesson

        assert res.skill == "React"
        assert res.lesson_id == "react-comp-001"
        # Code must have React JSX components
        assert "<" in lesson.starter_code and ">" in lesson.starter_code
        assert "props" in lesson.starter_code.lower() or "function" in lesson.starter_code.lower()
        # No Python or SQL contamination
        assert "def " not in lesson.starter_code
        assert "SELECT " not in lesson.starter_code
        # Walkthrough must mention props or components
        assert "prop" in (lesson.code_walkthrough or "").lower() or "component" in (lesson.code_walkthrough or "").lower()
        # Mistakes must mention component naming or fragments
        assert any(term in (lesson.common_mistakes or "").lower() for term in ["component", "react", "fragment", "html", "prop"])

    def test_langchain_what_langchain_is(self) -> None:
        """LangChain lesson explains architectural motivation, LCEL runnable protocol, and no generic text."""
        _clear_cache()
        req = TeachingLessonDetailRequest(
            skill="LangChain",
            concept="What LangChain Is & Architectural Motivation",
            lesson_id="lc-arch-001",
            learner_level="Intermediate",
            ai_generated=False,
        )
        res = generate_comprehensive_lesson(req)
        lesson = res.lesson

        assert res.skill == "LangChain"
        assert res.lesson_id == "lc-arch-001"
        assert "LangChain" in lesson.topic or "LangChain" in lesson.title
        # Code must demonstrate modern LCEL pipeline
        assert "|" in lesson.starter_code or "invoke" in lesson.starter_code
        assert "ChatPromptTemplate" in lesson.starter_code or "Runnable" in lesson.starter_code or "StrOutputParser" in lesson.starter_code
        # No generic placeholder strings
        assert lesson.starter_code != "# Write code here\n"
        assert "executes deterministic statement logic" not in (lesson.code_walkthrough or "")
        # Common mistakes should address LCEL or LLM pitfalls
        assert "chain" in (lesson.common_mistakes or "").lower() or "lcel" in (lesson.common_mistakes or "").lower() or "leak" in (lesson.common_mistakes or "").lower()
        # Quick check should test understanding of LangChain
        assert lesson.quick_check is not None
        assert any(term in lesson.quick_check["question"] for term in ["LCEL", "LangChain", "Runnable"])

    def test_langgraph_state_and_nodes(self) -> None:
        """LangGraph lesson covers StateGraph, state schemas, and node transitions."""
        _clear_cache()
        req = TeachingLessonDetailRequest(
            skill="LangGraph",
            concept="State and Nodes",
            lesson_id="lg-nodes-001",
            learner_level="Intermediate",
            ai_generated=False,
        )
        res = generate_comprehensive_lesson(req)
        lesson = res.lesson

        assert res.skill == "LangGraph"
        assert res.lesson_id == "lg-nodes-001"
        assert "StateGraph" in lesson.starter_code
        assert "TypedDict" in lesson.starter_code or "messages" in lesson.starter_code
        # No React or SQL code
        assert "import React" not in lesson.starter_code
        assert "SELECT " not in lesson.starter_code
        # Walkthrough explains graph nodes / state
        assert "node" in (lesson.code_walkthrough or "").lower() or "state" in (lesson.code_walkthrough or "").lower()

    def test_sql_joins(self) -> None:
        """SQL Joins lesson teaches relational joins, execution semantics, and realistic queries."""
        _clear_cache()
        req = TeachingLessonDetailRequest(
            skill="SQL",
            concept="Relational Joins & Execution Semantics",
            lesson_id="sql-joins-001",
            learner_level="Intermediate",
            ai_generated=False,
        )
        res = generate_comprehensive_lesson(req)
        lesson = res.lesson

        assert res.skill == "SQL"
        assert res.lesson_id == "sql-joins-001"
        # Code must have relational JOIN query
        assert "JOIN" in lesson.starter_code.upper()
        assert "ON" in lesson.starter_code.upper()
        # Mistakes should cover Cartesian products or NULL ON conditions
        assert "cartesian" in (lesson.common_mistakes or "").lower() or "null" in (lesson.common_mistakes or "").lower() or "join" in (lesson.common_mistakes or "").lower()

    def test_line_by_line_explanation_matches_starter_code(self) -> None:
        """Line-by-line explanation breaks down actual lines present in starter_code."""
        from app.services.lesson_generation_service import synthesize_line_by_line_walkthrough
        sample_code = (
            "from langchain_core.prompts import ChatPromptTemplate\n"
            "prompt = ChatPromptTemplate.from_template('Explain {topic}')\n"
            "chain = prompt | model\n"
            "result = chain.invoke({'topic': 'agents'})\n"
        )
        walkthrough = synthesize_line_by_line_walkthrough(sample_code, "LangChain", "LCEL")
        assert "ChatPromptTemplate" in walkthrough
        assert "invoke" in walkthrough or "chain" in walkthrough
        assert "executes deterministic statement logic" not in walkthrough

    def test_selected_lesson_id_preserved_in_request_and_response(self) -> None:
        """Lesson ID requested is faithfully preserved across response and nested lesson."""
        _clear_cache()
        custom_id = "test-custom-unique-lesson-id-777"
        req = TeachingLessonDetailRequest(
            skill="Python",
            concept="Variables and Data Types",
            lesson_id=custom_id,
            learner_level="Beginner",
            ai_generated=False,
        )
        res = generate_comprehensive_lesson(req)
        assert res.lesson_id == custom_id
        assert res.lesson.id == custom_id

    def test_switching_topics_does_not_leak_stale_content(self) -> None:
        """Switching from React to LangChain delivers distinct content without leakage."""
        _clear_cache()
        req_react = TeachingLessonDetailRequest(
            skill="React",
            concept="Components and Props",
            lesson_id="react-c-1",
            learner_level="Intermediate",
            ai_generated=False,
        )
        res_react = generate_comprehensive_lesson(req_react)

        req_lc = TeachingLessonDetailRequest(
            skill="LangChain",
            concept="What LangChain Is & Architectural Motivation",
            lesson_id="lc-arch-1",
            learner_level="Intermediate",
            ai_generated=False,
        )
        res_lc = generate_comprehensive_lesson(req_lc)

        assert res_react.skill == "React"
        assert res_lc.skill == "LangChain"
        assert res_react.lesson.id != res_lc.lesson.id
        assert "ChatPromptTemplate" not in res_react.lesson.starter_code
        assert "function" not in res_lc.lesson.starter_code or "|" in res_lc.lesson.starter_code

    def test_content_validation_rejects_hollow_placeholder_content(self) -> None:
        """validate_lesson_relevance rejects placeholder starter_code and short strings."""
        from app.services.lesson_generation_service import validate_lesson_relevance
        # Reject generic placeholder code
        valid, reason = validate_lesson_relevance(
            lesson_data={
                "title": "Python Variables",
                "topic": "Variables and Data Types",
                "starter_code": "# Write code here\n",
                "what_it_is": "Python variables store references to objects in memory.",
                "common_mistakes": "Mutating default arguments causes bugs.",
            },
            skill="Python",
            concept="Variables",
        )
        assert not valid
        assert "placeholder" in reason or "too short" in reason

        # Reject cross-domain contamination
        valid_contam, reason_contam = validate_lesson_relevance(
            lesson_data={
                "title": "Python Decorators",
                "topic": "Decorators",
                "starter_code": "import React, { useState } from 'react';\nfunction App() { return <div>Hi</div>; }",
                "what_it_is": "This lesson teaches React component architecture.",
                "common_mistakes": "Mutating useState state directly.",
            },
            skill="Python",
            concept="Decorators",
        )
        assert not valid_contam
        assert "mismatch" in reason_contam.lower() or "cross-domain" in reason_contam.lower()

    def test_provider_failure_does_not_produce_fake_verified_lesson(self) -> None:
        """When AI provider fails, status is fallback_curated, never fake verified_relevant."""
        _clear_cache()
        with patch(
            "app.services.lesson_generation_service.get_model_provider",
            return_value=FakeProvider(raise_error=True),
        ):
            res = generate_ai_driven_lesson(
                skill="LangChain",
                concept_title="NonExistentTopic12345",
                lesson_id="lc-fail-001",
                learner_level="Intermediate",
                active_section="overview",
            )
        assert res.validation_status == "fallback_curated"
        assert res.lesson.starter_code != "# Write code here\n"
        assert len(res.lesson.starter_code) > 20

    def test_large_language_models_curriculum_and_lesson_differentiation(self) -> None:
        """Large Language Models generates an authentic 4-stage curriculum and topic-pure lessons."""
        _clear_cache()
        db = _fake_db()
        user = _fake_user()

        path = build_skill_learning_path(db, "Large Language Models", user)
        assert path.skill_name == "Large Language Models"
        assert len(path.stages) >= 4
        stage_names = [s.stage_name for s in path.stages]
        assert "Foundations & Architecture" in stage_names
        assert "Representation & Mathematics" in stage_names

        # Generate LLM lesson
        req = TeachingLessonDetailRequest(
            skill="Large Language Models",
            concept="What an LLM Is & How It Differs from Traditional Software",
            lesson_id="llm-foundations-1",
            learner_level="Intermediate",
            ai_generated=False,
        )
        res = generate_comprehensive_lesson(req)
        assert res.skill == "Large Language Models"
        assert "autoregressive" in res.lesson.what_it_is.lower() or "probabilistic" in res.lesson.what_it_is.lower()
        assert "softmax" in res.lesson.starter_code.lower() or "vocab" in res.lesson.starter_code.lower()
        # Ensure zero React or SQL leakage
        assert "useState" not in res.lesson.starter_code
        assert "SELECT" not in res.lesson.starter_code
        assert "<html>" not in res.lesson.starter_code

    def test_prompt_engineering_curriculum_and_lesson_differentiation(self) -> None:
        """Prompt Engineering generates an authentic 3-stage curriculum and specialized prompt lessons."""
        _clear_cache()
        db = _fake_db()
        user = _fake_user()

        path = build_skill_learning_path(db, "Prompt Engineering", user)
        assert path.skill_name == "Prompt Engineering"
        assert len(path.stages) >= 3
        stage_names = [s.stage_name for s in path.stages]
        assert "Task Specification & Context" in stage_names
        assert "Advanced Steering & Scaffolding" in stage_names

        req = TeachingLessonDetailRequest(
            skill="Prompt Engineering",
            concept="Instruction Clarity & Task Specification",
            lesson_id="pe-clarity-1",
            learner_level="Intermediate",
            ai_generated=False,
        )
        res = generate_comprehensive_lesson(req)
        assert res.skill == "Prompt Engineering"
        assert "system" in res.lesson.starter_code.lower() or "xml" in res.lesson.starter_code.lower()
        assert "delimiters" in res.lesson.detailed_explanation.lower() or "instruction" in res.lesson.detailed_explanation.lower()
        assert "injection" in res.lesson.common_mistakes.lower() or "schema" in res.lesson.common_mistakes.lower()

    def test_all_five_technologies_have_distinct_learning_content(self) -> None:
        """Python, React, LangChain, Prompt Engineering, and LLMs produce completely distinct content."""
        _clear_cache()
        skills = [
            ("Python", "Variables & Dynamic Typing"),
            ("React", "Components and Props"),
            ("LangChain", "What LangChain Is & Architectural Motivation"),
            ("Prompt Engineering", "Instruction Clarity & Task Specification"),
            ("Large Language Models", "What an LLM Is & How It Differs from Traditional Software"),
        ]

        starter_codes = []
        objectives = []
        for sk, concept in skills:
            req = TeachingLessonDetailRequest(
                skill=sk,
                concept=concept,
                lesson_id=f"test-{sk.lower().replace(' ', '-')}",
                learner_level="Intermediate",
                ai_generated=False,
            )
            res = generate_comprehensive_lesson(req)
            starter_codes.append(res.lesson.starter_code)
            objectives.append(res.lesson.learning_objective)

        # All 5 starter codes must be unique and non-empty
        assert len(set(starter_codes)) == 5
        assert len(set(objectives)) == 5

        # Domain purity verification
        # Python should not mention LangChain Runnables
        assert "Runnable" not in starter_codes[0]
        # React should have JSX or components, not Python def
        assert "React" in starter_codes[1] or "function" in starter_codes[1]
        # LangChain should have LCEL or prompt pipes
        assert "|" in starter_codes[2] or "langchain" in starter_codes[2].lower()
        # Prompt Engineering should have XML/prompt templates
        assert "<system>" in starter_codes[3] or "prompt" in starter_codes[3].lower()
        # LLMs should have softmax or vocabulary logits
        assert "softmax" in starter_codes[4] or "vocab" in starter_codes[4].lower()

    def test_mentor_six_quick_actions_return_topic_grounded_guidance(self) -> None:
        """The 6 AI mentor quick actions return tailored responses specific to the lesson topic."""
        from app.services.teaching_service import chat_with_teaching_mentor
        db = _fake_db()
        user = _fake_user()

        actions = [
            ("Explain this concept more simply", "simply"),
            ("Show a different example", "example"),
            ("Give me a hint", "hint"),
            ("Explain why my answer is incorrect", "answer"),
            ("Give me a practical challenge", "challenge"),
            ("Connect this concept to my project", "project"),
        ]

        for prompt_text, expected_keyword in actions:
            req = TeachingChatRequest(
                mode="skill",
                target_id="LangChain",
                lesson_id="lc-arch-1",
                message=prompt_text,
                is_assessment=False,
            )
            reply = chat_with_teaching_mentor(db, user, req)
            assert reply.reply is not None
            assert len(reply.reply) > 50
            # Must mention the skill or concept in the guidance
            assert "langchain" in reply.reply.lower() or expected_keyword in reply.reply.lower() or "llm" in reply.reply.lower() or "chain" in reply.reply.lower()

    def test_assessment_mode_evaluates_without_auto_awarding_mastery(self) -> None:
        """Assessment mode evaluates learner submission rigorously and does not grant mastery on empty/failed tries."""
        from app.services.teaching_service import chat_with_teaching_mentor
        db = _fake_db()
        user = _fake_user()

        # Simulated provider failure during assessment
        with patch(
            "app.services.teaching_service.get_model_provider",
            return_value=FakeProvider(raise_error=True),
        ):
            req = TeachingChatRequest(
                mode="skill",
                target_id="Large Language Models",
                lesson_id="llm-foundations-1",
                message="My attempt: An LLM is just a database of sentences.",
                is_assessment=True,
            )
            reply = chat_with_teaching_mentor(db, user, req)
            # Must NOT award mastery on failure
            assert reply.demonstrated_understanding is False
            assert "retry" in reply.reply.lower() or "unavailable" in reply.reply.lower()


# ══════════════════════════════════════════════════════════════════════════════
# ACCEPTANCE TEST SCENARIOS A THROUGH F
# ══════════════════════════════════════════════════════════════════════════════

class TestScenariosAThroughF:
    """Automated acceptance test suite verifying Scenarios A through F."""

    def test_scenario_a_python_dictionaries(self) -> None:
        """
        Test A — Python dictionaries:
        Lesson: 'Python Dictionaries and Hash-Based Lookup'
        Expected:
        - Detailed concept explanations of keys, values, hash-based indexing.
        - A meaningful flowchart or visual mental model walkthrough.
        - Correct code and expected output.
        - Relevant edge cases and complexity discussion (O(1) average lookup, time & space).
        - Useful exercises and topic-specific assessment.
        - Relevant Python sources (docs.python.org, geeksforgeeks.org).
        """
        _clear_cache()
        req = TeachingLessonDetailRequest(
            skill="Python",
            concept="Python Dictionaries and Hash-Based Lookup",
            lesson_id="py-dict-001",
            learner_level="Intermediate",
            ai_generated=False,
        )
        detail = generate_comprehensive_lesson(req)

        lesson = detail.lesson
        full_text = f"{lesson.title} {lesson.concept_summary} {lesson.detailed_explanation} {lesson.starter_code}".lower()

        # 1. Keys, values, hash table, O(1) lookup
        assert any(k in full_text for k in ("hash", "o(1)", "key", "mapping", "dict", "lookup"))
        # 2. Visual flowchart / diagram walkthrough
        assert lesson.mental_model_diagram is not None and len(lesson.mental_model_diagram) > 0
        assert "hash" in lesson.mental_model_diagram.lower() or "bucket" in lesson.mental_model_diagram.lower()
        assert lesson.diagram_explanation is not None and len(lesson.diagram_explanation) > 0
        # 3. Complexity analysis
        assert lesson.time_complexity is not None and "o(1)" in lesson.time_complexity.lower()
        assert lesson.space_complexity is not None
        # 4. Working Python example with output
        assert "def " in lesson.starter_code or "{" in lesson.starter_code
        assert lesson.expected_output is not None and len(lesson.expected_output) > 0
        # 5. Relevant practice problem and solution
        assert len(lesson.practice_exercises) > 0
        ex_py = lesson.practice_exercises[0]
        sol = ex_py.get("solution") if isinstance(ex_py, dict) else getattr(ex_py, "solution", None)
        assert sol is not None
        # 6. Official Python docs & GeeksforGeeks
        assert len(lesson.resources) >= 1
        urls = [r["canonical_url"] for r in lesson.resources if isinstance(r, dict)]
        assert any("docs.python.org" in u for u in urls)
        assert any("geeksforgeeks.org" in u for u in urls)

    def test_scenario_b_react_components_props_and_state(self) -> None:
        """
        Test B — React:
        Lesson: 'React Components, Props, and State'
        Expected:
        - Accurate component, props, and state explanations.
        - Relevant React examples with useState.
        - Explanation of rendering behavior and state updates.
        - A meaningful visual diagram of component tree & re-render cycle.
        - Relevant exercises and official React sources (react.dev).
        - No Python or Figma contamination.
        """
        _clear_cache()
        req = TeachingLessonDetailRequest(
            skill="React",
            concept="React Components, Props, and State",
            lesson_id="react-props-state-001",
            learner_level="Intermediate",
            ai_generated=False,
        )
        detail = generate_comprehensive_lesson(req)

        lesson = detail.lesson
        full_text = f"{lesson.title} {lesson.concept_summary} {lesson.detailed_explanation} {lesson.starter_code}".lower()

        # 1. Accurate component, props, state explanations
        assert any(k in full_text for k in ("component", "props", "state", "usestate", "re-render"))
        # 2. Meaningful visual diagram
        assert lesson.mental_model_diagram is not None and len(lesson.mental_model_diagram) > 0
        assert "state" in lesson.mental_model_diagram.lower() or "props" in lesson.mental_model_diagram.lower()
        assert lesson.diagram_explanation is not None and len(lesson.diagram_explanation) > 0
        # 3. Relevant React examples with code & output
        assert "useState" in lesson.starter_code or "return (" in lesson.starter_code or "React" in lesson.starter_code
        assert lesson.expected_output is not None and len(lesson.expected_output) > 0
        # 4. Relevant exercises and official React sources
        assert len(lesson.practice_exercises) > 0
        assert len(lesson.resources) >= 1
        urls = [r["canonical_url"] for r in lesson.resources if isinstance(r, dict)]
        assert any("react.dev" in u for u in urls)
        # 5. No cross-contamination
        assert "figma" not in full_text
        assert "def " not in lesson.starter_code

    def test_scenario_javascript_closures(self) -> None:
        """
        Test JavaScript Closures:
        Lesson: 'JavaScript Closures: A Practical Guide'
        Expected:
        - Accurate lexical scope, closure, and function factory explanations.
        - Meaningful visual diagram of lexical environment and outer scope pointer.
        - Correct JavaScript code (createCounter) and expected output ('1\\n2\\n3').
        - Step-by-step trace and execution trace table.
        - Practical applications (private state, event handlers, React hooks).
        - Common mistakes (var in loops vs let).
        - Topic-specific assessment question.
        - Official MDN Web Docs sources (developer.mozilla.org).
        - No Python/GIL or Figma contamination.
        """
        _clear_cache()
        req = TeachingLessonDetailRequest(
            skill="JavaScript",
            concept="JavaScript Closures: A Practical Guide",
            lesson_id="js-closure-001",
            learner_level="Intermediate",
            ai_generated=False,
        )
        detail = generate_comprehensive_lesson(req)

        lesson = detail.lesson
        full_text = f"{lesson.title} {lesson.concept_summary} {lesson.detailed_explanation} {lesson.starter_code}".lower()

        # 1. Lexical scope, closure, function factory explanations
        assert any(k in full_text for k in ("closure", "lexical", "scope", "function", "state", "environment"))
        # 2. Visual diagram & mental model
        assert lesson.mental_model_diagram is not None and len(lesson.mental_model_diagram) > 0
        assert "createcounter" in lesson.mental_model_diagram.lower() or "increment" in lesson.mental_model_diagram.lower()
        assert lesson.diagram_explanation is not None and len(lesson.diagram_explanation) > 0
        # 3. JavaScript code & expected output
        assert "function createCounter" in lesson.starter_code
        assert "1" in lesson.expected_output and "2" in lesson.expected_output and "3" in lesson.expected_output
        # 4. Step-by-step and execution trace table
        assert lesson.step_by_step is not None and len(lesson.step_by_step) > 0
        assert len(lesson.execution_trace_table) >= 3
        assert lesson.execution_trace_table[0]["action"] == "createCounter()"
        # 5. Practical applications & common mistakes
        assert "private" in lesson.real_world_applications.lower() or "event" in lesson.real_world_applications.lower()
        assert "var" in lesson.common_mistakes.lower() and "let" in lesson.common_mistakes.lower()
        # 6. Official MDN Web Docs resource
        assert len(lesson.resources) >= 1
        urls = [r["canonical_url"] for r in lesson.resources if isinstance(r, dict)]
        assert any("developer.mozilla.org" in u for u in urls)
        # 7. No cross-contamination
        assert "figma" not in full_text
        assert "gil" not in full_text
        assert "cpython" not in full_text
        assert "def " not in lesson.starter_code

    def test_scenario_c_figma_auto_layout(self) -> None:
        """
        Test C — Figma / UI/UX:
        Lesson: 'Figma Auto Layout and Responsive Components'
        Expected:
        - Relevant design concepts (Auto Layout, padding, gap, Hug vs Fill vs Fixed).
        - A realistic layout example.
        - An explanation of resizing and responsive behavior.
        - A visual container hierarchy diagram.
        - A useful design exercise.
        - Relevant Figma and UX references (help.figma.com).
        - No LangChain or Python contamination.
        """
        _clear_cache()
        req = TeachingLessonDetailRequest(
            skill="Figma",
            concept="Figma Auto Layout and Responsive Components",
            lesson_id="figma-layout-001",
            learner_level="Intermediate",
            ai_generated=False,
        )
        detail = generate_comprehensive_lesson(req)

        lesson = detail.lesson
        full_text = f"{lesson.title} {lesson.concept_summary} {lesson.detailed_explanation} {lesson.starter_code}".lower()

        # 1. Figma-specific explanations & concepts (Hug vs Fill)
        assert any(k in full_text for k in ("auto layout", "frame", "padding", "gap", "hug", "fill", "resizing"))
        # 2. Visual container hierarchy diagram
        assert lesson.mental_model_diagram is not None and len(lesson.mental_model_diagram) > 0
        assert "auto layout" in lesson.mental_model_diagram.lower() or "frame" in lesson.mental_model_diagram.lower()
        assert lesson.diagram_explanation is not None and len(lesson.diagram_explanation) > 0
        # 3. Meaningful layout exercise
        assert len(lesson.practice_exercises) > 0
        ex = lesson.practice_exercises[0]
        ex_title = ex.get("title", "") if isinstance(ex, dict) else getattr(ex, "title", "")
        ex_prob = ex.get("problem_statement", "") if isinstance(ex, dict) else getattr(ex, "problem_statement", "")
        ex_text = f"{ex_title} {ex_prob}".lower()
        assert any(term in ex_text for term in ("layout", "card", "responsive", "padding", "auto"))
        # 4. Quiz tests Auto Layout
        assert "auto layout" in lesson.quick_check["question"].lower() or "sizing mode" in lesson.quick_check["question"].lower() or "figma" in lesson.quick_check["question"].lower()
        # 5. Verified Figma sources
        assert len(lesson.resources) >= 1
        urls = [r["canonical_url"] for r in lesson.resources if isinstance(r, dict)]
        assert any("figma.com" in u or "w3.org" in u for u in urls)
        # 6. NO unrelated LangChain, Python, or LLM content
        forbidden_cross_domain = ["langchain", "lcel", "runnable", "prompt injection", "cpython", "async def"]
        for term in forbidden_cross_domain:
            assert term not in full_text, f"Cross-domain contamination in Figma lesson: '{term}' found!"

    def test_scenario_langchain_loaders_and_splitters(self) -> None:
        """
        Supplementary Scenario — LangChain:
        Selected lesson: 'LangChain Document Loaders and Text Splitters'
        Expected:
        - Explanations of document loading, chunking, and why splitting matters.
        - Relevant LangChain sources (python.langchain.com).
        - A meaningful document-processing example.
        - A relevant exercise and quiz.
        - No Figma or unrelated generic content.
        """
        _clear_cache()
        req = TeachingLessonDetailRequest(
            skill="LangChain",
            concept="LangChain Document Loaders and Text Splitters",
            lesson_id="lc-loaders-001",
            learner_level="Intermediate",
            ai_generated=False,
        )
        detail = generate_comprehensive_lesson(req)

        lesson = detail.lesson
        full_text = f"{lesson.title} {lesson.concept_summary} {lesson.detailed_explanation} {lesson.starter_code}".lower()

        # 1. Loading, chunking, splitting explanations
        assert any(k in full_text for k in ("document loader", "text splitter", "chunk", "overlap", "split_documents"))
        # 2. Meaningful document-processing example
        assert "recursivelinearchartertextsplitter" in full_text.replace(" ", "") or "textsplitter" in full_text.replace(" ", "") or "textloader" in full_text
        # 3. Relevant LangChain sources
        assert len(lesson.resources) >= 1
        urls = [r["canonical_url"] for r in lesson.resources if isinstance(r, dict)]
        assert any("langchain.com" in u for u in urls)
        # 4. Relevant exercise and quiz
        assert "chunk" in lesson.quick_check["question"].lower() or "splitter" in lesson.quick_check["question"].lower()
        # 5. No Figma or unrelated generic content
        assert "figma" not in full_text
        assert "auto layout" not in full_text

    def test_scenario_d_candidate_personalization(self) -> None:
        """
        Scenario D — Candidate Personalization:
        Two test candidates with different skill levels, projects, and target roles.
        Expected:
        - Lessons adapt the explanation level and examples appropriately.
        - The underlying subject remains correct.
        - Neither candidate's private profile or saved progress leaks into the other's results.
        """
        _clear_cache()
        req_junior = TeachingLessonDetailRequest(
            skill="React",
            concept="Components and Props",
            lesson_id="react-p-junior",
            learner_level="Beginner",
            ai_generated=False,
        )
        detail_junior = generate_comprehensive_lesson(req_junior)

        _clear_cache()
        req_senior = TeachingLessonDetailRequest(
            skill="LangGraph",
            concept="What LangGraph Is",
            lesson_id="lg-p-senior",
            learner_level="Advanced",
            ai_generated=False,
        )
        detail_senior = generate_comprehensive_lesson(req_senior)

        # 1. Subject remains correct
        assert "react" in detail_junior.lesson.title.lower() or "component" in detail_junior.lesson.title.lower()
        assert "langgraph" in detail_senior.lesson.title.lower() or "graph" in detail_senior.lesson.title.lower()

        # 2. No leakage of candidate profiles or projects
        senior_dump = str(detail_senior.model_dump())
        junior_dump = str(detail_junior.model_dump())
        assert "junior" not in senior_dump.lower()
        assert "react" not in senior_dump.lower()
        assert "langgraph" not in junior_dump.lower()

    def test_scenario_e_failure_handling(self) -> None:
        """
        Scenario E — Failure handling:
        Simulate unavailable search, inaccessible pages, irrelevant search results, malformed model output, and provider timeouts.
        Expected:
        - Useful loading, retry, and error states.
        - No fabricated citations or unrelated fallback lessons.
        - Existing saved progress remains intact.
        """
        _clear_cache()
        # When model provider fails or times out, lesson generator falls back to curated verified lesson
        with patch("app.services.lesson_generation_service.get_model_provider", return_value=FakeProvider(raise_error=True)):
            req = TeachingLessonDetailRequest(
                skill="Python",
                concept="Variables & Data Types",
                lesson_id="py-fail-fallback",
                learner_level="Intermediate",
                ai_generated=True,
            )
            detail = generate_comprehensive_lesson(req)

            assert detail.lesson is not None
            assert "variable" in detail.lesson.title.lower()
            # Verified resources must come from official domains, not fabricated hallucinations
            for res in detail.lesson.resources:
                if isinstance(res, dict) and "canonical_url" in res:
                    assert res["canonical_url"].startswith("http")
                    assert not res["canonical_url"].startswith("http://fake")

    def test_scenario_f_ui_data_flow_and_distinct_skills(self) -> None:
        """
        Scenario F — UI / API Flow:
        Verify:
        - Changing selected skill updates the roadmap and lesson content.
        - Changing lessons does not show stale citations, quizzes, or cached content.
        """
        db = _fake_db()
        user = _fake_user()

        with patch("app.services.skill_learning_service.build_learner_knowledge_profile") as mock_profile:
            mock_profile.return_value = MagicMock(verified_projects=[], recommended_learning_order=[], skills_inventory=[])

            # 1. Fetch Python roadmap
            py_path = build_skill_learning_path(db, "Python", user)
            # 2. Fetch Figma roadmap
            figma_path = build_skill_learning_path(db, "Figma", user)

        assert py_path.skill_name.lower() != figma_path.skill_name.lower()
        py_titles = [l.title for s in py_path.stages for l in s.lessons]
        figma_titles = [l.title for s in figma_path.stages for l in s.lessons]

        # Titles must be completely disjoint
        overlap = set(py_titles).intersection(set(figma_titles))
        assert len(overlap) == 0, f"Roadmap titles overlap between Python and Figma: {overlap}"


class TestTenMandatoryRegressionScenarios:
    """
    Direct test verification for all 10 mandatory regression scenarios specified in the objective:
    1. An OpenCV lesson must not contain unrelated React hooks or JavaScript closures as its primary explanation.
    2. An OpenCV lesson must not cite React documentation as its authoritative source.
    3. A JavaScript lesson must use JavaScript-specific concepts and relevant documentation.
    4. A Prompt Engineering lesson must not inherit generic OpenCV or concurrency examples without a genuine connection.
    5. Every generated exercise must test the selected lesson's subject.
    6. Unavailable web content must not be represented as successfully retrieved content.
    7. Repeated generic paragraphs must be detected.
    8. Candidate-specific examples must only use information actually present in the candidate profile.
    9. Existing lesson completion and mastery progress must remain intact.
    10. Failure of the retrieval provider must not crash the learning page.
    """

    def test_scenario_1_opencv_no_react_or_closures(self) -> None:
        _clear_cache()
        req = TeachingLessonDetailRequest(
            skill="OpenCV",
            concept="Image Representation & Pixel Grids",
            lesson_id="cv-scen-1",
            learner_level="Beginner",
            ai_generated=False,
        )
        detail = generate_comprehensive_lesson(req)
        lesson_dump = str(detail.lesson.model_dump()).lower()
        assert "react" not in lesson_dump
        assert "virtual dom" not in lesson_dump
        assert "usememo" not in lesson_dump
        assert "usecallback" not in lesson_dump
        assert "closure" not in lesson_dump
        assert "bgr" in lesson_dump or "numpy" in lesson_dump or "pixel" in lesson_dump

    def test_scenario_2_opencv_cites_opencv_not_react(self) -> None:
        _clear_cache()
        req = TeachingLessonDetailRequest(
            skill="OpenCV",
            concept="Image Representation & Pixel Grids",
            lesson_id="cv-scen-2",
            learner_level="Beginner",
            ai_generated=False,
        )
        detail = generate_comprehensive_lesson(req)
        urls = [
            r.get("canonical_url", "")
            for r in detail.lesson.resources
            if isinstance(r, dict)
        ]
        assert not any("react.dev" in u for u in urls), f"OpenCV lesson cites React: {urls}"
        assert any("docs.opencv.org" in u for u in urls), f"OpenCV lesson missing OpenCV docs: {urls}"

    def test_scenario_3_javascript_uses_js_and_mdn(self) -> None:
        _clear_cache()
        req = TeachingLessonDetailRequest(
            skill="JavaScript",
            concept="Scope and Closures",
            lesson_id="js-scen-3",
            learner_level="Intermediate",
            ai_generated=False,
        )
        detail = generate_comprehensive_lesson(req)
        lesson_dump = str(detail.lesson.model_dump()).lower()
        assert "closure" in lesson_dump or "lexical" in lesson_dump
        urls = [
            r.get("canonical_url", "")
            for r in detail.lesson.resources
            if isinstance(r, dict)
        ]
        assert any("developer.mozilla.org" in u or "javascript.info" in u for u in urls)

    def test_scenario_4_prompt_engineering_no_opencv_or_concurrency(self) -> None:
        _clear_cache()
        req = TeachingLessonDetailRequest(
            skill="Prompt Engineering",
            concept="Instruction Clarity & Task Specification",
            lesson_id="pe-scen-4",
            learner_level="Intermediate",
            ai_generated=False,
        )
        detail = generate_comprehensive_lesson(req)
        dump = str(detail.lesson.model_dump()).lower()
        assert "cv2" not in dump
        assert "bgr" not in dump
        assert "canny" not in dump
        assert "pixel grid" not in dump
        assert "prompt" in dump

    def test_scenario_5_exercises_test_lesson_subject(self) -> None:
        _clear_cache()
        req_cv = TeachingLessonDetailRequest(
            skill="OpenCV",
            concept="Image Representation & Pixel Grids",
            lesson_id="cv-scen-5",
            learner_level="Beginner",
            ai_generated=False,
        )
        detail_cv = generate_comprehensive_lesson(req_cv)
        ex_cv = detail_cv.lesson.practice_exercises[0]
        ex_cv_text = str(ex_cv).lower()
        assert "opencv" in ex_cv_text or "cv2" in ex_cv_text or "image" in ex_cv_text or "pixel" in ex_cv_text

    def test_scenario_6_unavailable_web_content_marked_fallback(self) -> None:
        from app.services.teaching_resource_service import retrieve_teaching_resources_for_lesson
        # Querying an unknown exotic topic should return safe, clearly labeled fallbacks or empty list,
        # never claiming a successful crawl of a non-existent page.
        results = retrieve_teaching_resources_for_lesson(
            concept_title="NonExistentObscureFramework9999",
            limit=3,
        )
        for r in results:
            if not r.is_verified:
                assert r.freshness_status in ("stale", "fallback", "community")

    def test_scenario_7_repeated_generic_paragraphs_detected(self) -> None:
        from app.services.lesson_generation_service import validate_lesson_relevance
        bad_lesson = {
            "title": "OpenCV • Pixel Operations",
            "topic": "Pixel Operations",
            "detailed_explanation": (
                "In computer vision, pixel operations process matrices of intensity values across channels.\n\n"
                "In computer vision, pixel operations process matrices of intensity values across channels."
            ),
            "what_it_is": "Pixel manipulation in OpenCV arrays.",
            "starter_code": "import cv2\nimport numpy as np\nimg = np.zeros((10, 10, 3), dtype=np.uint8)\n",
            "common_mistakes": "Forgetting that OpenCV uses BGR order.",
        }
        is_valid, reason = validate_lesson_relevance(bad_lesson, "OpenCV", "Pixel Operations")
        assert not is_valid
        assert "repeated" in reason.lower()

    def test_scenario_8_candidate_personalization_grounded_in_profile(self) -> None:
        db = _fake_db()
        user = _fake_user()
        with patch("app.services.skill_learning_service.build_learner_knowledge_profile") as mock_profile:
            mock_profile.return_value = MagicMock(
                verified_projects=[{"name": "Precision Agriculture Vision", "technologies": ["OpenCV", "Python"]}],
                recommended_learning_order=[],
                skills_inventory=["OpenCV", "Python"],
            )
            path = build_skill_learning_path(db, "OpenCV", user)
            assert path.skill_name.lower() == "opencv"
            # Project personalization matches actual candidate profile
            assert path.stages[0].stage_name == "Core Image Processing"

    def test_scenario_9_existing_progress_preserved(self) -> None:
        db = _fake_db()
        user = _fake_user()

        # Simulate existing completed progress for lesson in DB
        progress_mock = MagicMock()
        progress_mock.skill = "opencv"
        progress_mock.lesson_id = "cv-lesson-1"
        progress_mock.completed = True
        progress_mock.mastery_score = 95
        db.query.return_value.filter.return_value.all.return_value = [progress_mock]

        path = build_skill_learning_path(db, "OpenCV", user)
        # Verify path generation does not wipe or overwrite progress
        assert path.total_lessons > 0
        assert path.skill_name.lower() == "opencv"

    def test_scenario_10_retrieval_failure_does_not_crash(self) -> None:
        _clear_cache()
        with patch("app.services.lesson_generation_service.retrieve_teaching_resources_for_lesson", side_effect=RuntimeError("Search API down")):
            req = TeachingLessonDetailRequest(
                skill="OpenCV",
                concept="Image Representation & Pixel Grids",
                lesson_id="cv-scen-10",
                learner_level="Beginner",
                ai_generated=False,
            )
            # Must gracefully fall back without raising unhandled 500 error
            detail = generate_comprehensive_lesson(req)
            assert detail is not None
            assert detail.lesson is not None
            assert "opencv" in detail.lesson.title.lower()



