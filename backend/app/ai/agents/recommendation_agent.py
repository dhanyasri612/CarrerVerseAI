"""
Recommendation Agent for CareerVerse AI.

Provides personalized career role recommendations grounded in candidate multi-modal data.
Reuses existing RAGContextBuilder and GroqProvider.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from app.ai.agents.recommendation_prompt import (
    RecommendationPromptBuilder,
    recommendation_prompt_builder,
)
from app.ai.providers.base import ModelProvider
from app.ai.providers.factory import get_model_provider
from app.ai.rag.context_builder import RAGContextBuilder, rag_context_builder
from app.schemas.rag import RAGRetrievedContext
from app.schemas.recommendation import (
    CareerRecommendationItem,
    CareerRecommendationResponse,
)

logger = logging.getLogger("careerverse.ai.agents.recommendation_agent")


class RecommendationAgent:
    """
    Recommendation Agent specialized in grounded career trajectory analysis.
    Fuses ChromaDB semantic retrieval and Neo4j Knowledge Graph evidence.
    """

    def __init__(
        self,
        context_builder: RAGContextBuilder = rag_context_builder,
        prompt_builder: RecommendationPromptBuilder = recommendation_prompt_builder,
        llm_provider: Optional[ModelProvider] = None,
    ):
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
        Safely extracts and parses JSON payload from LLM output.
        Handles markdown code blocks, truncated JSON, and regex recovery.
        """
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

        # 5. Regex extraction fallback
        recs = []
        titles = re.findall(r'"title"\s*:\s*"([^"]+)"', raw_content)
        categories = re.findall(r'"category"\s*:\s*"([^"]+)"', raw_content)
        rationales = re.findall(r'"rationale"\s*:\s*"([^"]+)"', raw_content)
        for idx, title in enumerate(titles):
            cat = categories[idx] if idx < len(categories) else "Software Engineering"
            rat = rationales[idx] if idx < len(rationales) else ""
            recs.append({"title": title, "category": cat, "rationale": rat})
        if recs:
            return {"recommendations": recs, "explanation": raw_content}

        raise ValueError(f"Failed to parse valid JSON from LLM response: {raw_content[:200]}...")

    def generate_recommendations(
        self,
        candidate_id: int,
        query: str,
        language: str = "en",
        top_k: int = 5,
        temperature: float = 0.2,
    ) -> CareerRecommendationResponse:
        """
        Executes grounded recommendation pipeline:
        1. Multi-modal RAG retrieval (ChromaDB + Neo4j)
        2. Grounded recommendation prompt construction in requested language
        3. Generative inference via Groq provider
        4. Safe JSON parsing and Pydantic validation
        """
        logger.info(
            "Recommendation Agent: Processing for Candidate ID: %d, Language: '%s', Query: '%s'",
            candidate_id,
            language,
            query[:50],
        )

        # 1. Multi-modal retrieval
        context: RAGRetrievedContext = self.context_builder.build_retrieval_context(
            candidate_id=candidate_id,
            query=query,
            top_k=top_k,
        )

        evidence_meta = {
            "sources": context.metadata.get("sources", []),
            "skills_count": context.metadata.get("graph_skills_count", 0),
            "projects_count": context.metadata.get("graph_projects_count", 0),
            "semantic_matches": context.metadata.get("semantic_chunks_count", 0),
        }

        # 2. Prompt construction
        prompt = self.prompt_builder.build_prompt(
            query=query, context=context, language=language
        )

        # 3. LLM generation
        provider_response = self.llm_provider.generate_text(
            system_prompt=prompt.system_prompt,
            user_message=prompt.user_message,
            temperature=temperature,
        )

        raw_output = provider_response.content.strip()
        model_name = provider_response.model

        # 4. Safe parsing & validation
        try:
            parsed_data = self._parse_llm_json(raw_output)
            recommendations_list: List[CareerRecommendationItem] = []

            for item in parsed_data.get("recommendations", []):
                title = (
                    item.get("title")
                    or item.get("career_direction")
                    or item.get("direction")
                    or item.get("career_option")
                    or item.get("role")
                    or item.get("job_title")
                    or item.get("role_title")
                    or item.get("name")
                    or item.get("career_path")
                    or item.get("target_role")
                )
                if not title or title.strip().lower() == "career role":
                    desc_text = (item.get("description") or item.get("rationale") or item.get("recommendation_notes") or "").lower()
                    if "data science" in desc_text or "machine learning" in desc_text:
                        title = "Data Science & Machine Learning"
                    elif "full stack" in desc_text or "frontend" in desc_text:
                        title = "Full Stack Development"
                    elif "ai" in desc_text or "nlp" in desc_text:
                        title = "AI & NLP Systems Engineering"
                    elif "ui/ux" in desc_text or "web development" in desc_text:
                        title = "Web Development & UI/UX"
                    elif "cloud" in desc_text or "devops" in desc_text:
                        title = "Cloud Infrastructure & DevOps"
                    else:
                        title = f"Career Trajectory {len(recommendations_list) + 1}"
                category = item.get("category") or item.get("domain") or "Software Engineering"
                rationale = (
                    item.get("rationale")
                    or item.get("recommendation_notes")
                    or item.get("notes")
                    or item.get("description")
                    or item.get("reason")
                    or item.get("fit_reason")
                    or ""
                )
                supporting_skills = item.get("supporting_skills") or item.get("skills") or []
                supporting_projects = item.get("supporting_projects") or item.get("projects") or []
                supporting_technologies = item.get("supporting_technologies") or item.get("technologies") or []
                supporting_experience = item.get("supporting_experience") or item.get("experience") or []
                confidence = item.get("confidence") or "High (Heuristic)"

                rec = CareerRecommendationItem(
                    title=title,
                    category=category,
                    rationale=rationale,
                    supporting_skills=supporting_skills,
                    supporting_projects=supporting_projects,
                    supporting_technologies=supporting_technologies,
                    supporting_experience=supporting_experience,
                    confidence=confidence,
                )
                recommendations_list.append(rec)

            explanation = parsed_data.get("explanation", raw_output)

            return CareerRecommendationResponse(
                candidate_id=candidate_id,
                query=query,
                recommendations=recommendations_list,
                explanation=explanation,
                evidence=evidence_meta,
                model_name=model_name,
                status="completed",
                errors=[],
            )

        except Exception as parse_err:
            logger.warning(
                "Structured JSON parsing failed for recommendation output, using safe fallback: %s",
                str(parse_err),
            )
            # Safe fallback preserves narrative response without crashing
            return CareerRecommendationResponse(
                candidate_id=candidate_id,
                query=query,
                recommendations=[],
                explanation=raw_output,
                evidence=evidence_meta,
                model_name=model_name,
                status="completed_unstructured",
                errors=[f"Structured parsing warning: {str(parse_err)}"],
            )


# Global singleton instance
recommendation_agent = RecommendationAgent()
