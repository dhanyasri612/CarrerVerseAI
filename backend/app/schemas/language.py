"""
Pydantic schemas for Multilingual AI Support.

Defines typed schemas for:
- Language detection results
- Language preferences & overrides
- Multilingual response metadata and audit metrics
"""

from typing import Optional
from pydantic import BaseModel, Field


class LanguageDetectionResult(BaseModel):
    """
    Structured outcome of language detection on a query.
    """
    language_code: str = Field(..., description="ISO 639-1 language code (e.g., 'en', 'ta', 'hi')")
    language_name: str = Field(..., description="Human-readable language name (e.g., 'English', 'Tamil', 'Hindi')")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the detection")
    detection_method: str = Field(..., description="Method used for detection (e.g. 'unicode_script', 'lexical_heuristic', 'statistical', 'explicit')")
    is_supported: bool = Field(..., description="Whether the detected language is supported by the CareerVerse AI pipeline")


class LanguagePreference(BaseModel):
    """
    Optional explicit language preference provided in request.
    """
    language_code: Optional[str] = Field(None, description="Explicit target language code override (e.g., 'ta', 'hi', 'en')")


class MultilingualResponseMetadata(BaseModel):
    """
    Metadata attached to responses documenting multilingual processing details.
    """
    detected_language: str = Field(..., description="Detected query language code")
    language_name: str = Field(..., description="Detected language name")
    response_language: str = Field(..., description="Language code used for final generated response")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")
    detection_method: str = Field(..., description="Detection method utilized")
    original_query: str = Field(..., description="Original, unmodified user query")
    normalized_query: Optional[str] = Field(None, description="Canonical normalized query used for internal routing/retrieval")
    is_translated_response: bool = Field(False, description="Whether the response was generated in a non-default language")
