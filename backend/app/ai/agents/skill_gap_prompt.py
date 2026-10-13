"""
Skill-Gap Evaluation Prompt Builder for CareerVerse AI.

Constructs strict, grounded prompts for the Skill-Gap / Evaluation Agent.
"""

import logging
from typing import Any, Dict, List
from app.ai.language.prompt_builder import language_prompt_builder
from app.schemas.rag import RAGPrompt, RAGRetrievedContext
from app.schemas.skill_gap import SkillGapItem

logger = logging.getLogger("careerverse.ai.agents.skill_gap_prompt")

EVALUATION_SYSTEM_PROMPT = """You are CareerVerse AI's Candidate Evaluation & Skill-Gap Specialist.
Your purpose is to synthesize a grounded evaluation narrative and actionable improvement focus areas based STRICTLY on the supplied deterministic skill comparison table and candidate intelligence.

STRICT GROUNDING & INTEGRITY RULES:
1. PRESERVE FACTUAL STATUSES: You must strictly adhere to the deterministic skill evaluation results provided below. Do NOT alter any skill's status (demonstrated, partially_demonstrated, missing, insufficient_evidence) or invent candidate proficiency.
2. NO HALLUCINATIONS: Do NOT fabricate courses, live company hiring standards, certifications, salary data, or experience not present in the context.
3. NO ARBITRARY PERCENTAGES: Do NOT invent arbitrary overall percentage scores (e.g. "You have 85% match"). Use the categorical statuses and counts provided.
4. ACTIONABLE IMPROVEMENT: Suggest clear, grounded upskilling and learning directions focused specifically on the identified missing and partially demonstrated skills.
5. PROFESSIONAL TONE: Provide an objective, encouraging, and structured assessment formatted in clean markdown.

OUTPUT FORMAT:
Respond with valid JSON matching this structure:
{
  "summary": "Comprehensive markdown synthesis summarizing verified strengths, key gaps, and readiness for the target role.",
  "improvement_areas": [
    "Specific improvement focus area 1 (e.g., Deepen Containerization & Docker deployment skills)",
    "Specific improvement focus area 2"
  ]
}

Do not include any text outside the JSON object.
"""


class SkillGapPromptBuilder:
    """
    Builds evaluation prompts combining deterministic skill analysis, role specifications,
    and retrieved candidate context. Supports multilingual output (Tamil, Hindi, English, etc.).
    """

    def __init__(self, system_prompt: str = EVALUATION_SYSTEM_PROMPT):
        self.system_prompt = system_prompt

    def build_prompt(
        self,
        target_role: str,
        query: str,
        skill_gaps: List[SkillGapItem],
        strengths: List[str],
        audit_metrics: Dict[str, Any],
        context: RAGRetrievedContext,
        language: str = "en",
    ) -> RAGPrompt:
        """
        Synthesizes a structured RAGPrompt for the Evaluation Agent in the specified language.
        """
        lang_instruction = language_prompt_builder.build_language_instruction(language)

        # Format the deterministic comparison table
        table_rows = []
        table_rows.append("| Skill | Requirement | Status | Gap Level | Candidate Evidence |")
        table_rows.append("| :--- | :--- | :--- | :--- | :--- |")
        for item in skill_gaps:
            evidence_str = "; ".join(item.candidate_evidence) if item.candidate_evidence else "None"
            table_rows.append(
                f"| **{item.skill}** ({item.category}) | {item.target_requirement} | `{item.status}` | `{item.gap_level}` | {evidence_str} |"
            )
        comparison_table = "\n".join(table_rows)

        user_message_parts = [
            f"### TARGET ROLE EVALUATION: {target_role}",
            "",
            "### DETERMINISTIC CANDIDATE SKILL COMPARISON TABLE (Ground Truth):",
            comparison_table,
            "",
            f"### AUDIT METRICS:",
            f"- Demonstrated Skills ({audit_metrics.get('demonstrated_count', 0)}): {', '.join(strengths) if strengths else 'None'}",
            f"- Partially Demonstrated ({audit_metrics.get('partial_count', 0)})",
            f"- Missing Skills ({audit_metrics.get('missing_count', 0)})",
            f"- Insufficient Evidence ({audit_metrics.get('insufficient_count', 0)})",
            "",
            "### CANDIDATE MULTI-MODAL RETRIEVED CONTEXT:",
            "```markdown",
            context.context_text.strip()[:4000],  # Truncate context cleanly if long
            "```",
            "",
            "### USER QUERY:",
            query.strip(),
            "",
            lang_instruction,
            "",
            "Please generate the grounded evaluation summary and prioritized improvement areas in JSON format in the requested language.",
        ]

        user_message = "\n".join(user_message_parts)

        return RAGPrompt(
            system_prompt=self.system_prompt,
            user_message=user_message,
            query=query,
        )


# Global singleton instance
skill_gap_prompt_builder = SkillGapPromptBuilder()

