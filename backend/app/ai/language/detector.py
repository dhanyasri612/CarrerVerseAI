"""
Deterministic and Statistical Language Detector for CareerVerse AI.

Detects query language using:
1. Explicit language override (if provided)
2. Deterministic Unicode Script Block frequency (Tamil: U+0B80–U+0BFF, Devanagari/Hindi: U+0900–U+097F)
3. Lexical pattern matching for Romanized Indic phrases (Tanglish, Hinglish)
4. Statistical n-gram fallback via langdetect
5. Default fallback to configured DEFAULT_LANGUAGE (English)
"""

import logging
import re
from typing import Dict, Optional, Tuple

try:
    from langdetect import DetectorFactory, detect_langs
    DetectorFactory.seed = 42
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

from app.core.config import DEFAULT_LANGUAGE, LANGUAGE_DETECTION_ENABLED, SUPPORTED_LANGUAGES
from app.schemas.language import LanguageDetectionResult

logger = logging.getLogger("careerverse.ai.language.detector")

LANGUAGE_METADATA_MAP: Dict[str, str] = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
}

LANGUAGE_NAME_TO_CODE: Dict[str, str] = {
    "english": "en",
    "tamil": "ta",
    "hindi": "hi",
    "french": "fr",
    "spanish": "es",
    "german": "de",
    "telugu": "te",
    "kannada": "kn",
    "malayalam": "ml",
    "bengali": "bn",
    "marathi": "mr",
    "gujarati": "gu",
}

# Romanized keyword sets for code-mixed / transliterated input
TAMIL_ROMANIZED_KEYWORDS = {
    "enakku", "velai", "skills", "thevai", "irukku", "illai", "venum",
    "eppadi", "theriyum", "mudiyum", "romba", "pannalam", "kudunga",
    "solunga", "solra", "theriyala", "kooda", "edhuvum", "enga", "epdi",
}

HINDI_ROMANIZED_KEYWORDS = {
    "mujhe", "kaise", "kya", "chahiye", "hoga", "karna", "karo", "kaun",
    "mera", "meri", "mere", "sikhe", "seekhna", "banne", "ke liye",
    "batao", "bataye", "chahiye", "kaunsa", "kaunsi", "karen", "tayari",
}

MALAYALAM_ROMANIZED_KEYWORDS = {
    "enikku", "chodhyam", "venam", "enthaanu", "enganeyanu", "ariyilla",
    "parayam", "cheyyam", "nokkaam", "cheyyanam", "aano", "aanu",
    "undennu", "illa", "pakshe", "enthu", "engane", "ippol", "ningal",
}


