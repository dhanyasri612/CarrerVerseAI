from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.ai.errors import AIProviderTimeoutError
from app.ai.rag.generator import rag_generator
from app.core.dependencies import get_current_user
from app.main import app
from app.schemas.rag import RAGGenerationResponse


client = TestClient(app)


class FakeRAGGenerator:
    def __init__(self):
        self.calls = []

    def generate_response(self, **kwargs):
        self.calls.append(kwargs)
        return RAGGenerationResponse(
            candidate_id=kwargs["candidate_id"],
            query=kwargs["query"],
            answer="Python and FastAPI are supported by the retrieved profile evidence.",
            model_name="fake-model",
            retrieval_metadata={
                "chroma_status": "available",
                "neo4j_status": "available",
                "sources": ["chromadb", "neo4j"],
            },
            prompt_length=100,
            context_length=80,
        )


def test_rag_endpoint_uses_authenticated_candidate_and_returns_retrieval_metadata(monkeypatch):
    fake_generator = FakeRAGGenerator()
    monkeypatch.setattr("app.routers.ai.rag_generator", fake_generator)
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=42)

    try:
        response = client.post(
            "/ai/rag",
            json={"query": "What are my strongest technical skills?", "language": "en"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["candidate_id"] == 42
    assert response.json()["retrieval_metadata"]["neo4j_status"] == "available"
    assert fake_generator.calls[0]["candidate_id"] == 42
    assert fake_generator.calls[0]["language"] == "en"


def test_rag_endpoint_maps_provider_failures(monkeypatch):
    class FailingRAGGenerator:
        def generate_response(self, **kwargs):
            raise AIProviderTimeoutError("provider timeout")

    monkeypatch.setattr("app.routers.ai.rag_generator", FailingRAGGenerator())
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=42)

    try:
        response = client.post("/ai/rag", json={"query": "Summarize my profile"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 504