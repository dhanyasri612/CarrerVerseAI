from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ResumeSkillAI(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    evidence: Optional[str] = Field(...)
    source_section: str = Field(...)
    confidence: Literal["High", "Medium", "Low", "Unverified", "Self-reported"] = Field(...)


class ResumeEducationAI(BaseModel):
    model_config = ConfigDict(extra="forbid")

    degree: Optional[str] = Field(...)
    institution: Optional[str] = Field(...)
    field: Optional[str] = Field(...)
    graduation_year: Optional[str] = Field(...)
    evidence: Optional[str] = Field(...)


class ResumeExperienceAI(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_title: Optional[str] = Field(...)
    company: Optional[str] = Field(...)
    duration: Optional[str] = Field(...)
    responsibilities: List[str] = Field(...)
    technologies: List[str] = Field(...)
    evidence: Optional[str] = Field(...)


class ResumeProjectAI(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(...)
    description: Optional[str] = Field(...)
    technologies: List[str] = Field(...)
    evidence: Optional[str] = Field(...)


class ResumeCertificationAI(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(...)
    issuer: Optional[str] = Field(...)
    evidence: Optional[str] = Field(...)


class ResumeAchievementAI(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: Optional[str] = Field(...)
    evidence: Optional[str] = Field(...)


class ResumeAIAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: Optional[str] = Field(...)
    skills: List[ResumeSkillAI] = Field(...)
    education: List[ResumeEducationAI] = Field(...)
    experience: List[ResumeExperienceAI] = Field(...)
    projects: List[ResumeProjectAI] = Field(...)
    certifications: List[ResumeCertificationAI] = Field(...)
    achievements: List[ResumeAchievementAI] = Field(...)
