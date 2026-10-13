from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CandidateGraphNode(BaseModel):
    """Pydantic model representing the Candidate root node in Neo4j."""
    model_config = ConfigDict(extra="ignore")

    candidate_id: int
    name: str
    email: str
    phone: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    graduation_year: Optional[int] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    completeness_score: Optional[int] = 0
    total_skills: Optional[int] = 0
    last_synced_at: Optional[Any] = None


class CandidateSkillItem(BaseModel):
    """Pydantic model for Skill node linked via HAS_SKILL relationship."""
    model_config = ConfigDict(extra="ignore")

    name: str
    category: str = "General"
    confidence_score: float = 0.5
    supporting_sources_count: int = 1
    sources: List[str] = Field(default_factory=list)


class CandidateProjectItem(BaseModel):
    """Pydantic model for Project node linked via HAS_PROJECT and USES_TECHNOLOGY."""
    model_config = ConfigDict(extra="ignore")

    project_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    source: Optional[str] = "candidate_profile"
    url: Optional[str] = None
    stars: Optional[int] = 0
    technologies: List[str] = Field(default_factory=list)


class CandidateCertificationItem(BaseModel):
    """Pydantic model for Certification node linked via HAS_CERTIFICATION."""
    model_config = ConfigDict(extra="ignore")

    certification_id: Optional[str] = None
    name: str
    issuing_organization: Optional[str] = "Unknown"
    issue_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    source: Optional[str] = "MANUAL"
    verification_status: Optional[str] = "UNVERIFIED"
    confidence_score: Optional[float] = 0.5


class CandidateEducationItem(BaseModel):
    """Pydantic model for Education node linked via HAS_EDUCATION."""
    model_config = ConfigDict(extra="ignore")

    education_id: Optional[str] = None
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None


class CandidateExperienceItem(BaseModel):
    """Pydantic model for Experience node linked via HAS_EXPERIENCE."""
    model_config = ConfigDict(extra="ignore")

    experience_id: Optional[str] = None
    company: str
    role: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)


class CandidateSubgraphResponse(BaseModel):
    """Container for the comprehensive structured Knowledge Graph subgraph of a candidate."""
    model_config = ConfigDict(extra="ignore")

    candidate: CandidateGraphNode
    skills: List[CandidateSkillItem] = Field(default_factory=list)
    projects: List[CandidateProjectItem] = Field(default_factory=list)
    certifications: List[CandidateCertificationItem] = Field(default_factory=list)
    education: List[CandidateEducationItem] = Field(default_factory=list)
    experience: List[CandidateExperienceItem] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
