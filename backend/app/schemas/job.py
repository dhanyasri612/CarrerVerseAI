from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    required_skills: Optional[List[str]] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    experience: Optional[str] = None


class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    description: str
    required_skills: Optional[List[str]] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    experience: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    experience: Optional[str] = None