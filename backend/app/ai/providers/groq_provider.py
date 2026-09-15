from typing import Any

from groq import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    Groq,
)

from app.ai.errors import (
    AIConfigurationError,
    AIProviderAuthenticationError,
    AIProviderError,
    AIProviderTimeoutError,
)
from app.ai.providers.base import ProviderResponse
from app.core.config import GROQ_API_KEY, GROQ_MODEL


class GroqProvider:
    def __init__(self, api_key: str | None = GROQ_API_KEY, model: str = GROQ_MODEL):
        if not api_key:
            raise AIConfigurationError("GROQ_API_KEY is not configured")
        self.model = model
        self.client = Groq(api_key=api_key)

    def generate(
        self,
        *,
        system_prompt: str,
        user_message: str,
        response_schema: dict[str, Any],
    ) -> ProviderResponse:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": response_schema,
                },
            )
        except AuthenticationError as exc:
            raise AIProviderAuthenticationError("Groq authentication failed") from exc
        except (APITimeoutError, APIConnectionError) as exc:
            raise AIProviderTimeoutError("Groq request timed out or could not connect") from exc
        except APIStatusError as exc:
            raise AIProviderError("Groq request failed") from exc
        except Exception as exc:
            raise AIProviderError("Unexpected Groq provider failure") from exc

        content = completion.choices[0].message.content if completion.choices else None
        if not content:
            raise AIProviderError("Groq returned an empty response")

        return ProviderResponse(content=content, model=completion.model or self.model)