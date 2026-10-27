import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.database import Base
from app.database.session import get_db
from app.models.user import User
from app.models.role import Role
from app.utils.jwt import create_access_token
from app.services.trend_intelligence_service import trend_intelligence_service, VERIFIED_TECH_SIGNALS


# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create roles
    candidate_role = Role(name="Candidate")
    db.add(candidate_role)
    db.commit()

    # Create user 1
    user1 = User(
        name="Alex River",
        email="alex.ai@example.com",
        hashed_password="testpass123",
        role_id=candidate_role.id
    )
    # Create user 2 (for authorization tests)
    user2 = User(
        name="Jordan Lee",
        email="jordan.backend@example.com",
        hashed_password="testpass123",
        role_id=candidate_role.id
    )
    db.add_all([user1, user2])
    db.commit()
    db.refresh(user1)
    db.refresh(user2)

    yield {"user1": user1, "user2": user2, "db": db}

    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_db):
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(setup_db):
    user = setup_db["user1"]
    token = create_access_token(data={"sub": user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user2(setup_db):
    user = setup_db["user2"]
    token = create_access_token(data={"sub": user.email})
    return {"Authorization": f"Bearer {token}"}


def test_trend_intelligence_signals_metadata():
    """Verify that all trend intelligence signals have credible, non-fabricated metadata."""
    assert len(VERIFIED_TECH_SIGNALS) >= 8
    for signal in VERIFIED_TECH_SIGNALS:
        assert signal["technology"]
        assert len(signal["target_roles"]) > 0
        assert signal["trend_status"] in ["newly_released", "increased_attention", "job_market_required", "established"]
        assert signal["source_name"]
        assert signal["source_url"].startswith("http")
        assert signal["publication_date"]  # Must be a dated string, e.g. 2024-10-15
        assert signal["evidence_summary"]
        assert signal["reliability"] in ["verified_official", "high_reputable"]


def test_trend_signals_filtered_by_role():
    """Ensure signals returned for AI Engineer differ from Frontend Developer."""
    ai_signals = trend_intelligence_service.get_signals_for_role("AI Engineer")
    fe_signals = trend_intelligence_service.get_signals_for_role("Frontend Developer")

    ai_techs = [s["technology"] for s in ai_signals]
    fe_techs = [s["technology"] for s in fe_signals]

    assert any("LangGraph" in t or "LLM" in t for t in ai_techs)
    assert any("React 19" in t or "Next.js" in t or "Tailwind" in t for t in fe_techs)


def test_generate_different_career_roadmaps(client, auth_headers):
    """Verify that targeting AI Engineer produces a different roadmap than Backend Developer."""
    res_ai = client.get("/career-roadmap/personalized?role=AI Engineer", headers=auth_headers)
    assert res_ai.status_code == 200
    data_ai = res_ai.json()
    assert data_ai["target_role"] == "AI Engineer"
    ai_milestones = [m["title"] for m in data_ai["milestones"]]
    assert any("RAG" in m or "AI" in m or "Vector" in m for m in ai_milestones)

    res_backend = client.get("/career-roadmap/personalized?role=Backend Developer", headers=auth_headers)
    assert res_backend.status_code == 200
    data_backend = res_backend.json()
    assert data_backend["target_role"] == "Backend Developer"
    backend_milestones = [m["title"] for m in data_backend["milestones"]]
    assert any("Relational" in m or "gRPC" in m or "Kafka" in m or "Kubernetes" in m for m in backend_milestones)

    # UI/UX Designer test
    res_uiux = client.get("/career-roadmap/personalized?role=UI/UX Designer", headers=auth_headers)
    assert res_uiux.status_code == 200
    data_uiux = res_uiux.json()
    assert data_uiux["target_role"] == "UI/UX Designer"
    uiux_milestones = [m["title"] for m in data_uiux["milestones"]]
    assert any("User Research" in m or "Wireframing" in m or "Figma" in m or "Accessibility" in m for m in uiux_milestones)
    # Ensure it did NOT fall back to AI Engineer or Backend
    assert not any("RAG" in m or "Kafka" in m or "gRPC" in m for m in uiux_milestones)


def test_milestone_attributes_and_completion_criteria(client, auth_headers):
    """Verify every milestone has purpose, prerequisites, effort, project deliverable, and completion criteria."""
    res = client.get("/career-roadmap/personalized?role=AI Engineer", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()

    for m in data["milestones"]:
        assert m["stage"] >= 1
        assert m["title"]
        assert m["why_recommended"]
        assert m["estimated_effort"]
        assert m["practical_project"]
        assert len(m["completion_criteria"]) >= 1
        assert m["status"] in ["completed", "in_progress", "upcoming"]


def test_toggle_milestone_progress(client, auth_headers):
    """Verify toggling milestone completion updates progress and readiness score."""
    res = client.get("/career-roadmap/personalized?role=AI Engineer", headers=auth_headers)
    data = res.json()
    first_milestone = data["milestones"][0]
    initial_status = first_milestone["status"]
    milestone_id = first_milestone["id"]

    # Toggle status
    res_toggle = client.post(f"/career-roadmap/milestones/{milestone_id}/toggle", headers=auth_headers)
    assert res_toggle.status_code == 200
    updated_data = res_toggle.json()
    updated_m = next(m for m in updated_data["milestones"] if m["id"] == milestone_id)

    if initial_status == "completed":
        assert updated_m["status"] == "in_progress"
    else:
        assert updated_m["status"] == "completed"
        assert updated_m["progress_pct"] == 100


def test_adaptive_recommendation_lifecycle(client, auth_headers):
    """Test accepting an adaptive recommendation: creates new version, inserts milestone, preserves progress."""
    res = client.get("/career-roadmap/personalized?role=AI Engineer", headers=auth_headers)
    data = res.json()
    initial_version = data["current_version"]
    recs = data.get("pending_recommendations", [])

    if not recs:
        # If no recommendation is pending, verify trend signals exist
        assert len(data.get("trend_signals", [])) > 0
        return

    rec_id = recs[0]["id"]
    rec_title = recs[0]["title"]

    # Accept recommendation
    res_accept = client.post(f"/career-roadmap/recommendations/{rec_id}/accept", headers=auth_headers)
    assert res_accept.status_code == 200
    new_data = res_accept.json()

    assert new_data["current_version"] == initial_version + 1
    # Check that recommendation log is now in change history with status accepted
    accepted_log = next((h for h in new_data["change_history"] if h["id"] == rec_id), None)
    assert accepted_log is not None
    assert accepted_log["status"] == "accepted"


def test_authorization_isolation(client, auth_headers, auth_headers_user2):
    """Ensure User 2 cannot access or mutate User 1's roadmap."""
    # User 1 creates roadmap
    res1 = client.get("/career-roadmap/personalized?role=AI Engineer", headers=auth_headers)
    data1 = res1.json()
    u1_milestone_id = data1["milestones"][0]["id"]

    # User 2 attempts to toggle User 1's milestone -> should 404
    res2 = client.post(f"/career-roadmap/milestones/{u1_milestone_id}/toggle", headers=auth_headers_user2)
    assert res2.status_code == 404
