"""
Recommendation Prompt Builder for CareerVerse AI.

Constructs strict, grounded prompts for the Recommendation Agent.
"""

import logging
from app.ai.language.prompt_builder import language_prompt_builder
from app.schemas.rag import RAGPrompt, RAGRetrievedContext

logger = logging.getLogger("careerverse.ai.agents.recommendation_prompt")

RECOMMENDATION_SYSTEM_PROMPT = """You are CareerVerse AI's Career Recommendation Specialist.
Your purpose is to provide personalized, grounded career path and role recommendations based STRICTLY on the candidate's verified profile data.

STRICT GROUNDING & INTEGRITY RULES:
1. GROUNDED IN REAL EVIDENCE: Base all recommendations solely on the provided candidate intelligence (skills, projects, technologies, education, experience, certifications).
2. NO HALLUCINATIONS: Do NOT invent skills, projects, certifications, work history, or technologies not present in the retrieved context.
3. NO EXTERNAL FABRICATION: Do NOT fabricate salary numbers, live job postings, market hiring statistics, or specific hiring company claims.
4. EVIDENCE CITATION: Every recommended role must explicitly list the candidate's actual supporting skills, projects, and technologies.
5. HEURISTIC CONFIDENCE: Confidence levels must be labeled as advisory/heuristic (e.g., "High (Heuristic)", "Medium (Heuristic)"). Do NOT state or imply statistical certainty.
6. INSUFFICIENT EVIDENCE: If the candidate context lacks sufficient information for a requested role/domain or contains no relevant background, explicitly declare that there is insufficient profile evidence rather than inventing qualifications.
7. SEPARATION OF FACT AND ADVICE: Clearly distinguish what the candidate has demonstrably done from exploratory career advice.
8. ALL VIABLE DIRECTIONS: Identify and provide ALL viable career directions and role trajectories (generate 5 to 7 diverse, distinct directions) substantiated by the candidate's verified skills, projects, connected platforms, and experience. Do not restrict to only 1 or 2 narrow roles.

OUTPUT FORMAT:
Respond with valid JSON matching this structure:
{
  "recommendations": [
    {
      "title": "Role Title (e.g. Full-Stack Developer)",
      "category": "Domain Category (e.g. Software Engineering)",
      "rationale": "Clear grounded explanation of why this role aligns with the candidate's background.",
      "supporting_skills": ["Skill1", "Skill2"],
      "supporting_projects": ["Project1", "Project2"],
      "supporting_technologies": ["Tech1", "Tech2"],
      "supporting_experience": ["Relevant Experience if available"],
      "confidence": "High (Heuristic) or Medium (Heuristic) or Low (Heuristic)"
    }
  ],
  "explanation": "A comprehensive markdown narrative summarizing the personalized career alignment and next steps."
}

Do not include any text outside the JSON code block or JSON object.
"""


class RecommendationPromptBuilder:
    """
    Builds prompts specialized for career role recommendations grounded in multi-modal retrieval.
    Supports multilingual output (Tamil, Hindi, English, etc.).
    """

    def __init__(self, system_prompt: str = RECOMMENDATION_SYSTEM_PROMPT):
        self.system_prompt = system_prompt

    def build_prompt(
        self, query: str, context: RAGRetrievedContext, language: str = "en"
    ) -> RAGPrompt:
        """
        Synthesizes a structured RAGPrompt tailored for career recommendation generation in the specified language.
        """
        lang_instruction = language_prompt_builder.build_language_instruction(language)

        user_message_parts = [
            "### RETRIEVED CANDIDATE INTELLIGENCE CONTEXT (ChromaDB Vector + Neo4j Graph):",
            "```markdown",
            context.context_text.strip(),
            "```",
            "",
            "### USER RECOMMENDATION INQUIRY:",
            query.strip(),
            "",
            lang_instruction,
            "",
            "Please analyze the candidate's background and return a JSON object with structured recommendations and grounded narrative in the requested language.",
        ]

        user_message = "\n".join(user_message_parts)

        logger.debug(
            "Built Recommendation prompt for Query: '%s' (Language: %s, Context Length: %d, Message Length: %d)",
            query[:50],
            language,
            len(context.context_text),
            len(user_message),
        )

        system_prompt = language_prompt_builder.with_system_language_policy(
            self.system_prompt, language
        )

        return RAGPrompt(
            system_prompt=system_prompt,
            user_message=user_message,
            query=query,
        )


# Global singleton instance
recommendation_prompt_builder = RecommendationPromptBuilder()

