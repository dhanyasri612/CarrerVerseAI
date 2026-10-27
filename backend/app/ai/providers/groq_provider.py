import time
from typing import Any
import logging

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
    AIProviderRateLimitError,
    AIProviderTimeoutError,
)
from app.ai.providers.base import ProviderResponse
from app.core.config import GROQ_API_KEY, GROQ_MAX_COMPLETION_TOKENS, GROQ_MODEL

logger = logging.getLogger("careerverse.ai")


class GroqProvider:
    def __init__(self, api_key: str | None = GROQ_API_KEY, model: str = GROQ_MODEL):
        if not api_key:
            raise AIConfigurationError("GROQ_API_KEY is not configured")
        self.model = model
        self.client = Groq(api_key=api_key, max_retries=0)

    def _get_candidate_models(self) -> list[str]:
        models = [self.model, "openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]
        seen = set()
        deduped = []
        for m in models:
            if m and m not in seen:
                seen.add(m)
                deduped.append(m)
        return deduped

    def generate(
        self,
        *,
        system_prompt: str,
        user_message: str,
        response_schema: dict[str, Any] | None = None,
        max_completion_tokens: int | None = None,
    ) -> ProviderResponse:
        candidate_models = self._get_candidate_models()
        max_attempts = 2
        last_status_code = None
        last_timeout_exc: Exception | None = None
        last_error: Exception | None = None

        for attempt in range(max_attempts):
            for candidate in candidate_models:
                try:
                    kwargs: dict[str, Any] = {
                        "model": candidate,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                        "max_completion_tokens": max_completion_tokens or GROQ_MAX_COMPLETION_TOKENS,
                    }
                    if response_schema is not None:
                        if isinstance(response_schema, dict) and "name" in response_schema and "schema" in response_schema:
                            kwargs["response_format"] = {
                                "type": "json_schema",
                                "json_schema": response_schema,
                            }
                        else:
                            kwargs["response_format"] = {
                                "type": "json_object",
                            }

                    completion = self.client.chat.completions.create(**kwargs)
                    content = completion.choices[0].message.content if completion.choices else None
                    if content:
                        return ProviderResponse(content=content, model=completion.model or candidate)
                except AuthenticationError as exc:
                    logger.error("Groq authentication failed: %s", exc)
                    raise AIProviderAuthenticationError("Groq authentication failed") from exc
                except APITimeoutError as exc:
                    last_timeout_exc = exc
                    last_error = exc
                    logger.warning("Groq timeout on model %s: %s", candidate, exc)
                except APIConnectionError as exc:
                    last_error = exc
                    logger.warning("Groq connection error on model %s: %s", candidate, exc)
                except APIStatusError as exc:
                    last_status_code = exc.status_code
                    last_error = exc
                    if exc.status_code in (400, 429, 413, 503) or "json_validate_failed" in str(exc):
                        logger.warning("Groq %s on model %s, trying next candidate...", exc.status_code, candidate)
                        continue
                    logger.warning("Groq status error on model %s (%s): %s", candidate, exc.status_code, exc.message)
                except Exception as exc:
                    last_error = exc
                    logger.warning("Unexpected error on model %s: %s", candidate, exc)

            if attempt < max_attempts - 1:
                sleep_secs = 5 * (attempt + 1)
                logger.info("All Groq candidate models busy/rate-limited. Waiting %d seconds before retry...", sleep_secs)
                time.sleep(sleep_secs)

        if last_status_code in (429, 413):
            raise AIProviderRateLimitError("Groq provider rate limit reached (HTTP 429 / TPM quota).")
        if isinstance(last_error, APITimeoutError) or (last_timeout_exc is not None and last_status_code is None):
            raise AIProviderTimeoutError("Groq request timed out after multiple retries.") from (last_timeout_exc or last_error)
        raise AIProviderError("All Groq model candidates failed or rate-limited after multiple retries.")

    def generate_text(
        self,
        *,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.2,
        max_completion_tokens: int | None = None,
    ) -> ProviderResponse:
        """Generates natural language response without JSON schema constraints."""
        candidate_models = self._get_candidate_models()
        max_attempts = 2
        last_status_code = None
        last_timeout_exc: Exception | None = None
        last_error: Exception | None = None

        for attempt in range(max_attempts):
            for candidate in candidate_models:
                try:
                    completion = self.client.chat.completions.create(
                        model=candidate,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                        temperature=temperature,
                        max_completion_tokens=max_completion_tokens or GROQ_MAX_COMPLETION_TOKENS,
                    )
                    content = completion.choices[0].message.content if completion.choices else None
                    if content:
                        return ProviderResponse(content=content, model=completion.model or candidate)
                except AuthenticationError as exc:
                    logger.error("Groq authentication failed: %s", exc)
                    raise AIProviderAuthenticationError("Groq authentication failed") from exc
                except APITimeoutError as exc:
                    last_timeout_exc = exc
                    last_error = exc
                    logger.warning("Groq timeout on model %s: %s", candidate, exc)
                except APIConnectionError as exc:
                    last_error = exc
                    logger.warning("Groq connection error on model %s: %s", candidate, exc)
                except APIStatusError as exc:
                    last_status_code = exc.status_code
                    last_error = exc
                    if exc.status_code in (429, 413, 503):
                        logger.warning("Groq %s on model %s, trying next candidate...", exc.status_code, candidate)
                        continue
                    logger.warning("Groq status error on model %s (%s): %s", candidate, exc.status_code, exc.message)
                except Exception as exc:
                    last_error = exc
                    logger.warning("Unexpected error on model %s: %s", candidate, exc)

            if attempt < max_attempts - 1:
                sleep_secs = 5 * (attempt + 1)
                logger.info("All Groq candidate models busy/rate-limited. Waiting %d seconds before retry...", sleep_secs)
                time.sleep(sleep_secs)

        if last_status_code in (429, 413):
            raise AIProviderRateLimitError("Groq provider rate limit reached (HTTP 429 / TPM quota).")
        if isinstance(last_error, APITimeoutError) or (last_timeout_exc is not None and last_status_code is None):
            raise AIProviderTimeoutError("Groq request timed out after multiple retries.") from (last_timeout_exc or last_error)
        raise AIProviderError("All Groq model candidates failed or rate-limited after multiple retries.")