import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./ai_foundation_test.db")

import pytest
from fastapi.testclient import TestClient

from app.ai.errors import AIConfigurationError, AIInvalidResponseError
from app.ai.parser import parse_test_response
from app.ai.providers.base import ProviderResponse
from app.core.dependencies import get_current_user
from app.main import app
from app.services.ai_service import ai_service


client = TestClient(app)


class FakeProvider:
    def __init__(self, content: str = '{"success": true, "message": "An API is a way for software systems to communicate."}'):
        self.content = content

    def generate(self, **kwargs) -> ProviderResponse:
        return ProviderResponse(content=self.content, model="fake-model")


def test_ai_endpoint_requires_existing_authentication():
    response = client.post(
        "/ai/test",
        json={"message": "Explain what an API is in simple terms."},
    )

    assert response.status_code == 401


def test_service_returns_valid_structured_response(monkeypatch):
    monkeypatch.setattr(ai_service, "provider", FakeProvider())

    result, model = ai_service.test("Explain what an API is in simple terms.")

    assert result.success is True
    assert result.message.startswith("An API")
    assert model == "fake-model"


def test_ai_endpoint_returns_structured_response(monkeypatch):
    monkeypatch.setattr(ai_service, "provider", FakeProvider())
    app.dependency_overrides[get_current_user] = lambda: object()

    try:
        response = client.post(
            "/ai/test",
            json={"message": "Explain what an API is in simple terms."},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "An API is a way for software systems to communicate.",
        "model": "fake-model",
    }


def test_parser_rejects_invalid_json():
    with pytest.raises(AIInvalidResponseError):
        parse_test_response("not-json")


def test_missing_key_is_reported_without_exposing_secrets():
    from app.ai.providers.groq_provider import GroqProvider

    with pytest.raises(AIConfigurationError, match="GROQ_API_KEY"):
        GroqProvider(api_key=None)