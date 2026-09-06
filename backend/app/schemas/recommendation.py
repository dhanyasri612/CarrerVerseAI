from pydantic import BaseModel
from typing import List

class JobRecommendation(BaseModel):
    job_id: int
    title: str
    company: str
    match_percentage: float
    matched_skills: List[str]
    missing_skills: List[str]
    