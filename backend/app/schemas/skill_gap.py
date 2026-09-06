from pydantic import BaseModel
from typing import List

class SkillGapResponse(BaseModel):
    resume_id: int
    job_id: int
    matched_skills: List[str]
    missing_skills: List[str]
    match_percentage: float