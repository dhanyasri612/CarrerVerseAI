from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class RoadmapStep(BaseModel):
    step: int
    skill: str
    description: str

class CareerRoadmapResponse(BaseModel):
    resume_id: int
    job_id: int
    current_skills: List[str]
    missing_skills: List[str]
    roadmap: List[RoadmapStep]

class ResourceItem(BaseModel):
    name: str
    url: Optional[str] = None

class MilestoneResponse(BaseModel):
    id: Optional[int] = None
    stage: int
    title: str
    category: Optional[str] = None
    description: Optional[str] = None
    why_recommended: Optional[str] = None
    prerequisites: List[str] = []
    estimated_effort: Optional[str] = None
    skills: List[str] = []
    practical_project: Optional[str] = None
    completion_criteria: List[str] = []
    learning_resources: List[Dict[str, Any]] = []
    status: str = "upcoming"
    progress_pct: int = 0
    completed_at: Optional[str] = None

class TrendSignalResponse(BaseModel):
    id: str
    technology: str
    target_roles: List[str] = []
    trend_status: str
    why_it_matters: str
    evidence_summary: str
    source_name: str
    source_url: str
    publication_date: str
    source_type: str
    reliability: str
    impact_level: str
    student_status: str
    gap_severity: str
    prerequisites_met: List[str] = []
    prerequisites_missing: List[str] = []
    recommended_action: str

class RecommendationResponse(BaseModel):
    id: int
    title: str
    why_suggested: str
    proposed_action: Optional[str] = None
    evidence_summary: Optional[str] = None
    evidence_source: Optional[str] = None
    evidence_url: Optional[str] = None
    evidence_date: Optional[str] = None
    suggested_milestone_data: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

class ChangeLogResponse(BaseModel):
    id: int
    action_type: str
    title: str
    why_changed: str
    proposed_action: Optional[str] = None
    evidence_summary: Optional[str] = None
    evidence_source: Optional[str] = None
    evidence_url: Optional[str] = None
    evidence_date: Optional[str] = None
    status: str
    created_at: Optional[str] = None
    resolved_at: Optional[str] = None

class PersonalizedRoadmapResponse(BaseModel):
    roadmap_id: int
    target_role: str
    readiness_score: int
    current_version: int
    total_milestones: int
    completed_milestones: int
    last_reviewed_at: Optional[str] = None
    next_milestone: Optional[MilestoneResponse] = None
    verified_skills: List[str] = []
    key_skill_gaps: List[str] = []
    milestones: List[MilestoneResponse] = []
    roadmap: List[MilestoneResponse] = []
    pending_recommendations: List[RecommendationResponse] = []
    change_history: List[ChangeLogResponse] = []
    trend_signals: List[TrendSignalResponse] = []
    version_summary: Optional[str] = None

class RoadmapGenerateRequest(BaseModel):
    target_role: Optional[str] = None
    force_refresh: bool = False