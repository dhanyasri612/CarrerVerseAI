from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ProviderResponse:
    content: str
    model: str


class ModelProvider(Protocol):
    def generate(
        self,
        *,
        system_prompt: str,
        user_message: str,
        response_schema: dict[str, Any],
        max_completion_tokens: int | None = None,
    ) -> ProviderResponse:
        """Generate a response using a structured output schema."""