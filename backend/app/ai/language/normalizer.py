"""
Query Normalizer and Intent Translator for Multilingual AI.

Provides semantic query normalization from supported languages (Tamil, Hindi, etc.)
into canonical English query representations for internal semantic search & task routing,
while strictly preserving the user's original query in state.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("careerverse.ai.language.normalizer")

# Mapping of common multilingual domain keywords to canonical English concepts
INTENT_TRANSLATION_MAP: List[Tuple[re.Pattern, str]] = [
    # Tamil - Recommendation
    (re.compile(r"(பொருத்தமான|பரிந்துரை|பொருந்தும்|வேலை வாய்ப்பு|career roles|roles fit)", re.IGNORECASE), "suitable career roles recommendation"),
    # Tamil - Skill Gap / Evaluation
    (re.compile(r"(skills வேண்டும்|விடுபட்டுள்ளன|குறைபாடு|தேவைப்படும்|இடைவெளி|கற்க வேண்டும்|என்ன skills)", re.IGNORECASE), "skill gap evaluation missing skills"),
    # Tamil - Interview
    (re.compile(r"(interview questions|நேர்காணல்|கேள்விகள்|தயார் செய்வது|interview prep)", re.IGNORECASE), "interview questions preparation"),

    # Hindi - Recommendation
    (re.compile(r"(उपयुक्त|सुझाव|करियर|roles मेरे लिए|करियर रोल्स)", re.IGNORECASE), "suitable career roles recommendation"),
    # Hindi - Skill Gap / Evaluation
    (re.compile(r"(सीखने चाहिए|कमी है|skill gap|कौन से skills|कौशल सीखने|कमी)", re.IGNORECASE), "skill gap evaluation missing skills"),
    # Hindi - Interview
    (re.compile(r"(interview questions|साक्षात्कार|तैयारी|प्रश्न|तैयारी कैसे)", re.IGNORECASE), "interview questions preparation"),
]

# Canonical role extractions across scripts
ROLE_TRANSLATION_MAP: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"backend developer|பேக்கெண்ட் டெவலப்பர்|बैकएंड डेवलपर", re.IGNORECASE), "Backend Developer"),
    (re.compile(r"frontend developer|பிரண்ட்எண்ட் டெவலப்பர்|फ्रंटएंड डेवलपर", re.IGNORECASE), "Frontend Developer"),
    (re.compile(r"full stack developer|ஃபுல் ஸ்டாக் டெவலப்பர்|फुल स्टैक डेवलपर", re.IGNORECASE), "Full Stack Developer"),
    (re.compile(r"machine learning engineer|மெஷின் லேர்னிங்|मशीन लर्निंग", re.IGNORECASE), "Machine Learning Engineer"),
    (re.compile(r"data scientist|டேட்டா சயின்டிஸ்ட்|डेटा साइंटिस्ट", re.IGNORECASE), "Data Scientist"),
    (re.compile(r"software developer|மென்பொருள் பொறியாளர்|सॉफ्टवेयर डेवलपर", re.IGNORECASE), "Software Developer"),
    (re.compile(r"rocket propulsion engineer|ராக்கெட்|रॉकेट", re.IGNORECASE), "Rocket Propulsion Engineer"),
]


class QueryNormalizer:
    """
    Normalizes multilingual queries for deterministic internal routing and semantic retrieval.
    """

    def extract_role_multilingual(self, query: str) -> Optional[str]:
        """Extracts canonical role title from multilingual text."""
        from app.ai.agents.role_requirements import get_role_requirements
        for pattern, role_title in ROLE_TRANSLATION_MAP:
            if pattern.search(query):
                reqs = get_role_requirements(role_title)
                if reqs:
                    return reqs["title"]
                return role_title
        return None

    def normalize_query(self, query: str, language_code: str) -> str:
        """
        Produces an English semantic representation of the query for internal processing
        if the query is in a non-English language.
        """
        if language_code == "en" or not query.strip():
            return query.strip()

        cleaned = query.strip()
        role = self.extract_role_multilingual(cleaned)

        matched_intents = []
        for pattern, eng_phrase in INTENT_TRANSLATION_MAP:
            if pattern.search(cleaned):
                matched_intents.append(eng_phrase)

        if not matched_intents and not role:
            return cleaned

        parts = []
        if role:
            parts.append(f"role '{role}'")
        if matched_intents:
            parts.append(" ".join(matched_intents))

        normalized = f"Career analysis for {', '.join(parts)} based on candidate profile evidence"
        logger.info(
            "QueryNormalizer: Normalized '%s' (%s) -> '%s'",
            cleaned[:40],
            language_code,
            normalized,
        )
        return normalized

    def normalize(self, query: str, language: str = "en") -> str:
        """Alias for normalize_query."""
        return self.normalize_query(query, language_code=language)


query_normalizer = QueryNormalizer()
