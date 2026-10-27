from types import SimpleNamespace

import pytest

from app.services import conversational_interview_service as interview_service
from app.services import profile_quiz_service as quiz_service


class InvalidProvider:
    def generate_text(self, **_kwargs):
        return SimpleNamespace(content="not valid json")


def test_quiz_invalid_provider_json_is_a_controlled_state_error(monkeypatch):
    monkeypatch.setattr(quiz_service, "get_model_provider", lambda: InvalidProvider())

    with pytest.raises(quiz_service.QuizSessionStateError, match="invalid quiz response"):
        quiz_service._json_response("prompt", {"candidate": "evidence"})


def test_interview_invalid_provider_json_is_a_controlled_state_error(monkeypatch):
    monkeypatch.setattr(interview_service, "get_model_provider", lambda: InvalidProvider())

    with pytest.raises(interview_service.InterviewSessionStateError, match="invalid interview response"):
        interview_service._provider_json("prompt", "payload")


def test_interview_final_report_repair_failure_is_controlled(monkeypatch):
    monkeypatch.setattr(interview_service, "get_model_provider", lambda: InvalidProvider())

    with pytest.raises(interview_service.InterviewSessionStateError, match="invalid interview response"):
        interview_service._provider_json("prompt", "payload", max_completion_tokens=1200)


# ── LangGraph Teaching Workflow Provider Failure Tests ────────────────────────

class RaisingProvider:
    def __init__(self, exc):
        self.exc = exc

    def generate_text(self, **kwargs):
        raise self.exc


class MalformedProvider:
    def generate_text(self, **kwargs):
        return SimpleNamespace(content="<<<malformed:::unparseable>>>")


class EmptyProvider:
    def generate_text(self, **kwargs):
        return SimpleNamespace(content="")


def test_teaching_workflow_handles_timeout_gracefully(monkeypatch):
    from app.ai.errors import AIProviderTimeoutError
    from app.services.teaching_agent_service import execute_teaching_agent_workflow
    from app.schemas.teaching import TeachingChatRequest

    monkeypatch.setattr("app.ai.providers.get_model_provider", lambda: RaisingProvider(AIProviderTimeoutError("Request timed out")))
    req = TeachingChatRequest(mode="skill", target_id="FastAPI", message="Explain dependency injection")
    res = execute_teaching_agent_workflow(req)
    assert res is not None
    assert res.reply is not None
    assert len(res.reply) > 20
    assert "Traceback" not in res.reply
    assert "AIProviderTimeoutError" not in res.reply


def test_teaching_workflow_handles_rate_limit_gracefully(monkeypatch):
    from app.ai.errors import AIProviderRateLimitError
    from app.services.teaching_agent_service import execute_teaching_agent_workflow
    from app.schemas.teaching import TeachingChatRequest

    monkeypatch.setattr("app.ai.providers.get_model_provider", lambda: RaisingProvider(AIProviderRateLimitError("Rate limit exceeded")))
    req = TeachingChatRequest(mode="skill", target_id="React", message="How does reconciliation work?")
    res = execute_teaching_agent_workflow(req)
    assert res is not None
    assert res.reply is not None
    assert len(res.reply) > 20
    assert "Traceback" not in res.reply


def test_teaching_workflow_handles_malformed_response_gracefully(monkeypatch):
    from app.services.teaching_agent_service import execute_teaching_agent_workflow
    from app.schemas.teaching import TeachingChatRequest

    monkeypatch.setattr("app.ai.providers.get_model_provider", lambda: MalformedProvider())
    req = TeachingChatRequest(mode="skill", target_id="Docker", message="Explain containers vs VMs")
    res = execute_teaching_agent_workflow(req)
    assert res is not None
    assert res.reply is not None
    assert len(res.reply) > 0


def test_teaching_workflow_handles_unavailable_provider_gracefully(monkeypatch):
    from app.ai.errors import AIProviderError
    from app.services.teaching_agent_service import execute_teaching_agent_workflow
    from app.schemas.teaching import TeachingChatRequest

    def _fail():
        raise AIProviderError("Service temporarily unavailable")

    monkeypatch.setattr("app.ai.providers.get_model_provider", _fail)
    req = TeachingChatRequest(mode="skill", target_id="PostgreSQL", message="What is MVCC?")
    res = execute_teaching_agent_workflow(req)
    assert res is not None
    assert res.reply is not None
    assert "Traceback" not in res.reply

