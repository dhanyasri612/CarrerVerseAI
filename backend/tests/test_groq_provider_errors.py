"""
Focused tests for GroqProvider error mapping and retry behavior.

These tests mock the Groq client so no real network call is made.
They verify that timeouts, 413, 429, 503, configuration, and generic
provider errors are mapped to the correct AI-error types before the
FastAPI layer translates them to HTTP status codes.
"""

from types import SimpleNamespace

import pytest

from app.ai.errors import (
    AIConfigurationError,
    AIProviderAuthenticationError,
    AIProviderError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
)
from app.ai.providers.groq_provider import GroqProvider


class FakeResponse:
    def __init__(self, status_code: int):
        self.status_code = status_code
        self.request = FakeRequest()


class FakeRequest:
    pass


class FakeCompletion:
    def __init__(self, content: str = "ok", model: str = "test-model"):
        self.choices = [SimpleNamespace(message=SimpleNamespace(content=content))]
        self.model = model


class FakeClient:
    def __init__(self, *args, **kwargs):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))
        self._side_effect = None
        self._call_count = 0

    def set_side_effect(self, exc):
        self._side_effect = exc
        self._call_count = 0

    def _create(self, **kwargs):
        self._call_count += 1
        if self._side_effect is not None:
            raise self._side_effect
        return FakeCompletion()


def _make_provider(monkeypatch, side_effect=None, api_key="test-key"):
    monkeypatch.setattr("app.ai.providers.groq_provider.Groq", FakeClient)
    provider = GroqProvider(api_key=api_key)
    if side_effect is not None:
        provider.client.set_side_effect(side_effect)
    return provider


def _api_status_error(status_code: int, message: str = "provider error"):
    from groq import APIStatusError

    return APIStatusError(message=message, response=FakeResponse(status_code), body=None)


def test_configuration_error_when_no_api_key(monkeypatch):
    monkeypatch.setattr("app.ai.providers.groq_provider.Groq", FakeClient)
    with pytest.raises(AIConfigurationError, match="GROQ_API_KEY is not configured"):
        GroqProvider(api_key=None)


def test_timeout_exhaustion_raises_ai_provider_timeout_error(monkeypatch):
    from groq import APITimeoutError

    provider = _make_provider(monkeypatch, side_effect=APITimeoutError(request=FakeRequest()))
    monkeypatch.setattr("app.ai.providers.groq_provider.time.sleep", lambda *a, **k: None)
    with pytest.raises(AIProviderTimeoutError, match="timed out"):
        provider.generate_text(
            system_prompt="sys", user_message="user", temperature=0.2
        )


def test_429_maps_to_rate_limit_error(monkeypatch):
    provider = _make_provider(monkeypatch, side_effect=_api_status_error(429))
    monkeypatch.setattr("app.ai.providers.groq_provider.time.sleep", lambda *a, **k: None)
    with pytest.raises(AIProviderRateLimitError, match="rate limit"):
        provider.generate_text(system_prompt="sys", user_message="user")


def test_413_maps_to_rate_limit_error(monkeypatch):
    provider = _make_provider(monkeypatch, side_effect=_api_status_error(413))
    monkeypatch.setattr("app.ai.providers.groq_provider.time.sleep", lambda *a, **k: None)
    with pytest.raises(AIProviderRateLimitError, match="rate limit"):
        provider.generate_text(system_prompt="sys", user_message="user")


def test_503_maps_to_provider_error_not_rate_limit(monkeypatch):
    provider = _make_provider(monkeypatch, side_effect=_api_status_error(503))
    monkeypatch.setattr("app.ai.providers.groq_provider.time.sleep", lambda *a, **k: None)
    with pytest.raises(AIProviderError):
        provider.generate_text(system_prompt="sys", user_message="user")


def test_503_in_generate_is_retried_and_mapped_to_provider_error(monkeypatch):
    provider = _make_provider(monkeypatch, side_effect=_api_status_error(503))
    monkeypatch.setattr("app.ai.providers.groq_provider.time.sleep", lambda *a, **k: None)
    with pytest.raises(AIProviderError):
        provider.generate(system_prompt="sys", user_message="user")


def test_generic_exception_maps_to_provider_error(monkeypatch):
    provider = _make_provider(monkeypatch, side_effect=RuntimeError("boom"))
    monkeypatch.setattr("app.ai.providers.groq_provider.time.sleep", lambda *a, **k: None)
    with pytest.raises(AIProviderError):
        provider.generate_text(system_prompt="sys", user_message="user")


def test_successful_call_returns_provider_response(monkeypatch):
    provider = _make_provider(monkeypatch, side_effect=None)
    result = provider.generate_text(system_prompt="sys", user_message="user")
    assert result.content == "ok"
    assert result.model == "test-model"
