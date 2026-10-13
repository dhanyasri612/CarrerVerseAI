"""
Multilingual Prompt Builder for CareerVerse AI.

Constructs dynamic language instructions ensuring:
1. Natural language response in the user's preferred language (Tamil, Hindi, English, etc.)
2. Preservation of technical terms (Python, React, FastAPI, SQL, Neo4j, etc.) in standard Latin script
3. Strict grounding and anti-hallucination rules enforced across all languages
"""

import logging
from typing import Dict, Optional

from app.ai.language.detector import LANGUAGE_METADATA_MAP

logger = logging.getLogger("careerverse.ai.language.prompt_builder")


class LanguagePromptBuilder:
    """
    Builds language instruction snippets dynamically for LLM system prompts.
    """

    TECHNICAL_TERMS_RULE = (
        "CRITICAL TECHNICAL ENTITY RULE:\n"
        "Do NOT translate technical terms and tool names into literal or awkward local words.\n"
        "Preserve recognized technical names in standard Latin script (e.g. Python, Java, JavaScript, "
        "TypeScript, React, FastAPI, Express.js, PostgreSQL, MySQL, MongoDB, Neo4j, ChromaDB, GitHub, "
        "LeetCode, HackerRank, REST API, SQL, Docker, Kubernetes, AWS, GCP, Azure, CI/CD, Redis, Git, "
        "Machine Learning, Deep Learning, CNN, LLM, etc.). Translate only the surrounding explanatory and narrative text."
    )

    GROUNDING_RULE = (
        "CRITICAL GROUNDING & ANTI-HALLUCINATION RULE:\n"
        "- Base all statements strictly on the candidate evidence provided.\n"
        "- Do NOT invent skills, projects, certifications, or work experience in any language.\n"
        "- If a queried skill, project, or role is not present in the candidate evidence, clearly state in the target language "
        "that it is not found in the verified profile."
    )

    def build_language_instruction(self, language_code: str) -> str:
        """
        Generates prompt instructions for the target language.
        """
        code = language_code.lower().strip()
        lang_name = LANGUAGE_METADATA_MAP.get(code, "English")

        if code == "en":
            return (
                f"\n=== LANGUAGE REQUIREMENT ===\n"
                f"- Output Language: English.\n"
                f"{self.GROUNDING_RULE}\n"
            )

        if code in ("ta", "tanglish"):
            return (
                f"\n=== LANGUAGE REQUIREMENT (CONVERSATIONAL TAMIL / TANGLISH) ===\n"
                f"- The candidate communicates in Tamil / Tanglish. Generate questions, explanations, and coaching in "
                f"natural, friendly, conversational spoken Tamil / Tanglish as used by modern software engineers.\n"
                f"- CRITICAL REGISTER RULE: NEVER use archaic, bookish, or formal literary 'Thooya Tamil' (தூய தமிழ்). "
                f"Avoid archaic words like கணினி நிரலாக்கம் or தரவுத்தளம். Engineers speak conversationally!\n"
                f"- Keep ALL technical terms and keywords in standard English (e.g., SQL, React, Python, Index, Table, "
                f"Database, API, Function, Loop, Cache, Latency, Component, State, Hook).\n"
                f"- Friendly conversational style: 'Ena panreenga, nala irukkeengala? SQL lesson romba easyaa irukka? "
                f"Indha query-la index epdi optimize aaguthu nu paapom.'\n"
                f"- {self.TECHNICAL_TERMS_RULE}\n"
                f"- {self.GROUNDING_RULE}\n"
            )

        if code in ("hi", "hinglish"):
            return (
                f"\n=== LANGUAGE REQUIREMENT (CONVERSATIONAL HINDI / HINGLISH) ===\n"
                f"- The candidate communicates in Hindi / Hinglish. Generate the response in natural, conversational, "
                f"friendly spoken Hinglish as spoken by software engineers (Devanagari or friendly Latin Hinglish).\n"
                f"- Keep technical terms in standard English (Python, FastAPI, Backend, API, Database, Index, etc.).\n"
                f"- Friendly conversational style: 'Aapka approach accha hai, ab dekhte hain isme edge case kaise handle karenge.'\n"
                f"- {self.TECHNICAL_TERMS_RULE}\n"
                f"- {self.GROUNDING_RULE}\n"
            )

        # General foreign language support
        return (
            f"\n=== LANGUAGE REQUIREMENT ({lang_name.upper()}) ===\n"
            f"- You MUST generate the final response and explanations in natural, fluent {lang_name}.\n"
            f"- {self.TECHNICAL_TERMS_RULE}\n"
            f"- {self.GROUNDING_RULE}\n"
        )


language_prompt_builder = LanguagePromptBuilder()
