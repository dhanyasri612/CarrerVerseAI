from typing import Any

from app.ai.errors import AIInvalidResponseError
from app.ai.parser import TestAIResponse, parse_test_response
from app.ai.prompts import PromptManager
from app.ai.providers.base import ModelProvider, ProviderResponse
from app.ai.providers.groq_provider import GroqProvider
from app.schemas.resume_ai import ResumeAIAnalysis
from app.schemas.skill_gap_ai import SkillGapAnalysis


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
        max_completion_tokens: int | None = None,
    ) -> ProviderResponse:
        return self._get_provider().generate(
            system_prompt=system_prompt,
            user_message=message,
            response_schema=response_schema,
            max_completion_tokens=max_completion_tokens,
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

    def generate_resume_intelligence(self, *, resume_text: str) -> tuple[ResumeAIAnalysis, str]:
        response = self.generate(
            message=PromptManager.resume_intelligence_prompt(resume_text),
            system_prompt=PromptManager.resume_intelligence_system_prompt(),
            response_schema={
                "name": "resume_ai_analysis",
                "strict": True,
                "schema": ResumeAIAnalysis.model_json_schema(),
            },
        )
        return ResumeAIAnalysis.model_validate_json(response.content), response.model

    def generate_skill_gap_analysis(
        self,
        *,
        target_role: str,
        role_requirements: list[str],
        candidate_evidence: str,
    ) -> tuple[SkillGapAnalysis, str]:
        response = self.generate(
            message=PromptManager.skill_gap_prompt(
                target_role=target_role,
                role_requirements=role_requirements,
                candidate_evidence=candidate_evidence,
            ),
            system_prompt=PromptManager.skill_gap_system_prompt(),
            response_schema={
                "name": "skill_gap_analysis",
                "strict": True,
                "schema": SkillGapAnalysis.model_json_schema(),
            },
            max_completion_tokens=4096,
        )
        try:
            result = SkillGapAnalysis.model_validate_json(response.content)
        except Exception as exc:
            raise AIInvalidResponseError("Groq returned an invalid skill-gap response") from exc
        return result, response.model


ai_service = AIService()