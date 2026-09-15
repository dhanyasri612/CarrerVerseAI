import json

from pydantic import BaseModel, ConfigDict, ValidationError

from app.ai.errors import AIInvalidResponseError


class TestAIResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool
    message: str


def parse_test_response(content: str) -> TestAIResponse:
    try:
        return TestAIResponse.model_validate(json.loads(content))
    except (json.JSONDecodeError, ValidationError, TypeError) as exc:
        raise AIInvalidResponseError("Groq returned an invalid structured response") from exc