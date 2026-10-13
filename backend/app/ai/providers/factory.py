"""
Provider Factory for CareerVerse AI.

Provides unified instantiation of ModelProvider (GroqProvider or OllamaProvider)
based on the configured AI_PROVIDER environment setting.
"""

import os
import logging
from typing import Optional

from app.ai.providers.base import ModelProvider
from app.ai.providers.groq_provider import GroqProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.core.config import AI_PROVIDER

logger = logging.getLogger("careerverse.ai.providers")


def get_model_provider(provider_name: Optional[str] = None) -> ModelProvider:
    """
    Returns the configured ModelProvider instance.
    Defaults to AI_PROVIDER setting ('groq' or 'ollama').
    """
    selected = (provider_name or os.getenv("AI_PROVIDER") or AI_PROVIDER or "groq").strip().lower()

    if selected == "ollama":
        try:
            logger.info("Using OllamaProvider (Local LLM)")
            return OllamaProvider()
        except Exception as exc:
            logger.warning("Failed to initialize OllamaProvider: %s. Falling back to GroqProvider.", exc)
            return GroqProvider()

    logger.info("Using GroqProvider (Cloud LLM)")
    return GroqProvider()
