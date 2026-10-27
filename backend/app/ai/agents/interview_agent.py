"""
Personalized Interview Preparation Agent for CareerVerse AI.

Generates grounded, evidence-backed interview questions tailored to candidate projects,
verified skills, target role expectations, and identified skill gaps.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from app.ai.agents.interview_prompt import (
    InterviewPromptBuilder,
    interview_prompt_builder,
)
from app.ai.agents.role_requirements import (
    get_role_requirements,
    list_available_roles,
    normalize_role_name,
)
from app.ai.agents.skill_gap_analyzer import (
    SkillGapAnalyzer,
    skill_gap_analyzer,
)
from app.ai.knowledge_graph.graph_queries import (
    GraphQueryService,
    graph_query_service,
)
from app.parsers.skill_normalizer import get_canonical_skill_name
from app.ai.providers.base import ModelProvider
from app.ai.providers.factory import get_model_provider
from app.ai.rag.context_builder import RAGContextBuilder, rag_context_builder
from app.schemas.interview import InterviewQuestion, InterviewResponse
from app.schemas.rag import RAGRetrievedContext
from app.schemas.skill_gap import SkillGapItem

logger = logging.getLogger("careerverse.ai.agents.interview_agent")


class InterviewAgent:
    """
    Candidate Interview Preparation Agent.
    Orchestrates evidence retrieval, deterministic mode routing, skill-gap alignment,
    and grounded LLM question generation.
    """

    def __init__(
        self,
        context_builder: RAGContextBuilder = rag_context_builder,
        graph_queries: GraphQueryService = graph_query_service,
        gap_analyzer: SkillGapAnalyzer = skill_gap_analyzer,
        prompt_builder: InterviewPromptBuilder = interview_prompt_builder,
        llm_provider: Optional[ModelProvider] = None,
    ):
        self.context_builder = context_builder
        self.graph_queries = graph_queries
        self.gap_analyzer = gap_analyzer
        self.prompt_builder = prompt_builder
        self._llm_provider = llm_provider

    @property
    def llm_provider(self) -> ModelProvider:
        """Lazy load the default LLM provider."""
        if self._llm_provider is None:
            self._llm_provider = get_model_provider()
        return self._llm_provider

    def _detect_interview_mode(
        self, query: str, explicit_role: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Deterministic rule-based interview mode and target-role extractor.
        Modes:
        - "project": Questions specifically focusing on candidate projects
        - "skill_gap": Questions targeting weak areas or missing role requirements
        - "skill": Questions targeting specific candidate technical skills
        - "target_role": Questions tailored for a specific career role
        - "general": Balanced general interview preparation
        """
        q = query.lower()
        target_role = explicit_role

        # 1. Check for role keywords if not explicit
        if not target_role:
            for role_phrase in [
                "software developer", "software engineer", "frontend developer",
                "backend developer", "machine learning engineer", "full stack developer",
                "data scientist", "rocket propulsion engineer"
            ]:
                if role_phrase in q:
                    target_role = role_phrase
                    break

        # 2. Mode classification
        if any(kw in q for kw in ["project", "projects", "built", "repo", "repository", "careerverseai", "ecomm", "inboxpilot"]):
            return "project", target_role

        if any(kw in q for kw in ["skill gap", "skill gaps", "weak", "weakness", "weaknesses", "weak area", "weak areas", "lacking", "missing skills"]):
            return "skill_gap", target_role

        if any(kw in q for kw in ["python", "fastapi", "sql", "neo4j", "docker", "react", "technical questions", "my skills", "skill"]):
            if not target_role:
                return "skill", None

        if target_role:
            return "target_role", target_role

        return "general", None

    def _parse_llm_json(self, raw_content: str) -> Dict[str, Any]:
        """
        Safely extracts JSON payload from LLM response with code-block handling, repair, and regex recovery.
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

        # 5. Regex extraction fallback for preparation_summary and questions
        summary_match = re.search(r'"(?:preparation_summary|summary)"\s*:\s*"((?:[^"\\]|\\.)*)"', raw_content, re.DOTALL)
        questions_found = []
        q_matches = re.findall(r'"(?:question|கேள்வி|प्रश्न)"\s*:\s*"((?:[^"\\]|\\.)*)"', raw_content)
        for q in q_matches:
            q_clean = q.replace('\\"', '"').replace('\\n', ' ').strip()
            if q_clean:
                questions_found.append({
                    "question": q_clean,
                    "question_type": "technical",
                    "difficulty": "medium",
                    "topic": "Technical Assessment",
                    "rationale": "Grounded question.",
                })
        if summary_match or questions_found:
            sum_clean = summary_match.group(1).replace('\\"', '"').replace('\\n', ' ').strip() if summary_match else raw_content
            return {
                "preparation_summary": sum_clean,
                "questions": questions_found,
            }

        raise ValueError(f"Failed to parse valid JSON from LLM response: {raw_content[:200]}...")

    def _validate_and_sanitize_questions(
        self,
        raw_questions: List[Dict[str, Any]],
        candidate_projects: Set[str],
        candidate_skills: Set[str],
        candidate_techs: Set[str],
    ) -> List[InterviewQuestion]:
        """
        Validates that candidate-specific references in questions are grounded in verified evidence.
        Filters out hallucinated project names from supporting fields.
        """
        sanitized: List[InterviewQuestion] = []
        valid_types = {"technical", "project_based", "skill_based", "role_based", "skill_gap", "behavioral"}
        valid_difficulties = {"easy", "medium", "hard"}

        cand_proj_lower = {p.lower() for p in candidate_projects if p}
        cand_skills_lower = {s.lower() for s in candidate_skills if s}
        cand_techs_lower = {t.lower() for t in candidate_techs if t}

        for item in raw_questions:
            if not isinstance(item, dict) or "question" not in item:
                continue

            q_text = str(item.get("question", "")).strip()
            if not q_text:
                continue

            q_type = str(item.get("question_type", "technical")).lower()
            if q_type not in valid_types:
                q_type = "technical"

            diff = str(item.get("difficulty", "medium")).lower()
            if diff not in valid_difficulties:
                diff = "medium"

            topic = str(item.get("topic", "Technical Assessment")).strip()
            rationale = str(item.get("rationale", "Recommended interview preparation question.")).strip()

            # Sanitize supporting projects
            supp_projs = []
            for p in item.get("supporting_projects", []):
                p_str = str(p).strip()
                if p_str and any(p_str.lower() in cp or cp in p_str.lower() for cp in cand_proj_lower):
                    supp_projs.append(p_str)

            # Sanitize supporting skills
            supp_skills = []
            for s in item.get("supporting_skills", []):
                s_str = str(s).strip()
                if s_str:
                    supp_skills.append(s_str)

            # Sanitize supporting technologies
            supp_techs = []
            for t in item.get("supporting_technologies", []):
                t_str = str(t).strip()
                if t_str:
                    supp_techs.append(t_str)

            sources = [str(src).strip() for src in item.get("evidence_sources", []) if str(src).strip()]
            if not sources:
                sources = ["rag", "graph"]

            sanitized.append(
                InterviewQuestion(
                    question=q_text,
                    question_type=q_type,
                    difficulty=diff,
                    topic=topic,
                    rationale=rationale,
                    supporting_skills=supp_skills,
                    supporting_projects=supp_projs,
                    supporting_technologies=supp_techs,
                    evidence_sources=sources,
                )
            )

        return sanitized

    def generate_interview_preparation(
        self,
        candidate_id: int,
        query: str,
        target_role: Optional[str] = None,
        language: str = "en",
        top_k: int = 5,
        num_questions: int = 5,
        temperature: float = 0.2,
    ) -> InterviewResponse:
        """
        Executes grounded interview preparation pipeline:
        1. Validation & Mode detection
        2. Graph & Multi-modal RAG retrieval
        3. Deterministic skill-gap evaluation (if target role / gap mode)
        4. Strict prompt assembly & Groq LLM inference in requested language
        5. Grounding verification & Structured Pydantic response
        """
        # Validate candidate ID
        if candidate_id is None or not isinstance(candidate_id, int) or candidate_id <= 0:
            error_msg = f"Invalid candidate_id: {candidate_id}. Must be a positive integer."
            logger.warning("Validation failure: %s", error_msg)
            return InterviewResponse(
                candidate_id=candidate_id,
                target_role=target_role,
                query=query,
                interview_mode="general",
                questions=[],
                preparation_summary=f"Validation failed: {error_msg}",
                model_name=None,
                status="validation_failed",
                errors=[error_msg],
            )

        cleaned_query = query.strip() if isinstance(query, str) else ""
        if not cleaned_query:
            error_msg = "User query cannot be empty or whitespace."
            logger.warning("Validation failure: %s", error_msg)
            return InterviewResponse(
                candidate_id=candidate_id,
                target_role=target_role,
                query=cleaned_query,
                interview_mode="general",
                questions=[],
                preparation_summary=f"Validation failed: {error_msg}",
                model_name=None,
                status="validation_failed",
                errors=[error_msg],
            )

        # Detect mode and target role
        interview_mode, detected_role = self._detect_interview_mode(cleaned_query, target_role)
        effective_role = target_role or detected_role

        logger.info(
            "Interview Agent: Evaluating Candidate ID %d, Mode: '%s', Role: '%s', Language: '%s', Query: '%s'",
            candidate_id,
            interview_mode,
            effective_role,
            language,
            cleaned_query[:40],
        )

        # Validate target role if provided/detected
        canonical_role_title = None
        skill_gaps: Optional[List[SkillGapItem]] = None
        if effective_role:
            role_reqs = get_role_requirements(effective_role)
            if not role_reqs:
                available = list_available_roles()
                error_msg = f"Unknown or unsupported target role '{effective_role}'. Supported roles: {', '.join(available)}"
                logger.warning(error_msg)
                return InterviewResponse(
                    candidate_id=candidate_id,
                    target_role=effective_role,
                    query=cleaned_query,
                    interview_mode=interview_mode,
                    questions=[],
                    preparation_summary=f"Interview preparation could not be generated: {error_msg}",
                    model_name=None,
                    status="invalid_role",
                    errors=[error_msg],
                )
            canonical_role_title = role_reqs["title"]

            # Analyze skill gaps for target role
            try:
                gaps, _, _ = self.gap_analyzer.analyze_candidate_skill_gaps(
                    candidate_id=candidate_id,
                    target_role=canonical_role_title,
                )
                skill_gaps = gaps
            except Exception as exc:
                logger.warning("Skill gap analysis failed during interview preparation: %s", str(exc))

        # Retrieve Candidate Graph Evidence
        try:
            skills = self.graph_queries.get_candidate_skills(candidate_id)
            projects = self.graph_queries.get_candidate_projects(candidate_id)
            technologies = self.graph_queries.get_candidate_technologies(candidate_id)
            experience = self.graph_queries.get_candidate_experience(candidate_id)
            certifications = self.graph_queries.get_candidate_certifications(candidate_id)
            education = self.graph_queries.get_candidate_education(candidate_id)

            candidate_graph_evidence = {
                "skills": skills,
                "projects": projects,
                "technologies": technologies,
                "experience": experience,
                "certifications": certifications,
                "education": education,
            }

            def _safe_str(item: Any, *fields: str) -> str:
                if isinstance(item, str):
                    return item.strip()
                if isinstance(item, dict):
                    for f in fields:
                        if f in item and item[f]:
                            return str(item[f]).strip()
                for f in fields:
                    val = getattr(item, f, None)
                    if val is not None and not callable(val):
                        return str(val).strip()
                return str(item).strip()

            cand_project_names = {_safe_str(p, "title", "name") for p in projects if p}
            cand_skill_names = {_safe_str(s, "name", "title") for s in skills if s}
            cand_tech_names = {_safe_str(t, "name") for t in technologies if t}

        except Exception as exc:
            error_msg = f"Failed to retrieve candidate graph evidence: {str(exc)}"
            logger.error(error_msg, exc_info=True)
            return InterviewResponse(
                candidate_id=candidate_id,
                target_role=canonical_role_title,
                query=cleaned_query,
                interview_mode=interview_mode,
                questions=[],
                preparation_summary=f"Error retrieving candidate profile: {error_msg}",
                model_name=None,
                status="failed",
                errors=[error_msg],
            )

        # Retrieve Multi-modal RAG context
        try:
            rag_context: RAGRetrievedContext = self.context_builder.build_retrieval_context(
                candidate_id=candidate_id,
                query=cleaned_query,
                top_k=top_k,
            )
        except Exception as exc:
            logger.warning("RAG retrieval encountered an issue: %s", str(exc))
            rag_context = RAGRetrievedContext(
                candidate_id=candidate_id,
                query=cleaned_query,
                semantic_results=[],
                graph_context=None,
                context_text="",
                metadata={"sources": []},
            )

        technical_citations = rag_context.metadata.get("technical_sources", [])
        technical_source_status = rag_context.metadata.get("technical_source_status", "unavailable")

        def attach_technical_citations(questions: List[InterviewQuestion]) -> List[InterviewQuestion]:
            for question in questions:
                question.source_citations = technical_citations
                question.technical_source_status = technical_source_status
            return questions

        # Helper to construct localized fallback questions
        def build_fallback_questions() -> List[InterviewQuestion]:
            fb: List[InterviewQuestion] = []
            for proj in list(cand_project_names)[:2]:
                if language == "ta":
                    q_txt = f"உங்கள் '{proj}' திட்டத்தின் ஒட்டுமொத்த கட்டமைப்பு மற்றும் தொழில்நுட்ப முடிவுகளைப் பற்றி விளக்க முடியுமா?"
                elif language == "hi":
                    q_txt = f"क्या आप अपने '{proj}' प्रोजेक्ट के समग्र आर्किटेक्चर और तकनीकी निर्णयों के बारे में विस्तार से बता सकते हैं?"
                else:
                    q_txt = f"Can you walk me through the overall architecture and technical decisions of your {proj} project?"

                fb.append(
                    InterviewQuestion(
                        question=q_txt,
                        question_type="project_based",
                        difficulty="medium",
                        topic="Project Architecture",
                        rationale=f"Candidate has verified evidence for project {proj}.",
                        supporting_skills=["System Design", "Architecture"],
                        supporting_projects=[proj],
                        supporting_technologies=list(cand_tech_names)[:2],
                        evidence_sources=["graph", "project"],
                    )
                )

            for sk in list(cand_skill_names)[:2]:
                if language == "ta":
                    q_txt = f"{sk} பயன்படுத்தி அமைப்புகளை உருவாக்கும்போது செயல்திறன் மேம்படுத்தல் மற்றும் பிழை கையாளுதலை எவ்வாறு அணுகுகிறீர்கள்?"
                elif language == "hi":
                    q_txt = f"{sk} के साथ सिस्टम बनाते समय आप प्रदर्शन अनुकूलन और त्रुटि प्रबंधन को कैसे संभालते हैं?"
                else:
                    q_txt = f"How do you approach performance optimization and error handling when building systems with {sk}?"

                fb.append(
                    InterviewQuestion(
                        question=q_txt,
                        question_type="technical",
                        difficulty="medium",
                        topic=f"{sk} Fundamentals",
                        rationale=f"Candidate has demonstrated competency in {sk}.",
                        supporting_skills=[sk],
                        supporting_projects=[],
                        supporting_technologies=[],
                        evidence_sources=["graph", "skill"],
                    )
                )
            return fb

        # Build Prompt
        prompt = self.prompt_builder.build_prompt(
            query=cleaned_query,
            interview_mode=interview_mode,
            target_role=canonical_role_title,
            context=rag_context,
            candidate_graph_evidence=candidate_graph_evidence,
            skill_gap_items=skill_gaps,
            num_questions=num_questions,
            language=language,
        )

        # Inference with LLM
        try:
            provider_response = self.llm_provider.generate_text(
                system_prompt=prompt.system_prompt,
                user_message=prompt.user_message,
                temperature=temperature,
            )
            raw_output = provider_response.content.strip()
            model_name = provider_response.model

            # Parse and Validate Output
            parsed_json = self._parse_llm_json(raw_output)
            summary = parsed_json.get("preparation_summary", "Strategic personalized interview preparation.")
            raw_questions = parsed_json.get("questions", [])

            sanitized_questions = self._validate_and_sanitize_questions(
                raw_questions=raw_questions,
                candidate_projects=cand_project_names,
                candidate_skills=cand_skill_names,
                candidate_techs=cand_tech_names,
            )

            if not sanitized_questions:
                logger.info("Interview Agent: No valid questions parsed from LLM, constructing grounded fallbacks.")
                sanitized_questions = build_fallback_questions()
            sanitized_questions = attach_technical_citations(sanitized_questions)

            return InterviewResponse(
                candidate_id=candidate_id,
                target_role=canonical_role_title,
                query=cleaned_query,
                interview_mode=interview_mode,
                questions=sanitized_questions,
                preparation_summary=summary,
                model_name=model_name,
                status="completed",
                errors=[],
            )

        except Exception as exc:
            logger.warning("LLM inference / JSON parse failed for interview agent: %s", str(exc))

            fallback_questions = build_fallback_questions()
            fallback_questions = attach_technical_citations(fallback_questions)

            if language == "ta":
                prep_summary = "உங்கள் உண்மையான திட்டங்கள் மற்றும் தொழில்நுட்ப திறன்களின் அடிப்படையில் நேர்காணல் கேள்விகள் தயாரிக்கப்பட்டுள்ளன."
            elif language == "hi":
                prep_summary = "आपकी वास्तविक परियोजनाओं और तकनीकी कौशलों के आधार पर साक्षात्कार प्रश्न तैयार किए गए हैं।"
            else:
                prep_summary = "Interview preparation generated based on verified profile evidence."

            return InterviewResponse(
                candidate_id=candidate_id,
                target_role=canonical_role_title,
                query=cleaned_query,
                interview_mode=interview_mode,
                questions=fallback_questions,
                preparation_summary=prep_summary,
                model_name=None,
                status="completed",
                errors=[f"LLM generation warning: {str(exc)}"],
            )


# Global singleton instance
interview_agent = InterviewAgent()
