"""
Ollama Local LLM Provider for CareerVerse AI.

Provides local OpenAI-compatible LLM execution via Ollama server (e.g. http://localhost:11434/v1).
Implements the ModelProvider protocol for zero architectural disruption.
"""

import logging
from typing import Any
import httpx

from app.ai.errors import (
    AIConfigurationError,
    AIProviderError,
    AIProviderTimeoutError,
)
from app.ai.providers.base import ProviderResponse
from app.core.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MAX_COMPLETION_TOKENS,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
)

logger = logging.getLogger("careerverse.ai.providers.ollama")


class OllamaProvider:
    """
    Ollama Local LLM Provider adhering to the ModelProvider protocol.
    Communicates via Ollama's OpenAI-compatible HTTP endpoint.
    """

    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_MODEL,
        timeout: float = OLLAMA_TIMEOUT,
    ):
        if not base_url:
            raise AIConfigurationError("OLLAMA_BASE_URL is not configured.")
        if not model:
            raise AIConfigurationError("OLLAMA_MODEL is not configured.")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.endpoint = f"{self.base_url}/chat/completions"

    def generate(
        self,
        *,
        system_prompt: str,
        user_message: str,
        response_schema: dict[str, Any] | None = None,
        max_completion_tokens: int | None = None,
    ) -> ProviderResponse:
        """
        Generates structured or text completion using Ollama.
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.2,
            "max_tokens": max_completion_tokens or OLLAMA_MAX_COMPLETION_TOKENS,
        }
        if response_schema is not None:
            payload["response_format"] = {"type": "json_object"}

        return self._send_request(payload)

    def generate_text(
        self,
        *,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.2,
        max_completion_tokens: int | None = None,
    ) -> ProviderResponse:
        """
        Generates natural language response without JSON schema constraints.
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": temperature,
            "max_tokens": max_completion_tokens or OLLAMA_MAX_COMPLETION_TOKENS,
        }

        return self._send_request(payload)

    def _send_request(self, payload: dict[str, Any]) -> ProviderResponse:
        """Sends synchronous POST request to Ollama with strict error handling."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(self.endpoint, json=payload)
                if response.status_code == 404:
                    # Model not found or wrong path
                    error_msg = response.text
                    if "not found" in error_msg.lower():
                        raise AIProviderError(
                            f"Ollama model '{self.model}' not found on {self.base_url}. "
                            f"Run `ollama pull {self.model}` to download it."
                        )
                    raise AIProviderError(
                        f"Ollama endpoint {self.endpoint} not found (HTTP 404): {error_msg}"
                    )
                response.raise_for_status()
                data = response.json()

            choices = data.get("choices", [])
            if not choices:
                raise AIProviderError(f"Ollama returned no choices for model '{self.model}'.")

            content = choices[0].get("message", {}).get("content")
            if not content:
                raise AIProviderError(f"Ollama returned empty response content for model '{self.model}'.")

            return ProviderResponse(
                content=content,
                model=data.get("model", self.model),
            )

        except (httpx.ConnectError, httpx.NetworkError, httpx.ConnectTimeout) as exc:
            logger.error("Ollama connection failed: %s", exc)
            raise AIProviderError(
                f"Ollama server is unavailable at {self.base_url}. Please ensure Ollama is running."
            ) from exc
        except (httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout) as exc:
            logger.error("Ollama request timed out: %s", exc)
            raise AIProviderTimeoutError(f"Ollama request timed out after {self.timeout}s.") from exc
        except httpx.HTTPStatusError as exc:
            logger.error("Ollama HTTP status error: %s", exc)
            raise AIProviderError(
                f"Ollama error (HTTP {exc.response.status_code}): {exc.response.text}"
            ) from exc
        except (AIProviderError, AIProviderTimeoutError, AIConfigurationError):
            raise
        except Exception as exc:
            logger.error("Unexpected error in Ollama generation: %s", exc)
            raise AIProviderError(f"Ollama generation failed: {exc}") from exc
