import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./resume_ai_test.db")

from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.ai.errors import AIProviderError
from app.core.dependencies import get_current_user
from app.main import app
from app.database.session import SessionLocal
from app.models.resume import Resume
from app.services import skill_gap_ai_service
from app.services.ai_service import ai_service
from app.schemas.skill_gap_ai import SkillGapAnalysis

client = TestClient(app)


VALID_ANALYSIS = {
    "target_role": "Backend Developer",
    "current_skill_summary": {
        "demonstrated_skills": ["Python", "FastAPI"],
        "supported_skills": ["PostgreSQL"],
        "partially_supported_skills": [],
        "self_reported_skills": [],
        "unverified_skills": [],
    },
    "skill_gaps": [
        {
            "skill": "Docker",
            "category": "DevOps",
            "status": "missing",
            "confidence": "high",
            "priority": "high",
            "reason": "Not found in available candidate evidence.",
            "evidence": [],
            "related_skills": ["FastAPI"],
        }
    ],
    "roadmap": [
        {
            "stage": 1,
            "title": "Containerization foundation",
            "goal": "Build deployment skills around the existing backend experience.",
            "skills": ["Docker"],
            "prerequisites": ["FastAPI"],
            "estimated_effort": "1-2 weeks",
            "learning_objectives": ["Build a Dockerfile for an existing API."],
            "practical_task": "Containerize the existing backend and run it locally.",
        }
    ],
    "summary": {
        "total_gaps": 1,
        "critical_gaps": 0,
        "high_priority_gaps": 1,
        "medium_priority_gaps": 0,
        "low_priority_gaps": 0,
    },
}


class FakeSkillGapProvider:
    def generate(self, **kwargs):
        import json

        return type("Response", (), {"content": json.dumps(VALID_ANALYSIS), "model": "fake-model"})()


def owned_resume():
    db = SessionLocal()
    resume = db.query(Resume).first()
    db.close()
    assert resume is not None
    return resume


def test_skill_gap_schema_validates_controlled_values():
    result = SkillGapAnalysis.model_validate(VALID_ANALYSIS)
    assert result.skill_gaps[0].status == "missing"
    assert result.roadmap[0].skills == ["Docker"]


def test_skill_gap_schema_rejects_unknown_status():
    invalid = {**VALID_ANALYSIS, "skill_gaps": [{**VALID_ANALYSIS["skill_gaps"][0], "status": "unknown"}]}
    try:
        SkillGapAnalysis.model_validate(invalid)
        assert False, "Expected schema validation to fail"
    except ValidationError:
        assert True


def test_skill_gap_ai_service_returns_structured_response(monkeypatch):
    monkeypatch.setattr(ai_service, "provider", FakeSkillGapProvider())
    result, model = ai_service.generate_skill_gap_analysis(
        target_role="Backend Developer",
        role_requirements=["Python", "Docker"],
        candidate_evidence='{"skills":["Python"]}',
    )
    assert model == "fake-model"
    assert result.skill_gaps[0].reason == "Not found in available candidate evidence."


def test_skill_gap_endpoint_requires_authentication():
    response = client.post(
        "/ai/skill-gap/analyze",
        json={"resume_id": 1, "target_role": "Backend Developer", "role_requirements": ["Docker"]},
    )
    assert response.status_code == 401


def test_skill_gap_endpoint_rejects_missing_resume(monkeypatch):
    monkeypatch.setattr(ai_service, "provider", FakeSkillGapProvider())
    app.dependency_overrides[get_current_user] = lambda: type("User", (), {"id": 999999})()
    try:
        response = client.post(
            "/ai/skill-gap/analyze",
            json={"resume_id": 999999, "target_role": "Backend Developer", "role_requirements": ["Docker"]},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 404


def test_skill_gap_endpoint_rejects_missing_role_requirements(monkeypatch):
    app.dependency_overrides[get_current_user] = lambda: type("User", (), {"id": 3})()
    try:
        response = client.post(
            "/ai/skill-gap/analyze",
            json={"resume_id": 1, "target_role": "Unknown Role"},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code in {400, 404}


def test_skill_gap_endpoint_returns_personalized_analysis(monkeypatch):
    resume = owned_resume()
    monkeypatch.setattr(
        skill_gap_ai_service,
        "analyze_resume_intelligence",
        lambda **kwargs: type("ResumeAnalysis", (), {"model_dump": lambda self, **options: {"skills": ["Python"]}})(),
    )
    monkeypatch.setattr(
        skill_gap_ai_service,
        "build_unified_candidate_profile",
        lambda **kwargs: type("Profile", (), {"model_dump": lambda self, **options: {"unified_skills": ["Python"]}})(),
    )
    monkeypatch.setattr(ai_service, "provider", FakeSkillGapProvider())
    app.dependency_overrides[get_current_user] = lambda: type("User", (), {"id": resume.user_id})()
    try:
        response = client.post(
            "/ai/skill-gap/analyze",
            json={"resume_id": resume.id, "target_role": "Backend Developer", "role_requirements": ["Python", "Docker"]},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["target_role"] == "Backend Developer"
    assert response.json()["roadmap"][0]["skills"] == ["Docker"]


def test_skill_gap_endpoint_translates_provider_failure(monkeypatch):
    resume = owned_resume()
    def fail(**kwargs):
        raise AIProviderError("provider unavailable")

    monkeypatch.setattr(
        skill_gap_ai_service,
        "analyze_resume_intelligence",
        lambda **kwargs: type("ResumeAnalysis", (), {"model_dump": lambda self, **options: {}})(),
    )
    monkeypatch.setattr(
        skill_gap_ai_service,
        "build_unified_candidate_profile",
        lambda **kwargs: type("Profile", (), {"model_dump": lambda self, **options: {}})(),
    )
    monkeypatch.setattr(ai_service, "generate_skill_gap_analysis", fail)
    app.dependency_overrides[get_current_user] = lambda: type("User", (), {"id": resume.user_id})()
    try:
        response = client.post(
            "/ai/skill-gap/analyze",
            json={"resume_id": resume.id, "target_role": "Backend Developer", "role_requirements": ["Docker"]},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 502
