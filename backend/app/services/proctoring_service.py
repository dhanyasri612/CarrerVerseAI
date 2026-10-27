import logging
from datetime import datetime, timedelta
import uuid
from typing import Dict, Any, List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.interview_session import InterviewSession
from app.models.proctoring_event import ProctoringEvent
from app.schemas.proctoring import (
    ProctoringEventCreateRequest,
    ProctoringEventResponse,
    ProctoringSummaryResponse,
    VALID_PROCTORING_EVENT_TYPES,
)

logger = logging.getLogger(__name__)


def _get_owned_session(db: Session, user: User, session_id: str) -> InterviewSession:
    sess = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.session_id == session_id,
            InterviewSession.candidate_id == user.id,
        )
        .first()
    )
    if not sess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found or unauthorized access",
        )
    return sess


def record_proctoring_event(
    db: Session,
    current_user: User,
    session_id: str,
    req: ProctoringEventCreateRequest,
) -> ProctoringEventResponse:
    """
    Records a browser or media telemetry event with server-authoritative timestamps,
    candidate isolation, and duplicate event flood prevention.
    """
    session = _get_owned_session(db, current_user, session_id)

    event_type = req.event_type.strip().lower()
    if event_type not in VALID_PROCTORING_EVENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid proctoring event type: {event_type}",
        )

    now = datetime.utcnow()

    # Flood prevention: check if an identical event was recorded in the last 500ms
    recent_dup = (
        db.query(ProctoringEvent)
        .filter(
            ProctoringEvent.session_id == session_id,
            ProctoringEvent.event_type == event_type,
            ProctoringEvent.created_at >= now - timedelta(milliseconds=500),
        )
        .first()
    )
    if recent_dup:
        return ProctoringEventResponse.model_validate(recent_dup)

    # Classify severity and action neutrally
    severity = "info"
    action = "logged"
    if event_type in {"visibility_hidden", "window_blur", "fullscreen_exit"}:
        severity = "warning"
        action = "warning_issued"
    elif event_type in {"camera_interrupted", "mic_interrupted", "connection_offline"}:
        severity = "warning"
        action = "reconnect_prompt"
    elif event_type in {"timing_anomaly"}:
        severity = "info"
        action = "logged"

    meta: Dict[str, Any] = req.metadata or {}
    if req.duration_ms is not None:
        meta["duration_ms"] = req.duration_ms

    event_record = ProctoringEvent(
        event_id=str(uuid.uuid4()),
        session_id=session.session_id,
        candidate_id=current_user.id,
        event_type=event_type,
        severity=severity,
        action_taken=action,
        metadata_json=meta,
        created_at=now,
        reviewed=False,
    )

    db.add(event_record)
    db.commit()
    db.refresh(event_record)

    return ProctoringEventResponse.model_validate(event_record)


def get_session_proctoring_summary(
    db: Session,
    current_user: User,
    session_id: str,
) -> ProctoringSummaryResponse:
    """
    Computes a comprehensive proctoring summary based on recorded integrity events.
    Strictly decoupled from technical scoring rubric.
    """
    session = _get_owned_session(db, current_user, session_id)

    events = (
        db.query(ProctoringEvent)
        .filter(ProctoringEvent.session_id == session_id)
        .order_by(ProctoringEvent.created_at.asc())
        .all()
    )

    timeline = [ProctoringEventResponse.model_validate(e) for e in events]
    warning_count = sum(1 for e in events if e.severity == "warning")
    interruption_count = sum(
        1 for e in events if e.event_type in {"camera_interrupted", "mic_interrupted", "connection_offline", "screenshare_stopped"}
    )

    if warning_count == 0:
        outcome = "Verified Normal"
    elif warning_count <= 3:
        outcome = "Minor Ambiguous Interruptions Noted"
    else:
        outcome = "Multiple Browser Events Recorded (Review Recommended)"

    return ProctoringSummaryResponse(
        session_id=session.session_id,
        candidate_id=current_user.id,
        unproctored=False,
        total_events=len(events),
        warning_count=warning_count,
        interruption_count=interruption_count,
        timeline=timeline,
        policy_outcome=outcome,
        review_status="Automated Check Complete",
    )
