from typing import Any

from app.ai.parser import TestAIResponse, parse_test_response
from app.ai.prompts import PromptManager
from app.ai.providers.base import ModelProvider, ProviderResponse
from app.ai.providers.groq_provider import GroqProvider


class AIService:
    def __init__(self, provider: ModelProvider | None = None):
        self.provider = provider

    def _get_provider(self) -> ModelProvider:
        if self.provider is None:
            self.provider = GroqProvider()
        return self.provider

    def generate(
        self,
        *,
        message: str,
        system_prompt: str,
        response_schema: dict[str, Any],
    ) -> ProviderResponse:
        return self._get_provider().generate(
            system_prompt=system_prompt,
            user_message=message,
            response_schema=response_schema,
        )

    def test(self, message: str) -> tuple[TestAIResponse, str]:
        response = self.generate(
            message=message,
            system_prompt=PromptManager.test_system_prompt(),
            response_schema={
                "name": "ai_test_response",
                "strict": True,
                "schema": TestAIResponse.model_json_schema(),
            },
        )
        return parse_test_response(response.content), response.model


ai_service = AIService()