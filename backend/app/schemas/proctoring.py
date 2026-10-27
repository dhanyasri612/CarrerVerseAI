from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


VALID_PROCTORING_EVENT_TYPES = {
    "visibility_hidden",
    "visibility_visible",
    "window_blur",
    "window_focus",
    "fullscreen_enter",
    "fullscreen_exit",
    "camera_interrupted",
    "camera_restored",
    "mic_interrupted",
    "mic_restored",
    "screenshare_started",
    "screenshare_stopped",
    "connection_offline",
    "connection_online",
    "timing_anomaly",
}


class ProctoringConsentRequest(BaseModel):
    camera_consent: bool = Field(True, description="Candidate consented to camera feed preview")
    mic_consent: bool = Field(True, description="Candidate consented to audio capture")
    screen_share_consent: bool = Field(False, description="Candidate consented to optional screen share")
    browser_monitoring_consent: bool = Field(True, description="Candidate consented to transparent tab/focus events")
    unproctored_mode: bool = Field(False, description="True if candidate opted for unproctored practice mode")


class ProctoringEventCreateRequest(BaseModel):
    event_type: str = Field(..., description="Browser or peripheral integrity event type")
    duration_ms: Optional[int] = Field(None, ge=0, description="Duration of interruption in milliseconds")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Neutral contextual details")


class ProctoringEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    session_id: str
    candidate_id: int
    event_type: str
    severity: str
    action_taken: str
    metadata_json: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime
    reviewed: bool = False
    reviewer_notes: Optional[str] = None


class ProctoringSummaryResponse(BaseModel):
    session_id: str
    candidate_id: int
    unproctored: bool = False
    total_events: int = 0
    warning_count: int = 0
    interruption_count: int = 0
    timeline: List[ProctoringEventResponse] = Field(default_factory=list)
    policy_outcome: str = "Verified Normal"
    review_status: str = "Automated Check Complete"
    disclaimer: str = (
        "Notice: Browser events (e.g. window blur or tab switching) are inherently ambiguous "
        "and do not constitute definitive evidence of misconduct. Technical evaluation is kept strictly independent."
    )
