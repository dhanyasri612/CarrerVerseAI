from pydantic import BaseModel
from typing import List

class ResumeImprovementResponse(BaseModel):
    resume_id: int
    job_id: int
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    