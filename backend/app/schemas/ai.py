from pydantic import BaseModel, Field

from app.ai.parser import TestAIResponse


class AITestRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class AITestResponse(TestAIResponse):
    model: str