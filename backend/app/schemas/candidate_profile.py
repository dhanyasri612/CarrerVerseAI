from typing import List, Optional , Dict , Any
from pydantic import BaseModel

class CandidateProfileResponse(BaseModel):
    id:int
    user_id:int
    summary: Optional[str] = None
    
    skills: Optional[List[str]] = None
    education: Optional[List[str]] = None
    experience: Optional[List[str]] = None
    projects: Optional[List[str]] = None
    certifications: Optional[List[str]] = None

    github_data: Optional[Dict[str, Any]] = None
    coding_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True