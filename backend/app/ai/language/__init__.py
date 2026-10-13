"""
Multilingual AI package for CareerVerse AI.
"""

from app.ai.language.detector import LanguageDetector, language_detector
from app.ai.language.normalizer import QueryNormalizer, query_normalizer
from app.ai.language.prompt_builder import LanguagePromptBuilder, language_prompt_builder

__all__ = [
    "LanguageDetector",
    "language_detector",
    "QueryNormalizer",
    "query_normalizer",
    "LanguagePromptBuilder",
    "language_prompt_builder",
]
