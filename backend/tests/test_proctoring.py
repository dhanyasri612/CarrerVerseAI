import pytest
import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.database.session import SessionLocal
from app.models.user import User
from app.models.interview_session import InterviewSession
from app.models.proctoring_event import ProctoringEvent
from app.schemas.proctoring import (
    ProctoringEventCreateRequest,
    VALID_PROCTORING_EVENT_TYPES,
)
from app.services.proctoring_service import (
    record_proctoring_event,
    get_session_proctoring_summary,
)
from app.services.conversational_interview_service import end_interview_session


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def candidate(db):
    user = db.query(User).first()
    if not user:
        user = User(
            email=f"candidate_{uuid.uuid4().hex[:8]}@example.com",
            name="Candidate One",
            hashed_password="hash",
            role_id=1,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture
def other_candidate(db, candidate):
    user = (
        db.query(User)
        .filter(User.id != candidate.id)
        .first()
    )
    if not user:
        user = User(
            email=f"other_{uuid.uuid4().hex[:8]}@example.com",
            name="Candidate Two",
            hashed_password="hash",
            role_id=candidate.role_id or 1,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture
def active_session(db, candidate):
    sess = InterviewSession(
        session_id=str(uuid.uuid4()),
        candidate_id=candidate.id,
        target_role="Full Stack Engineer",
        interview_mode="github",
        status="active",
        created_at=datetime.utcnow(),
    )
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return sess


def test_record_proctoring_event_success(db, candidate, active_session):
    req = ProctoringEventCreateRequest(
        event_type="visibility_hidden",
        duration_ms=1200,
        metadata={"cause": "user switched browser tab"},
    )
    res = record_proctoring_event(db, candidate, active_session.session_id, req)
    assert res.session_id == active_session.session_id
    assert res.candidate_id == candidate.id
    assert res.event_type == "visibility_hidden"
    assert res.severity == "warning"
    assert res.action_taken == "warning_issued"
    assert res.metadata_json.get("duration_ms") == 1200


def test_record_proctoring_event_candidate_isolation(db, other_candidate, active_session):
    req = ProctoringEventCreateRequest(
        event_type="window_blur",
    )
    with pytest.raises(HTTPException) as exc:
        record_proctoring_event(db, other_candidate, active_session.session_id, req)
    assert exc.value.status_code == 404


def test_record_proctoring_event_invalid_type(db, candidate, active_session):
    req = ProctoringEventCreateRequest(
        event_type="suspicious_ai_detected",
    )
    with pytest.raises(HTTPException) as exc:
        record_proctoring_event(db, candidate, active_session.session_id, req)
    assert exc.value.status_code == 400
    assert "Invalid proctoring event type" in exc.value.detail


def test_record_proctoring_event_flood_debouncing(db, candidate, active_session):
    req = ProctoringEventCreateRequest(
        event_type="fullscreen_exit",
    )
    # First record
    res1 = record_proctoring_event(db, candidate, active_session.session_id, req)
    # Immediate duplicate within 500ms
    res2 = record_proctoring_event(db, candidate, active_session.session_id, req)
    assert res1.event_id == res2.event_id

    # Verify only 1 record exists in DB
    events = (
        db.query(ProctoringEvent)
        .filter(ProctoringEvent.session_id == active_session.session_id)
        .all()
    )
    assert len(events) == 1


def test_get_session_proctoring_summary_decoupled_from_technical_scores(db, candidate, active_session):
    # Add a normal event and a warning event
    e1 = ProctoringEventCreateRequest(event_type="fullscreen_enter")
    record_proctoring_event(db, candidate, active_session.session_id, e1)

    e2 = ProctoringEventCreateRequest(event_type="window_blur")
    record_proctoring_event(db, candidate, active_session.session_id, e2)

    summary = get_session_proctoring_summary(db, candidate, active_session.session_id)
    assert summary.session_id == active_session.session_id
    assert summary.total_events == 2
    assert summary.warning_count == 1
    assert "Ambiguous Interruptions" in summary.policy_outcome or "Verified Normal" in summary.policy_outcome
    assert "Technical evaluation is kept strictly independent" in summary.disclaimer


def test_end_interview_session_lifecycle(db, candidate, active_session):
    # Session is active initially
    assert active_session.status == "active"
    assert active_session.completed_at is None

    # Explicitly end session early
    res = end_interview_session(db, candidate, active_session.session_id)
    assert res.status == "ended_early"
    assert res.completed_at is not None

    # Refresh from db
    db.refresh(active_session)
    assert active_session.status == "ended_early"
    assert active_session.completed_at is not None


def test_api_proctoring_endpoints(candidate, active_session):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.dependencies import get_current_user

    app.dependency_overrides[get_current_user] = lambda: candidate
    client = TestClient(app)
    try:
        # POST proctoring event
        post_resp = client.post(
            f"/ai/career/interview/session/{active_session.session_id}/proctoring/events",
            json={"event_type": "visibility_hidden", "duration_ms": 500, "metadata": {"tab": "switched"}},
        )
        assert post_resp.status_code == 200
        event_data = post_resp.json()
        assert event_data["event_type"] == "visibility_hidden"
        assert event_data["severity"] == "warning"

        # GET proctoring summary
        summary_resp = client.get(
            f"/ai/career/interview/session/{active_session.session_id}/proctoring/summary"
        )
        assert summary_resp.status_code == 200
        summary_data = summary_resp.json()
        assert summary_data["session_id"] == active_session.session_id
        assert summary_data["warning_count"] >= 1
        assert "Ambiguous Interruptions" in summary_data["policy_outcome"] or "Verified Normal" in summary_data["policy_outcome"]

        # POST end session early
        end_resp = client.post(
            f"/ai/career/interview/session/{active_session.session_id}/end"
        )
        assert end_resp.status_code == 200
        assert end_resp.json()["status"] == "ended_early"
    finally:
        app.dependency_overrides.clear()

