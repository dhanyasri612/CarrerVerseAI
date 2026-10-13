from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SkillEvidenceRecord(BaseModel):
    concept_name: str
    category: str = "General"
    evidence_source: str = Field(..., description="'resume' | 'github' | 'leetcode' | 'hackerrank' | 'certification' | 'assessment' | 'inferred'")
    evidence_identifier: Optional[str] = None
    evidence_description: str
    last_verified_at: Optional[str] = None
    evidence_type: str = Field("inferred", description="'explicitly_declared' | 'observed' | 'assessed' | 'inferred'")
    confidence_score: float = Field(0.5, ge=0.0, le=1.0)
    prerequisites: List[str] = Field(default_factory=list)
    status: str = Field("not_started", description="'unknown' | 'not_started' | 'learning' | 'needs_revision' | 'demonstrated_understanding' | 'mastered'")
    is_knowledge_gap: bool = False
    why_matters_for_role: Optional[str] = None
    learning_priority: str = Field("medium", description="'high' | 'medium' | 'low'")
    estimated_effort_hours: Optional[int] = None


class LearnerKnowledgeProfile(BaseModel):
    candidate_id: int
    candidate_name: str
    target_role: str
    career_goals: List[str] = Field(default_factory=list)
    skills_inventory: Dict[str, SkillEvidenceRecord] = Field(default_factory=dict)
    verified_projects: List[Dict[str, Any]] = Field(default_factory=list)
    target_role_required_skills: List[str] = Field(default_factory=list)
    knowledge_gaps: List[str] = Field(default_factory=list)
    demonstrated_strengths: List[str] = Field(default_factory=list)
    recommended_learning_order: List[str] = Field(default_factory=list)
    last_updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class TeachingResourceItem(BaseModel):
    id: str
    title: str
    canonical_url: Optional[str] = None
    file_reference: Optional[str] = None
    resource_type: str = Field(..., description="'official_doc' | 'tutorial' | 'candidate_project' | 'exercise' | 'prior_feedback'")
    concepts_covered: List[str] = Field(default_factory=list)
    difficulty_level: str = "Medium"
    source: str
    retrieval_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    excerpt: str
    relevance_rationale: str
    is_verified: bool = True


class ConceptMapNode(BaseModel):
    id: str
    label: str
    category: str
    status: str  # "mastered" | "demonstrated" | "learning" | "gap" | "not_started"
    difficulty: str = "Medium"
    confidence_score: float = 0.5
    is_current: bool = False
    has_project_evidence: bool = False
    project_name: Optional[str] = None


class ConceptMapEdge(BaseModel):
    source: str
    target: str
    relationship: str  # "REQUIRES" | "RELATED_TO" | "DEMONSTRATES" | "TAUGHT_IN"
    label: str


class ConceptMapResponse(BaseModel):
    candidate_id: int
    current_concept_id: Optional[str] = None
    nodes: List[ConceptMapNode]
    edges: List[ConceptMapEdge]
    total_nodes: int
    total_edges: int
