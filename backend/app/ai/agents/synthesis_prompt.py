"""
Final Synthesis Prompt Builder for CareerVerse AI Multi-Agent Coordination.

Constructs grounded prompts that instruct the LLM to synthesize outputs from
Recommendation Agent, Skill-Gap Evaluation Agent, and Interview Agent into a coherent,
unified career intelligence response without duplicating raw text or hallucinating.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from app.ai.language.prompt_builder import language_prompt_builder
from app.schemas.rag import RAGPrompt

logger = logging.getLogger("careerverse.ai.agents.synthesis_prompt")


class SynthesisPromptBuilder:
    """
    Builds strict, grounded synthesis prompts enforcing:
    - Truthfulness and grounding in supplied candidate evidence
    - Preservation of deterministic skill gaps and agent outputs
    - Synthesis into a unified response rather than simple string concatenation
    - Strict JSON structured output format in requested language (Tamil, Hindi, English, etc.)
    """

    SYSTEM_PROMPT = """You are the CareerVerse AI Multi-Agent Synthesis Agent.
Your responsibility is to synthesize outputs from specialized career intelligence agents (Recommendation Agent, Skill-Gap Agent, Interview Agent) into a unified, highly coherent, grounded career intelligence report.

STRICT SYNTHESIS CONSTRAINTS:
1. Use ONLY the supplied candidate profile facts, agent outputs, and retrieved context.
2. DO NOT invent or assume candidate skills, projects, degrees, certifications, or work experience.
3. DO NOT fabricate or assume role requirements beyond what the agents identified.
4. Preserve the deterministic skill-gap evaluation findings and evidence exactly.
5. Clearly distinguish between:
   - Verified candidate facts (proven evidence)
   - Career recommendations (heuristic advisory guidance)
   - Identified skill gaps (areas requiring development)
   - Interview preparation (targeted questions and strategies)
6. DO NOT claim that a recommendation is objectively guaranteed or correct.
7. DO NOT claim an interview question will definitely be asked.
8. DO NOT invent salary, job market numbers, hiring statistics, or external sources.
9. Produce ONE coherent, flowing response rather than three disconnected answers.
10. Avoid redundant repetition of the same skills or projects across different sections.
11. If an agent was not executed or failed, acknowledge the available information honestly without fabricating the missing parts.

OUTPUT FORMAT REQUIREMENTS:
You MUST respond with a single, valid JSON object strictly matching this schema:
```json
{
  "summary": "<High-level executive overview synthesizing the candidate's background, recommended career direction, and readiness>",
  "final_guidance": "<Comprehensive, actionable, unified career intelligence guidance harmonizing recommendations, skill development priorities, and interview preparation strategies>"
}
```
Do NOT include any text outside the JSON block.
"""

    def build_prompt(
        self,
        query: str,
        aggregated_context: Dict[str, Any],
        language: str = "en",
    ) -> RAGPrompt:
        """
        Builds the complete grounded RAGPrompt for the Synthesis Agent in the target language.
        """
        candidate_id = aggregated_context.get("candidate_id")
        target_role = aggregated_context.get("target_role")
        tasks = aggregated_context.get("tasks", [])
        candidate_profile = aggregated_context.get("candidate_profile", {})
        rec_data = aggregated_context.get("recommendation")
        eval_data = aggregated_context.get("evaluation")
        interview_data = aggregated_context.get("interview")
        errors = aggregated_context.get("errors", [])

        lang_instruction = language_prompt_builder.build_language_instruction(language)

        user_message_parts: List[str] = [
            f"USER QUERY: {query}",
            f"CANDIDATE ID: {candidate_id}",
            f"TARGET ROLE: {target_role if target_role else 'None Specified'}",
            f"COORDINATED TASKS: {', '.join(tasks)}",
            "",
            "=== VERIFIED CANDIDATE PROFILE FACTS ===",
            f"Demonstrated Skills: {', '.join(candidate_profile.get('skills', [])) if candidate_profile.get('skills') else 'None verified'}",
            f"Verified Projects: {', '.join(candidate_profile.get('projects', [])) if candidate_profile.get('projects') else 'None verified'}",
            f"Technologies Used: {', '.join(candidate_profile.get('technologies', [])) if candidate_profile.get('technologies') else 'None verified'}",
            f"Work Experience: {', '.join(candidate_profile.get('experience', [])) if candidate_profile.get('experience') else 'None listed'}",
            f"Certifications: {', '.join(candidate_profile.get('certifications', [])) if candidate_profile.get('certifications') else 'None listed'}",
            f"Education: {', '.join(candidate_profile.get('education', [])) if candidate_profile.get('education') else 'None listed'}",
            "",
        ]

        if rec_data:
            user_message_parts.append("=== RECOMMENDATION AGENT OUTPUT ===")
            user_message_parts.append(f"Status: {rec_data.get('status')}")
            recs = rec_data.get("recommendations", [])
            for i, r in enumerate(recs, 1):
                user_message_parts.append(
                    f"  {i}. {r.get('title')} ({r.get('category')} - Fit: {r.get('confidence')}): {r.get('rationale')}"
                )
            user_message_parts.append(f"Explanation: {rec_data.get('explanation')}")
            user_message_parts.append("")

        if eval_data:
            user_message_parts.append(f"=== SKILL-GAP / EVALUATION AGENT OUTPUT (Target: {eval_data.get('target_role')}) ===")
            user_message_parts.append(f"Status: {eval_data.get('status')}")
            user_message_parts.append(f"Strengths: {', '.join(eval_data.get('strengths', []))}")
            gaps = eval_data.get("skill_gaps", [])
            for g in gaps:
                user_message_parts.append(
                    f"  - Skill: {g.get('skill')} | Status: {g.get('status')} | Gap Level: {g.get('gap_level')} | Evidence: {', '.join(g.get('candidate_evidence', []))}"
                )
            user_message_parts.append(f"Summary: {eval_data.get('summary')}")
            user_message_parts.append(f"Improvement Areas: {', '.join(eval_data.get('improvement_areas', []))}")
            user_message_parts.append("")

        if interview_data:
            user_message_parts.append("=== INTERVIEW PREPARATION AGENT OUTPUT ===")
            user_message_parts.append(f"Status: {interview_data.get('status')}")
            user_message_parts.append(f"Interview Mode: {interview_data.get('interview_mode')}")
            questions = interview_data.get("questions", [])
            for i, q in enumerate(questions, 1):
                user_message_parts.append(
                    f"  {i}. [{q.get('question_type')} - {q.get('difficulty')}]: {q.get('question')} (Topic: {q.get('topic')})"
                )
            user_message_parts.append(f"Preparation Advice: {interview_data.get('preparation_summary')}")
            user_message_parts.append("")

        if errors:
            user_message_parts.append(f"EXECUTION WARNINGS/ERRORS: {'; '.join(errors)}")
            user_message_parts.append("")

        user_message_parts.append(lang_instruction)
        user_message_parts.append(
            "Synthesize the above information into a single unified career report in JSON format matching the schema in the requested language."
        )

        user_message = "\n".join(user_message_parts)

        return RAGPrompt(
            system_prompt=self.SYSTEM_PROMPT,
            user_message=user_message,
            query=query,
        )


synthesis_prompt_builder = SynthesisPromptBuilder()

