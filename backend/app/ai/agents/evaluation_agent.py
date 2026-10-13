"""
Evaluation & Skill-Gap Agent for CareerVerse AI.

Compares candidate evidence against system-defined target role requirements deterministically,
and generates grounded explanation and improvement paths using Groq LLM.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from app.ai.agents.role_requirements import get_role_requirements, list_available_roles
from app.ai.agents.skill_gap_analyzer import (
    SkillGapAnalyzer,
    skill_gap_analyzer,
)
from app.ai.agents.skill_gap_prompt import (
    SkillGapPromptBuilder,
    skill_gap_prompt_builder,
)
from app.ai.providers.base import ModelProvider
from app.ai.providers.factory import get_model_provider
from app.ai.rag.context_builder import RAGContextBuilder, rag_context_builder
from app.schemas.rag import RAGRetrievedContext
from app.schemas.skill_gap import SkillGapItem, SkillGapResponse

logger = logging.getLogger("careerverse.ai.agents.evaluation_agent")


class EvaluationAgent:
    """
    Candidate Evaluation & Skill-Gap Agent.
    Orchestrates deterministic candidate graph comparison and grounded LLM explanation.
    """

    def __init__(
        self,
        analyzer: SkillGapAnalyzer = skill_gap_analyzer,
        context_builder: RAGContextBuilder = rag_context_builder,
        prompt_builder: SkillGapPromptBuilder = skill_gap_prompt_builder,
        llm_provider: Optional[ModelProvider] = None,
    ):
        self.analyzer = analyzer
        self.context_builder = context_builder
        self.prompt_builder = prompt_builder
        self._llm_provider = llm_provider

    @property
    def llm_provider(self) -> ModelProvider:
        """Lazy load the default LLM provider."""
        if self._llm_provider is None:
            self._llm_provider = get_model_provider()
        return self._llm_provider

    def _parse_llm_json(self, raw_content: str) -> Dict[str, Any]:
        """
        Safely extracts JSON payload from LLM response with code-block handling.
        """
        cleaned = raw_content.strip()

        # Try direct JSON parse first
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Try extracting from code block fences
        if "```" in cleaned:
            code_blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
            for block in code_blocks:
                try:
                    return json.loads(block.strip())
                except json.JSONDecodeError:
                    pass

        # Extract between outermost { and }
        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            try:
                return json.loads(cleaned[first_brace : last_brace + 1])
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Failed to parse valid JSON from LLM response: {raw_content[:200]}...")

    def evaluate_skill_gaps(
        self,
        candidate_id: int,
        target_role: Optional[str] = None,
        query: Optional[str] = None,
        language: str = "en",
        top_k: int = 5,
        temperature: float = 0.2,
    ) -> SkillGapResponse:
        """
        Executes grounded evaluation pipeline:
        1. Role requirements validation
        2. Deterministic candidate evidence comparison (Ground Truth)
        3. Multi-modal RAG retrieval (ChromaDB + Neo4j)
        4. Grounded narrative generation via LLM in requested language
        5. Structured Pydantic validation
        """
        effective_query = query or (
            f"Evaluate my skills and identify gaps for {target_role}."
            if target_role
            else "Evaluate my skills and identify career gaps."
        )
        logger.info(
            "Evaluation Agent: Evaluating Candidate ID %d for Target Role: '%s', Language: '%s'",
            candidate_id,
            target_role,
            language,
        )

        # 1. Handle missing / absent Target Role safely
        if not target_role or not str(target_role).strip():
            msg = "Target role is required for role-specific skill-gap evaluation. Please specify a target role (e.g., Backend Developer, Frontend Developer, Data Scientist)."
            logger.info("Evaluation Agent: %s", msg)
            return SkillGapResponse(
                candidate_id=candidate_id,
                target_role=None,
                query=effective_query,
                strengths=[],
                skill_gaps=[],
                summary="Role-specific skill-gap analysis requires a target role. Please specify a target role (such as Backend Developer or Frontend Developer) to evaluate required skills and gap severity.",
                improvement_areas=[
                    "Specify a target job role to perform detailed requirement comparison and skill-gap analysis."
                ],
                model_name=None,
                status="target_role_required",
                errors=[],
            )

        # 2. Validate Target Role in registry
        role_reqs = get_role_requirements(target_role)
        if not role_reqs:
            available = list_available_roles()
            error_msg = f"Unknown or unsupported target role '{target_role}'. Supported roles: {', '.join(available)}"
            logger.warning(error_msg)
            return SkillGapResponse(
                candidate_id=candidate_id,
                target_role=target_role,
                query=effective_query,
                strengths=[],
                skill_gaps=[],
                summary=f"Evaluation could not be performed: {error_msg}",
                improvement_areas=[],
                model_name=None,
                status="invalid_role",
                errors=[error_msg],
            )

        canonical_role_title = role_reqs["title"]

        # 2. Deterministic Evidence Analysis (Ground Truth)
        skill_gaps, strengths, audit_metrics = self.analyzer.analyze_candidate_skill_gaps(
            candidate_id=candidate_id,
            target_role=canonical_role_title,
        )

        # 3. Retrieve Multi-modal context
        context: RAGRetrievedContext = self.context_builder.build_retrieval_context(
            candidate_id=candidate_id,
            query=effective_query,
            top_k=top_k,
        )

        # 4. Prompt construction
        prompt = self.prompt_builder.build_prompt(
            target_role=canonical_role_title,
            query=effective_query,
            skill_gaps=skill_gaps,
            strengths=strengths,
            audit_metrics=audit_metrics,
            context=context,
            language=language,
        )

        # 5. LLM Inference
        provider_response = self.llm_provider.generate_text(
            system_prompt=prompt.system_prompt,
            user_message=prompt.user_message,
            temperature=temperature,
        )

        raw_output = provider_response.content.strip()
        model_name = provider_response.model

        # Helper to construct compatibility skill representations
        matched_skills_list = [
            {"name": item.skill, "category": item.category, "source": ", ".join(item.evidence_sources) or "Verified Profile", "evidence": ", ".join(item.candidate_evidence) or "Demonstrated"}
            for item in skill_gaps if item.status == "demonstrated"
        ]
        if not matched_skills_list and strengths:
            matched_skills_list = [{"name": s, "category": "Core Skill", "source": "Profile Evidence", "evidence": "Evidenced"} for s in strengths]

        missing_skills_list = [
            {"name": item.skill, "category": item.category, "priority": f"{item.gap_level.upper()} Priority", "explanation": item.explanation}
            for item in skill_gaps if item.status == "missing"
        ]

        partial_skills_list = [
            {"name": item.skill, "category": item.category, "gap": item.explanation or "Partial evidence", "explanation": item.explanation}
            for item in skill_gaps if item.status in ("partially_demonstrated", "insufficient_evidence")
        ]

        total_count = len(matched_skills_list) + len(missing_skills_list) + len(partial_skills_list)
        readiness_val = round(len(matched_skills_list) / max(total_count, 1), 2)

        # 6. Parse structured narrative and improvements
        try:
            parsed = self._parse_llm_json(raw_output)
            summary = parsed.get("summary", raw_output)
            improvements = parsed.get("improvement_areas", [])
            if not isinstance(improvements, list):
                improvements = [str(improvements)]

            return SkillGapResponse(
                candidate_id=candidate_id,
                target_role=canonical_role_title,
                query=effective_query,
                strengths=strengths,
                skill_gaps=skill_gaps,
                summary=summary,
                improvement_areas=improvements,
                matched_skills=matched_skills_list,
                missing_skills=missing_skills_list,
                partial_skills=partial_skills_list,
                readiness_score=readiness_val,
                model_name=model_name,
                status="completed",
                errors=[],
            )

        except Exception as parse_err:
            logger.warning(
                "Structured JSON parsing failed for evaluation output, using safe fallback: %s",
                str(parse_err),
            )
            return SkillGapResponse(
                candidate_id=candidate_id,
                target_role=canonical_role_title,
                query=effective_query,
                strengths=strengths,
                skill_gaps=skill_gaps,
                summary=raw_output,
                improvement_areas=[
                    f"Focus on missing requirements: {', '.join([item.skill for item in skill_gaps if item.status == 'missing'][:3])}"
                ],
                matched_skills=matched_skills_list,
                missing_skills=missing_skills_list,
                partial_skills=partial_skills_list,
                readiness_score=readiness_val,
                model_name=model_name,
                status="completed",
                errors=[f"Structured parsing warning: {str(parse_err)}"],
            )


# Global singleton instance
evaluation_agent = EvaluationAgent()
