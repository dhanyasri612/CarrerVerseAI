"""
Final Synthesis Agent for CareerVerse AI Multi-Agent System.

Synthesizes outputs from Recommendation Agent, Evaluation/Skill-Gap Agent,
and Interview Preparation Agent into a unified, grounded MultiAgentResponse.
Handles partial agent failures gracefully without fabricating missing results.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from app.ai.agents.context_aggregator import ContextAggregator, context_aggregator
from app.ai.agents.synthesis_prompt import (
    SynthesisPromptBuilder,
    synthesis_prompt_builder,
)
from app.ai.providers.base import ModelProvider
from app.ai.providers.factory import get_model_provider
from app.schemas.interview import InterviewResponse
from app.schemas.multi_agent import AgentExecutionResult, MultiAgentResponse
from app.schemas.recommendation import CareerRecommendationResponse
from app.schemas.skill_gap import SkillGapResponse

logger = logging.getLogger("careerverse.ai.agents.synthesis_agent")


class SynthesisAgent:
    """
    Final Synthesis Agent.
    Coordinates outputs across all active specialized agents and produces
    a unified, grounded career intelligence response.
    """

    def __init__(
        self,
        aggregator: ContextAggregator = context_aggregator,
        prompt_builder: SynthesisPromptBuilder = synthesis_prompt_builder,
        llm_provider: Optional[ModelProvider] = None,
    ):
        self.aggregator = aggregator
        self.prompt_builder = prompt_builder
        self._llm_provider = llm_provider

    @property
    def llm_provider(self) -> ModelProvider:
        """Lazy load the default LLM provider."""
        if self._llm_provider is None:
            self._llm_provider = get_model_provider()
        return self._llm_provider

    def _parse_llm_json(self, raw_content: str) -> Dict[str, Any]:
        """Safely extracts JSON payload from LLM response with code-block handling, repair, and regex recovery."""
        cleaned = raw_content.strip()

        # Remove markdown code fences if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        if cleaned.endswith("```"):
            cleaned = re.sub(r"\n?```$", "", cleaned)
        cleaned = cleaned.strip()

        # 1. Try direct JSON parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # 2. Try extracting from code block fences in original
        code_blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_content)
        for block in code_blocks:
            try:
                return json.loads(block.strip())
            except json.JSONDecodeError:
                pass

        # 3. Extract substring from first { to last }
        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            candidate = cleaned[first_brace : last_brace + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        # 4. Incremental repair for truncated JSON
        if first_brace != -1:
            snippet = cleaned[first_brace:]
            for i in range(len(snippet) - 1, 0, -1):
                if snippet[i] in ("}", "]"):
                    sub = snippet[: i + 1]
                    for suffix in ["", "}", "]}", '"]}', '"}]}', '"}]}']:
                        try:
                            return json.loads(sub + suffix)
                        except json.JSONDecodeError:
                            pass

        # 5. Regex extraction fallback for summary and final_guidance
        summary_match = re.search(r'"summary"\s*:\s*"([^"]+)"', raw_content)
        guidance_match = re.search(r'"final_guidance"\s*:\s*"([^"]+)"', raw_content)
        if summary_match or guidance_match:
            return {
                "summary": summary_match.group(1) if summary_match else raw_content,
                "final_guidance": guidance_match.group(1) if guidance_match else "Proceed with targeted skill development.",
            }

        raise ValueError(f"Failed to parse valid JSON from LLM response: {raw_content[:200]}...")

    def synthesize(
        self,
        candidate_id: int,
        query: str,
        target_role: Optional[str] = None,
        tasks: Optional[List[str]] = None,
        recommendation_response: Optional[CareerRecommendationResponse] = None,
        evaluation_response: Optional[SkillGapResponse] = None,
        interview_response: Optional[InterviewResponse] = None,
        agent_results: Optional[Dict[str, Any]] = None,
        errors: Optional[List[str]] = None,
        language: str = "en",
        language_metadata: Optional[Any] = None,
        temperature: float = 0.2,
    ) -> MultiAgentResponse:
        """
        Executes multi-agent synthesis:
        1. Context Aggregation
        2. Status & Partial-failure analysis
        3. Synthesis Prompt Construction & LLM generation in requested language
        4. Structured MultiAgentResponse assembly
        """
        logger.info(
            "Synthesis Agent: Synthesizing multi-agent results for Candidate ID %d, Language: '%s', Tasks: %s",
            candidate_id,
            language,
            tasks,
        )

        accumulated_errors = list(errors or [])
        active_agent_results = dict(agent_results or {})
        executed_agents: List[str] = []

        # Track executed agents and detect failures
        has_partial_failure = False
        has_invalid_role = False

        if recommendation_response is not None:
            executed_agents.append("recommendation")
            if recommendation_response.status == "failed" or recommendation_response.errors:
                if recommendation_response.status == "failed":
                    has_partial_failure = True
            if "recommendation" not in active_agent_results:
                active_agent_results["recommendation"] = AgentExecutionResult(
                    agent_name="recommendation",
                    status="success" if recommendation_response.status == "completed" else recommendation_response.status,
                    result_summary=recommendation_response.explanation[:100] if recommendation_response.explanation else None,
                    errors=recommendation_response.errors,
                )

        if evaluation_response is not None:
            executed_agents.append("evaluation")
            if evaluation_response.status == "invalid_role":
                has_invalid_role = True
            elif evaluation_response.status == "failed" or evaluation_response.errors:
                if evaluation_response.status == "failed":
                    has_partial_failure = True
            if "evaluation" not in active_agent_results:
                active_agent_results["evaluation"] = AgentExecutionResult(
                    agent_name="evaluation",
                    status="success" if evaluation_response.status == "completed" else evaluation_response.status,
                    result_summary=evaluation_response.summary[:100] if evaluation_response.summary else None,
                    errors=evaluation_response.errors,
                )

        if interview_response is not None:
            executed_agents.append("interview")
            if interview_response.status == "invalid_role":
                has_invalid_role = True
            elif interview_response.status == "failed" or (interview_response.errors and not interview_response.questions):
                if interview_response.status == "failed":
                    has_partial_failure = True
            if "interview" not in active_agent_results:
                active_agent_results["interview"] = AgentExecutionResult(
                    agent_name="interview",
                    status="success" if interview_response.status == "completed" else interview_response.status,
                    result_summary=interview_response.preparation_summary[:100] if interview_response.preparation_summary else None,
                    errors=interview_response.errors,
                )

        # Check active_agent_results for failed or partial status across all tracked agents
        for agent_name, agent_res in active_agent_results.items():
            st = getattr(agent_res, "status", None) if hasattr(agent_res, "status") else (agent_res.get("status") if isinstance(agent_res, dict) else None)
            if st == "failed":
                has_partial_failure = True

        # Check if tasks were explicitly requested but any recorded failure
        if tasks:
            for t in tasks:
                if t in active_agent_results:
                    res_val = active_agent_results[t]
                    st = getattr(res_val, "status", None) if hasattr(res_val, "status") else (res_val.get("status") if isinstance(res_val, dict) else None)
                    if st == "failed":
                        has_partial_failure = True

        # 1. Aggregate Context
        aggregated = self.aggregator.aggregate(
            candidate_id=candidate_id,
            user_query=query,
            target_role=target_role,
            tasks=tasks,
            recommendation_response=recommendation_response,
            evaluation_response=evaluation_response,
            interview_response=interview_response,
            agent_results=active_agent_results,
            errors=accumulated_errors,
        )

        # Determine overall status
        if candidate_id <= 0 or not query.strip():
            overall_status = "validation_failed"
        elif has_invalid_role and not (recommendation_response and recommendation_response.recommendations):
            overall_status = "invalid_role"
        elif has_partial_failure:
            overall_status = "partial"
        else:
            overall_status = "completed"

        # If invalid candidate or empty query, return early without LLM call
        if overall_status == "validation_failed":
            return MultiAgentResponse(
                candidate_id=candidate_id,
                query=query,
                language=language,
                language_metadata=language_metadata,
                target_role=target_role,
                agents_used=executed_agents,
                summary=f"Validation failed: {'; '.join(accumulated_errors)}",
                recommendations=[],
                skill_gaps=[],
                interview_preparation=[],
                final_guidance="",
                evidence={},
                agent_results=active_agent_results,
                model_name=None,
                status=overall_status,
                errors=accumulated_errors,
            )

        # 2. Build synthesis or compose single-agent response
        model_name = None
        if len(executed_agents) <= 1:
            # Single-agent fast path: reuse specialized agent output directly
            summary_parts = []
            guidance_parts = []

            if recommendation_response:
                rec_parts = []
                if recommendation_response.explanation:
                    rec_parts.append(recommendation_response.explanation)
                if recommendation_response.recommendations:
                    for r in recommendation_response.recommendations:
                        rationale_text = r.rationale if r.rationale else ""
                        skills_text = f"**Skills:** {', '.join(r.supporting_skills)}" if r.supporting_skills else ""
                        rec_parts.append(f"### {r.title} ({r.category})\n{rationale_text}\n{skills_text}".strip())

                combined_rec = "\n\n".join(rec_parts) if rec_parts else (recommendation_response.explanation or "Career recommendations generated.")
                summary_parts.append(combined_rec)

                if language == "ta":
                    guidance_parts.append("மேற்கண்ட பரிந்துரைகளை அடிப்படையாகக் கொண்டு உங்கள் திறன்களை மேலும் மேம்படுத்துங்கள்.")
                elif language == "hi":
                    guidance_parts.append("उपरोक्त सिफारिशों के आधार पर अपने करियर कौशल को और बेहतर बनाएं।")
                else:
                    guidance_parts.append("Refer to the career recommendations above based on candidate verified profile.")

            elif evaluation_response and evaluation_response.summary:
                summary_parts.append(evaluation_response.summary)
                gap_count = len(evaluation_response.skill_gaps)
                target_name = target_role or "the target role"
                if language == "ta":
                    guidance_parts.append(f"{target_name} பணிக்கான {gap_count} திறன் இடைவெளிகளை நிரப்ப பயிற்சி செய்யுங்கள்.")
                elif language == "hi":
                    guidance_parts.append(f"{target_name} पद के लिए पहचाने गए {gap_count} कौशल अंतरालों को पूरा करने पर ध्यान दें।")
                else:
                    guidance_parts.append(f"Focus on addressing the {gap_count} identified skill gap(s) for {target_name}.")

            elif interview_response and interview_response.preparation_summary:
                summary_parts.append(interview_response.preparation_summary)
                q_count = len(interview_response.questions)
                if language == "ta":
                    guidance_parts.append(f"பரிந்துரைக்கப்பட்ட {q_count} நேர்காணல் கேள்விகளை நன்கு பயிற்சி செய்யுங்கள்.")
                elif language == "hi":
                    guidance_parts.append(f"अनुशंसित {q_count} साक्षात्कार प्रश्नों का गहन अभ्यास करें।")
                else:
                    guidance_parts.append(f"Practice the {q_count} targeted interview questions.")

            summary = "\n\n".join(summary_parts) if summary_parts else "Career intelligence analysis completed."
            final_guidance = "\n\n".join(guidance_parts) if guidance_parts else "Proceed with targeted skill development."
            model_name = getattr(recommendation_response or evaluation_response or interview_response, "model_name", None)
        else:
            # Multi-agent synthesis path: synthesize across multiple agents via LLM
            prompt = self.prompt_builder.build_prompt(
                query=query,
                aggregated_context=aggregated,
                language=language,
            )

            try:
                provider_response = self.llm_provider.generate_text(
                    system_prompt=prompt.system_prompt,
                    user_message=prompt.user_message,
                    temperature=temperature,
                )
                raw_output = provider_response.content.strip()
                model_name = provider_response.model

                parsed_json = self._parse_llm_json(raw_output)
                raw_summary = parsed_json.get("summary", "Synthesized multi-agent career intelligence summary.")
                raw_guidance = parsed_json.get("final_guidance", "Actionable unified career guidance.")

                if isinstance(raw_summary, dict):
                    summary = "\n\n".join(f"{k.replace('_', ' ').title()}: {v}" for k, v in raw_summary.items())
                elif isinstance(raw_summary, list):
                    summary = "\n".join(str(item) for item in raw_summary)
                else:
                    summary = str(raw_summary).strip()

                if isinstance(raw_guidance, dict):
                    final_guidance = "\n\n".join(f"{k.replace('_', ' ').title()}: {v}" for k, v in raw_guidance.items())
                elif isinstance(raw_guidance, list):
                    final_guidance = "\n".join(str(item) for item in raw_guidance)
                else:
                    final_guidance = str(raw_guidance).strip()

            except Exception as exc:
                logger.warning("Synthesis Agent LLM call failed or fell back: %s", str(exc))
                summary_parts = []
                guidance_parts = []

                if recommendation_response and (recommendation_response.explanation or recommendation_response.generated_answer):
                    summary_parts.append(f"Career Recommendations: {recommendation_response.explanation or recommendation_response.generated_answer}")
                if evaluation_response and evaluation_response.summary:
                    summary_parts.append(f"Skill Evaluation: {evaluation_response.summary}")
                if interview_response and interview_response.preparation_summary:
                    guidance_parts.append(f"Interview Strategy: {interview_response.preparation_summary}")

                summary = "\n\n".join(summary_parts) if summary_parts else "Career intelligence analysis completed."
                final_guidance = "\n\n".join(guidance_parts) if guidance_parts else "Proceed with targeted skill development and interview preparation."
                accumulated_errors.append(f"Synthesis warning: {str(exc)}")

        # 4. Assemble final structured MultiAgentResponse
        recs_list = recommendation_response.recommendations if recommendation_response else []
        gaps_list = evaluation_response.skill_gaps if evaluation_response else []
        questions_list = interview_response.questions if interview_response else []

        evidence_dict = {
            "candidate_profile": aggregated.get("candidate_profile", {}),
            "retrieval_sources": aggregated.get("retrieval_sources", []),
            "agents_executed": executed_agents,
        }

        return MultiAgentResponse(
            candidate_id=candidate_id,
            query=query,
            language=language,
            language_metadata=language_metadata,
            target_role=target_role,
            agents_used=executed_agents,
            summary=summary,
            recommendations=recs_list,
            recommendation_details=recommendation_response,
            skill_gaps=gaps_list,
            evaluation_details=evaluation_response,
            interview_preparation=questions_list,
            interview_details=interview_response,
            final_guidance=final_guidance,
            evidence=evidence_dict,
            agent_results=active_agent_results,
            model_name=model_name,
            status=overall_status,
            errors=accumulated_errors,
        )


synthesis_agent = SynthesisAgent()
