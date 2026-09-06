from pydantic import BaseModel
from typing import List

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