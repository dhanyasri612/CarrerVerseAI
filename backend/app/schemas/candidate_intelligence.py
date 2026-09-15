from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class SkillEvidenceItem(BaseModel):
    source: str = Field(..., description="Source where skill was discovered (resume, github, certification, leetcode, hackerrank, candidate_profile)")
    detail: str = Field(..., description="Contextual evidence details")
    weight: float = Field(..., ge=0.0, le=1.0, description="Reliability weight of this specific evidence")


class UnifiedSkill(BaseModel):
    name: str = Field(..., description="Canonical normalized skill name")
    category: str = Field(..., description="Taxonomy category")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Evidence-based confidence metric (0.0 - 1.0)")
    sources: List[str] = Field(default_factory=list, description="Unique source names supporting this skill")
    supporting_sources_count: int = Field(0, description="Number of distinct independent sources")
    evidence: List[SkillEvidenceItem] = Field(default_factory=list, description="Audit evidence items")


class SkillsByCategory(BaseModel):
    category: str
    skills: List[UnifiedSkill] = Field(default_factory=list)


class UserProfileSummary(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    graduation_year: Optional[int] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    summary: Optional[str] = None
    created_at: Optional[datetime] = None


class EducationSummary(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None
    raw_text: Optional[str] = None


class ExperienceSummary(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    raw_text: Optional[str] = None


class ProjectSummary(BaseModel):
    title: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    source: str = Field("candidate_profile", description="Source: github, resume, candidate_profile")
    url: Optional[str] = None
    stars: Optional[int] = None


class CertificationsSummary(BaseModel):
    total_certifications: int = 0
    verified_count: int = 0
    pending_count: int = 0
    items: List[Dict[str, Any]] = Field(default_factory=list)


class GitHubSummary(BaseModel):
    connected: bool = False
    username: Optional[str] = None
    profile_url: Optional[str] = None
    total_repositories: int = 0
    total_stars: int = 0
    total_forks: int = 0
    languages: Dict[str, Any] = Field(default_factory=dict)
    top_topics: List[str] = Field(default_factory=list)
    analyzed_repositories_count: int = 0


class LinkedInSummary(BaseModel):
    connected: bool = False
    name: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    profile_picture: Optional[str] = None
    locale: Optional[str] = None


class LeetCodeSummary(BaseModel):
    connected: bool = False
    username: Optional[str] = None
    profile_url: Optional[str] = None
    ranking: Optional[int] = None
    reputation: Optional[int] = None
    total_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    acceptance_rate: Optional[float] = None
    contest_rating: Optional[float] = None
    badges_count: int = 0
    languages: List[Dict[str, Any]] = Field(default_factory=list)


class HackerRankSummary(BaseModel):
    connected: bool = False
    username: Optional[str] = None
    profile_url: Optional[str] = None
    display_name: Optional[str] = None
    country: Optional[str] = None
    school: Optional[str] = None
    total_solved: int = 0
    badges_count: int = 0
    certificates_count: int = 0
    badges: List[Dict[str, Any]] = Field(default_factory=list)


class ResumeSummary(BaseModel):
    uploaded: bool = False
    count: int = 0
    latest_filename: Optional[str] = None
    parsed_status: bool = False


class ProfileCompleteness(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Overall profile completeness score (0-100)")
    section_scores: Dict[str, int] = Field(default_factory=dict, description="Completeness score per section")
    missing_sections: List[str] = Field(default_factory=list, description="List of uncompleted profile sections")
    actionable_recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations to improve profile")
    data_quality_warnings: List[str] = Field(default_factory=list, description="Potential data quality or verification warnings")


class UnifiedProfileResponse(BaseModel):
    user_profile: UserProfileSummary
    education: List[EducationSummary] = Field(default_factory=list)
    experience: List[ExperienceSummary] = Field(default_factory=list)
    projects: List[ProjectSummary] = Field(default_factory=list)
    resume_summary: ResumeSummary
    github_summary: GitHubSummary
    linkedin_summary: LinkedInSummary
    leetcode_summary: LeetCodeSummary
    hackerrank_summary: HackerRankSummary
    certifications_summary: CertificationsSummary
    unified_skills: List[UnifiedSkill] = Field(default_factory=list)
    skills_by_category: List[SkillsByCategory] = Field(default_factory=list)
    completeness: ProfileCompleteness

    model_config = ConfigDict(from_attributes=True)