class LanguageDetector:
    """
    Deterministic & statistical language detection service.
    """

    def __init__(self, supported_languages: Optional[list] = None, default_language: str = DEFAULT_LANGUAGE):
        self.supported_languages = supported_languages or SUPPORTED_LANGUAGES
        self.default_language = default_language

    def normalize_language_code(self, raw_lang: Optional[str]) -> Optional[str]:
        """Maps full language names or codes to standard 2-letter ISO 639-1 code."""
        if not raw_lang:
            return None
        cleaned = raw_lang.strip().lower()
        if "-" in cleaned:
            cleaned = cleaned.split("-")[0]
        if cleaned in LANGUAGE_METADATA_MAP:
            return cleaned
        if cleaned in LANGUAGE_NAME_TO_CODE:
            return LANGUAGE_NAME_TO_CODE[cleaned]
        return cleaned

    def detect_unicode_script(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Calculates character frequency across distinct Unicode script blocks.

        Covered script ranges:
          Tamil:     U+0B80 – U+0BFF
          Devanagari (Hindi):  U+0900 – U+097F
          Telugu:    U+0C00 – U+0C7F
          Kannada:   U+0C80 – U+0CFF
          Malayalam: U+0D00 – U+0D7F
        """
        tamil_chars = 0
        devanagari_chars = 0
        telugu_chars = 0
        kannada_chars = 0
        malayalam_chars = 0
        latin_chars = 0
        total_letters = 0

        for char in text:
            code = ord(char)
            # Tamil: 0x0B80 - 0x0BFF
            if 0x0B80 <= code <= 0x0BFF:
                tamil_chars += 1
                total_letters += 1
            # Devanagari (Hindi): 0x0900 - 0x097F
            elif 0x0900 <= code <= 0x097F:
                devanagari_chars += 1
                total_letters += 1
            # Telugu: 0x0C00 - 0x0C7F
            elif 0x0C00 <= code <= 0x0C7F:
                telugu_chars += 1
                total_letters += 1
            # Kannada: 0x0C80 - 0x0CFF
            elif 0x0C80 <= code <= 0x0CFF:
                kannada_chars += 1
                total_letters += 1
            # Malayalam: 0x0D00 - 0x0D7F
            elif 0x0D00 <= code <= 0x0D7F:
                malayalam_chars += 1
                total_letters += 1
            elif char.isalpha() and ('a' <= char.lower() <= 'z'):
                latin_chars += 1
                total_letters += 1

        if total_letters == 0:
            return None

        tamil_ratio = tamil_chars / total_letters
        devanagari_ratio = devanagari_chars / total_letters
        telugu_ratio = telugu_chars / total_letters
        kannada_ratio = kannada_chars / total_letters
        malayalam_ratio = malayalam_chars / total_letters

        # If significant native script is present (even with embedded English words like 'FastAPI')
        if tamil_chars >= 2 and tamil_ratio >= 0.15:
            conf = min(0.99, max(0.85, tamil_ratio * 1.5))
            return "ta", conf

        if devanagari_chars >= 2 and devanagari_ratio >= 0.15:
            conf = min(0.99, max(0.85, devanagari_ratio * 1.5))
            return "hi", conf

        if telugu_chars >= 2 and telugu_ratio >= 0.15:
            conf = min(0.99, max(0.85, telugu_ratio * 1.5))
            return "te", conf

        if kannada_chars >= 2 and kannada_ratio >= 0.15:
            conf = min(0.99, max(0.85, kannada_ratio * 1.5))
            return "kn", conf

        if malayalam_chars >= 2 and malayalam_ratio >= 0.15:
            conf = min(0.99, max(0.85, malayalam_ratio * 1.5))
            return "ml", conf

        return None

    def detect_romanized_lexicon(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Checks for transliterated / Romanized words (Tanglish / Hinglish / Manglish).
        """
        words = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))
        if not words:
            return None

        tamil_matches = words.intersection(TAMIL_ROMANIZED_KEYWORDS)
        hindi_matches = words.intersection(HINDI_ROMANIZED_KEYWORDS)
        malayalam_matches = words.intersection(MALAYALAM_ROMANIZED_KEYWORDS)

        if len(tamil_matches) >= 2 or (len(tamil_matches) == 1 and len(words) <= 5):
            conf = min(0.95, 0.70 + (len(tamil_matches) * 0.1))
            return "ta", conf

        if len(hindi_matches) >= 2 or (len(hindi_matches) == 1 and len(words) <= 5):
            conf = min(0.95, 0.70 + (len(hindi_matches) * 0.1))
            return "hi", conf

        if len(malayalam_matches) >= 2 or (len(malayalam_matches) == 1 and len(words) <= 5):
            conf = min(0.95, 0.70 + (len(malayalam_matches) * 0.1))
            return "ml", conf

        return None

    def detect_statistical(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Statistical n-gram language detection via langdetect.
        """
        if not LANGDETECT_AVAILABLE:
            return None

        # Filter out numbers and special characters
        cleaned = re.sub(r"[0-9\W]+", " ", text).strip()
        if len(cleaned) < 3:
            return None

        try:
            results = detect_langs(cleaned)
            if results:
                best = results[0]
                lang_code = best.lang
                prob = float(best.prob)
                return lang_code, prob
        except Exception as exc:
            logger.debug("langdetect exception on '%s': %s", text[:30], exc)

        return None

    def detect_language(
        self,
        text: str,
        explicit_language: Optional[str] = None,
    ) -> LanguageDetectionResult:
        """
        Primary detection method executing the prioritized identification pipeline:
        1. Explicit language override
        2. Unicode script block check
        3. Romanized lexicon check
        4. Statistical n-gram detection
        5. Default fallback
        """
        # 1. Explicit language override
        if explicit_language:
            norm_code = self.normalize_language_code(explicit_language)
            if norm_code:
                is_supp = norm_code in self.supported_languages
                lang_name = LANGUAGE_METADATA_MAP.get(norm_code, norm_code.upper())
                logger.info(
                    "LanguageDetector: Explicit language requested '%s' (Normalized: '%s', Supported: %s)",
                    explicit_language,
                    norm_code,
                    is_supp,
                )
                return LanguageDetectionResult(
                    language_code=norm_code,
                    language_name=lang_name,
                    confidence=1.0,
                    detection_method="explicit",
                    is_supported=is_supp,
                )

        if not text or not text.strip() or not LANGUAGE_DETECTION_ENABLED:
            return LanguageDetectionResult(
                language_code=self.default_language,
                language_name=LANGUAGE_METADATA_MAP.get(self.default_language, "English"),
                confidence=1.0,
                detection_method="default_fallback",
                is_supported=True,
            )

        cleaned_text = text.strip()

        # 2. Unicode script detection
        script_res = self.detect_unicode_script(cleaned_text)
        if script_res:
            code, conf = script_res
            is_supp = code in self.supported_languages
            lang_name = LANGUAGE_METADATA_MAP.get(code, code.upper())
            logger.info("LanguageDetector: Detected '%s' (%s) via Unicode Script (conf: %.2f)", code, lang_name, conf)
            return LanguageDetectionResult(
                language_code=code,
                language_name=lang_name,
                confidence=conf,
                detection_method="unicode_script",
                is_supported=is_supp,
            )

        # 3. Romanized lexicon check
        lex_res = self.detect_romanized_lexicon(cleaned_text)
        if lex_res:
            code, conf = lex_res
            is_supp = code in self.supported_languages
            lang_name = LANGUAGE_METADATA_MAP.get(code, code.upper())
            logger.info("LanguageDetector: Detected '%s' (%s) via Romanized Lexicon (conf: %.2f)", code, lang_name, conf)
            return LanguageDetectionResult(
                language_code=code,
                language_name=lang_name,
                confidence=conf,
                detection_method="lexical_heuristic",
                is_supported=is_supp,
            )

        # 4. Statistical detection
        stat_res = self.detect_statistical(cleaned_text)
        if stat_res:
            code, conf = stat_res
            is_supp = code in self.supported_languages
            lang_name = LANGUAGE_METADATA_MAP.get(code, code.upper())
            logger.info("LanguageDetector: Detected '%s' (%s) via Statistical Model (conf: %.2f)", code, lang_name, conf)
            return LanguageDetectionResult(
                language_code=code,
                language_name=lang_name,
                confidence=conf,
                detection_method="statistical",
                is_supported=is_supp,
            )

        # 5. Default fallback
        logger.info("LanguageDetector: Defaulting to '%s' for query '%s'", self.default_language, cleaned_text[:30])
        return LanguageDetectionResult(
            language_code=self.default_language,
            language_name=LANGUAGE_METADATA_MAP.get(self.default_language, "English"),
            confidence=0.80,
            detection_method="default_fallback",
            is_supported=True,
        )


language_detector = LanguageDetector()
