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
        response_schema: dict[str, Any] | None = None,
        max_completion_tokens: int | None = None,
    ) -> ProviderResponse:
        """Generate a response using a structured output schema or raw text."""
        ...

    def generate_text(
        self,
        *,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.2,
        max_completion_tokens: int | None = None,
    ) -> ProviderResponse:
        """Generate free-form text response."""
        ...