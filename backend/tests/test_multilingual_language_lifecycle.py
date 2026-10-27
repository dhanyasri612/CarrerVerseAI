import json
from types import SimpleNamespace

import pytest

from app.ai.agents.interview_prompt import interview_prompt_builder
from app.ai.agents.recommendation_prompt import recommendation_prompt_builder
from app.ai.language.prompt_builder import language_prompt_builder
from app.schemas.career_ai import CareerIntelligenceRequest
from app.schemas.interview_session import InterviewAnswerRequest, InterviewSessionCreateRequest
from app.schemas.teaching import TeachingChatRequest, TeachingChatTurn, TeachingEvaluationRequest
from app.services import teaching_service


def test_explicit_language_is_normalized_and_rejected_instead_of_falling_back_to_english():
    assert CareerIntelligenceRequest(query="career advice", language="ta-IN").language == "ta"
    assert InterviewSessionCreateRequest(language="hi-IN").language == "hi"
    with pytest.raises(ValueError):
        InterviewAnswerRequest(answer="answer", language="xx")


def test_language_policy_is_in_the_system_prompt_for_all_agent_prompt_builders():
    policy = language_prompt_builder.with_system_language_policy("base", "ta")
    assert "English-only output is not" in policy
    assert "Tamil (ta)" in policy

    # A minimal context object is sufficient because this assertion targets the
    # prompt boundary, where the selected language must be enforced.
    from app.schemas.rag import RAGRetrievedContext

    context = RAGRetrievedContext(candidate_id=1, query="question", context_text="verified")
    assert "Tamil (ta)" in interview_prompt_builder.build_prompt(
        "question", "general", None, context, {}, language="ta"
    ).system_prompt
    assert "Hindi (hi)" in recommendation_prompt_builder.build_prompt(
        "question", context, language="hi"
    ).system_prompt


# ── Teaching evaluation: Tamil language in system prompt ──────────────────────

class FakeTeachingProvider:
    """Stub that records the system_prompt and returns a minimal valid JSON response."""

    def __init__(self):
        self.system_prompts: list = []
        self.user_messages: list = []

    def generate_text(self, *, system_prompt, user_message, temperature=0.3, max_completion_tokens=None):
        self.system_prompts.append(system_prompt)
        self.user_messages.append(user_message)
        content = json.dumps({
            "what_is_right": "Correct approach identified.",
            "what_is_wrong": "Edge cases missing.",
            "masterclass_lesson": "Use hash map for O(n) lookup.",
            "optimal_solution": "def solution(): pass",
            "key_takeaway": "Trade space for time.",
            "suggested_follow_up": "What if the array is sorted?",
        })
        return SimpleNamespace(content=content, model="fake-model")


def test_teaching_evaluation_language_tamil(monkeypatch):
    """evaluate_and_teach must inject a multilingual clause mentioning 'Tamil'
    into the system_prompt when language='ta'."""
    provider = FakeTeachingProvider()
    monkeypatch.setattr(teaching_service, "get_model_provider", lambda: provider)

    req = TeachingEvaluationRequest(
        section_id="dsa",
        lesson_id="test-lesson",
        concept_title="Two Sum",
        question_prompt="Find two numbers that add up to target.",
        candidate_thoughts="I would use a hash map to store complements.",
        language="ta",
    )
    # evaluate_and_teach does not need a db session or user
    result = teaching_service.evaluate_and_teach(req, current_user=SimpleNamespace(id=1))

    assert result.what_is_right
    assert result.masterclass_lesson

    # At least one system prompt must contain 'Tamil' from the multilingual clause
    assert any("Tamil" in sp for sp in provider.system_prompts), (
        "Expected 'Tamil' in system_prompt for language='ta', but got: "
        + str([sp[:200] for sp in provider.system_prompts])
    )


def test_teaching_chat_language_hindi(monkeypatch):
    """chat_with_teaching_mentor must inject a multilingual clause mentioning
    'Hindi' into the system_prompt when language='hi'."""
    provider = FakeTeachingProvider()

    # Override generate_text to return a plain string (as the chat path uses .content directly)
    def _generate_text(*, system_prompt, user_message, temperature=0.3, max_completion_tokens=None):
        provider.system_prompts.append(system_prompt)
        provider.user_messages.append(user_message)
        return SimpleNamespace(content="Hooks को समझने के लिए: useState और useEffect.", model="fake-model")

    provider.generate_text = _generate_text
    monkeypatch.setattr(teaching_service, "get_model_provider", lambda: provider)

    req = TeachingChatRequest(
        mode="skill",
        target_id="React",
        message="Explain hooks",
        language="hi",
    )

    # chat_with_teaching_mentor requires db and current_user; use minimal stubs
    class FakeDB:
        def query(self, *args, **kwargs):
            return self

        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return None

        def all(self):
            return []

        def add(self, *args, **kwargs):
            pass

        def flush(self):
            pass

        def commit(self):
            pass

        def rollback(self):
            pass

        def refresh(self, *args, **kwargs):
            pass

    fake_user = SimpleNamespace(id=1, target_role="Software Engineer")

    # build_skill_learning_path is imported locally inside chat_with_teaching_mentor;
    # patch it on the module object so the local import picks up the stub.
    import app.services.skill_learning_service as sls_module

    monkeypatch.setattr(
        sls_module,
        "build_skill_learning_path",
        lambda db, skill, user: SimpleNamespace(
            skill_name="React",
            total_stages=1,
            connected_projects=[],
            stages=[],
        ),
    )

    result = teaching_service.chat_with_teaching_mentor(FakeDB(), fake_user, req)

    assert result.reply
    assert any("Hindi" in sp or "Hinglish" in sp for sp in provider.system_prompts), (
        "Expected 'Hindi' or 'Hinglish' in system_prompt for language='hi', but got: "
        + str([sp[:200] for sp in provider.system_prompts])
    )
