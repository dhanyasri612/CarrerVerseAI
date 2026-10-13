"""
LangGraph Orchestrator for CareerVerse AI Multi-Agent Architecture.

Orchestrates deterministic validation, multi-agent task routing, and execution of:
- Language Detection & Query Normalization
- Recommendation Agent
- Skill-Gap / Evaluation Agent
- Interview Preparation Agent
- Context Aggregator
- Final Synthesis Agent
- Multilingual Response Generation
- General RAG fallback pipeline
"""

import logging
import time
from typing import Any, Dict, List, Literal, Optional, Tuple

from langgraph.graph import END, START, StateGraph

from app.ai.agents.context_aggregator import ContextAggregator, context_aggregator
from app.ai.agents.evaluation_agent import EvaluationAgent, evaluation_agent
from app.ai.agents.interview_agent import InterviewAgent, interview_agent
from app.ai.agents.recommendation_agent import RecommendationAgent, recommendation_agent
from app.ai.agents.role_requirements import get_role_requirements, list_available_roles
from app.ai.agents.state import CareerIntelligenceState
from app.ai.agents.synthesis_agent import SynthesisAgent, synthesis_agent
from app.ai.agents.task_router import TaskRouter, task_router
from app.ai.language.detector import LanguageDetector, language_detector
from app.ai.language.normalizer import QueryNormalizer, query_normalizer
from app.ai.providers.base import ModelProvider
from app.ai.providers.factory import get_model_provider
from app.ai.rag.context_builder import RAGContextBuilder, rag_context_builder
from app.ai.rag.prompt_builder import RAGPromptBuilder, rag_prompt_builder
from app.core.config import DEFAULT_LANGUAGE
from app.schemas.language import MultilingualResponseMetadata
from app.schemas.multi_agent import AgentExecutionResult, MultiAgentResponse
from app.schemas.rag import RAGRetrievedContext

logger = logging.getLogger("careerverse.ai.agents.orchestrator")


class CareerOrchestrator:
    """
    LangGraph-based Multi-Agent Career Orchestrator.
    Coordinates specialized agents through shared state and final synthesis with multilingual support.
    """

    def __init__(
        self,
        context_builder: RAGContextBuilder = rag_context_builder,
        prompt_builder: RAGPromptBuilder = rag_prompt_builder,
        rec_agent: RecommendationAgent = recommendation_agent,
        eval_agent: EvaluationAgent = evaluation_agent,
        interview_agent: InterviewAgent = interview_agent,
        task_router_engine: TaskRouter = task_router,
        aggregator: ContextAggregator = context_aggregator,
        synth_agent: SynthesisAgent = synthesis_agent,
        lang_detector: LanguageDetector = language_detector,
        query_norm: QueryNormalizer = query_normalizer,
        llm_provider: Optional[ModelProvider] = None,
    ):
        self.context_builder = context_builder
        self.prompt_builder = prompt_builder
        self.rec_agent = rec_agent
        self.eval_agent = eval_agent
        self.interview_agent = interview_agent
        self.task_router = task_router_engine
        self.aggregator = aggregator
        self.synth_agent = synth_agent
        self.lang_detector = lang_detector
        self.query_norm = query_norm
        self._llm_provider = llm_provider
        self.app = self._build_graph()

    @property
    def llm_provider(self) -> ModelProvider:
        """Lazy load the default LLM provider."""
        if self._llm_provider is None:
            self._llm_provider = get_model_provider()
        return self._llm_provider

    def request_processor(self, state: CareerIntelligenceState) -> Dict[str, Any]:
        """
        Node 1: Deterministic validation of input parameters and language detection.
        """
        candidate_id = state.get("candidate_id")
        user_query = state.get("user_query", "")
        explicit_target_role = state.get("target_role")
        explicit_language = state.get("response_language")
        errors = list(state.get("errors", []))
        metadata = dict(state.get("metadata", {}))

        logger.info(
            "Node [request_processor]: Candidate ID %s, Query: '%s', Explicit Role: '%s', Explicit Language: '%s'",
            candidate_id,
            str(user_query)[:40],
            explicit_target_role,
            explicit_language,
        )

        # Validate candidate ID
        if candidate_id is None or not isinstance(candidate_id, int) or candidate_id <= 0:
            error_msg = f"Invalid candidate_id: {candidate_id}. Must be a positive integer."
            logger.warning("Validation failure: %s", error_msg)
            errors.append(error_msg)

        # Validate user query
        cleaned_query = user_query.strip() if isinstance(user_query, str) else ""
        if not cleaned_query:
            error_msg = "User query cannot be empty or whitespace."
            logger.warning("Validation failure: %s", error_msg)
            errors.append(error_msg)

        # Language Detection
        det_res = self.lang_detector.detect_language(
            text=cleaned_query,
            explicit_language=explicit_language,
        )

        detected_language = det_res.language_code
        language_name = det_res.language_name
        language_confidence = det_res.confidence
        detection_method = det_res.detection_method

        # Fallback to DEFAULT_LANGUAGE if detected language is not supported
        if det_res.is_supported:
            response_language = detected_language
        else:
            logger.warning(
                "Unsupported language '%s' (%s) detected. Falling back to default '%s'",
                detected_language,
                language_name,
                DEFAULT_LANGUAGE,
            )
            response_language = DEFAULT_LANGUAGE

        # Semantic query normalization for internal routing / search
        normalized_query = self.query_norm.normalize_query(cleaned_query, detected_language)

        lang_metadata = MultilingualResponseMetadata(
            detected_language=detected_language,
            language_name=language_name,
            response_language=response_language,
            confidence=language_confidence,
            detection_method=detection_method,
            original_query=cleaned_query,
            normalized_query=normalized_query if normalized_query != cleaned_query else None,
            is_translated_response=(response_language != "en"),
        )

        metadata["detected_language"] = detected_language
        metadata["response_language"] = response_language
        metadata["language_confidence"] = language_confidence
        metadata["language_detection_method"] = detection_method

        if errors:
            return {
                "candidate_id": candidate_id,
                "user_query": cleaned_query,
                "original_query": cleaned_query,
                "normalized_query": normalized_query,
                "detected_language": detected_language,
                "language_name": language_name,
                "language_confidence": language_confidence,
                "response_language": response_language,
                "language_metadata": lang_metadata,
                "intent": "unknown",
                "tasks": [],
                "status": "validation_failed",
                "errors": errors,
                "metadata": metadata,
                "generated_answer": f"Request processing error: {'; '.join(errors)}",
            }

        metadata["processed_length"] = len(cleaned_query)
        metadata["request_validated"] = True

        return {
            "candidate_id": candidate_id,
            "user_query": cleaned_query,
            "original_query": cleaned_query,
            "normalized_query": normalized_query,
            "detected_language": detected_language,
            "language_name": language_name,
            "language_confidence": language_confidence,
            "response_language": response_language,
            "language_metadata": lang_metadata,
            "target_role": explicit_target_role,
            "status": "validated",
            "errors": errors,
            "metadata": metadata,
        }

    def task_router_node(self, state: CareerIntelligenceState) -> Dict[str, Any]:
        """
        Node 2: Deterministic task routing and role extraction.
        """
        cleaned_query = state["user_query"]
        explicit_role = state.get("target_role")
        metadata = dict(state.get("metadata", {}))

        intent, tasks, target_role = self.task_router.analyze_task(
            query=cleaned_query,
            explicit_role=explicit_role,
        )

        metadata["detected_intent"] = intent
        metadata["planned_tasks"] = tasks
        if target_role:
            metadata["target_role"] = target_role

        logger.info(
            "Node [task_router_node]: Intent '%s', Tasks %s, Role '%s'",
            intent,
            tasks,
            target_role,
        )

        return {
            "intent": intent,
            "tasks": tasks,
            "target_role": target_role,
            "metadata": metadata,
            "agents_used": [],
            "agent_results": {},
        }

    def recommendation_node(self, state: CareerIntelligenceState) -> Dict[str, Any]:
        """
        Specialized Node: Recommendation Agent execution with multilingual generation.
        """
        candidate_id = state["candidate_id"]
        user_query = state["user_query"]
        response_lang = state.get("response_language", "en")
        errors = list(state.get("errors", []))
        metadata = dict(state.get("metadata", {}))
        agent_results = dict(state.get("agent_results", {}))
        agents_used = list(state.get("agents_used", []))

        logger.info(
            "Node [recommendation_node]: Running Recommendation Agent for Candidate ID %d, Language: '%s'",
            candidate_id,
            response_lang,
        )
        start_time = time.time()

        try:
            rec_res = self.rec_agent.generate_recommendations(
                candidate_id=candidate_id,
                query=user_query,
                language=response_lang,
            )
            exec_time = (time.time() - start_time) * 1000

            agents_used.append("recommendation")
            agent_results["recommendation"] = AgentExecutionResult(
                agent_name="recommendation",
                status="success" if rec_res.status == "completed" else rec_res.status,
                execution_time_ms=exec_time,
                result_summary=f"{len(rec_res.recommendations)} roles recommended",
                errors=rec_res.errors,
            )

            metadata["recommendation_model"] = rec_res.model_name
            metadata["recommendations_count"] = len(rec_res.recommendations)

            current_target = state.get("target_role")

            return {
                "recommendation_response": rec_res,
                "target_role": current_target,
                "generated_answer": rec_res.explanation,
                "model_name": rec_res.model_name,
                "retrieval_metadata": rec_res.evidence,
                "agent_results": agent_results,
                "agents_used": agents_used,
                "metadata": metadata,
                "errors": errors + rec_res.errors,
            }
        except Exception as exc:
            exec_time = (time.time() - start_time) * 1000
            error_msg = f"Recommendation Agent failed: {str(exc)}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
            agent_results["recommendation"] = AgentExecutionResult(
                agent_name="recommendation",
                status="failed",
                execution_time_ms=exec_time,
                result_summary=None,
                errors=[error_msg],
            )
            return {
                "agent_results": agent_results,
                "agents_used": agents_used,
                "errors": errors,
            }

    def evaluation_node(self, state: CareerIntelligenceState) -> Dict[str, Any]:
        """
        Specialized Node: Skill-Gap / Evaluation Agent execution with multilingual generation.
        """
        candidate_id = state["candidate_id"]
        user_query = state.get("user_query", "")
        response_lang = state.get("response_language", "en")
        target_role = state.get("target_role")

        errors = list(state.get("errors", []))
        metadata = dict(state.get("metadata", {}))
        agent_results = dict(state.get("agent_results", {}))
        agents_used = list(state.get("agents_used", []))

        logger.info(
            "Node [evaluation_node]: Running Evaluation Agent for Candidate ID %d, Target Role: '%s', Language: '%s'",
            candidate_id,
            target_role,
            response_lang,
        )
        start_time = time.time()

        try:
            eval_res = self.eval_agent.evaluate_skill_gaps(
                candidate_id=candidate_id,
                target_role=target_role,
                query=user_query,
                language=response_lang,
            )
            exec_time = (time.time() - start_time) * 1000

            agents_used.append("evaluation")
            agent_status = "success" if eval_res.status == "completed" else eval_res.status
            agent_results["evaluation"] = AgentExecutionResult(
                agent_name="evaluation",
                status=agent_status,
                execution_time_ms=exec_time,
                result_summary=(
                    f"{len(eval_res.strengths)} strengths, {len(eval_res.skill_gaps)} gaps"
                    if eval_res.status == "completed"
                    else eval_res.summary[:100]
                ),
                errors=eval_res.errors,
            )

            metadata["evaluation_model"] = eval_res.model_name
            if eval_res.target_role:
                metadata["target_role"] = eval_res.target_role
            metadata["strengths_count"] = len(eval_res.strengths)
            metadata["gaps_count"] = len(eval_res.skill_gaps)

            return {
                "evaluation_response": eval_res,
                "target_role": eval_res.target_role or target_role,
                "generated_answer": eval_res.summary,
                "model_name": eval_res.model_name,
                "agent_results": agent_results,
                "agents_used": agents_used,
                "metadata": metadata,
                "errors": errors + eval_res.errors,
            }
        except Exception as exc:
            exec_time = (time.time() - start_time) * 1000
            error_msg = f"Evaluation Agent failed: {str(exc)}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
            agent_results["evaluation"] = AgentExecutionResult(
                agent_name="evaluation",
                status="failed",
                execution_time_ms=exec_time,
                result_summary=None,
                errors=[error_msg],
            )
            return {
                "agent_results": agent_results,
                "agents_used": agents_used,
                "errors": errors,
            }

    def interview_node(self, state: CareerIntelligenceState) -> Dict[str, Any]:
        """
        Specialized Node: Interview Preparation Agent execution with multilingual generation.
        """
        candidate_id = state["candidate_id"]
        user_query = state["user_query"]
        response_lang = state.get("response_language", "en")
        target_role = state.get("target_role")
        errors = list(state.get("errors", []))
        metadata = dict(state.get("metadata", {}))
        agent_results = dict(state.get("agent_results", {}))
        agents_used = list(state.get("agents_used", []))

        logger.info(
            "Node [interview_node]: Running Interview Agent for Candidate ID %d, Target Role: '%s', Language: '%s'",
            candidate_id,
            target_role,
            response_lang,
        )
        start_time = time.time()

        try:
            int_res = self.interview_agent.generate_interview_preparation(
                candidate_id=candidate_id,
                query=user_query,
                target_role=target_role,
                language=response_lang,
            )
            exec_time = (time.time() - start_time) * 1000

            agents_used.append("interview")
            agent_results["interview"] = AgentExecutionResult(
                agent_name="interview",
                status="success" if int_res.status == "completed" else int_res.status,
                execution_time_ms=exec_time,
                result_summary=f"{len(int_res.questions)} questions generated",
                errors=int_res.errors,
            )

            metadata["interview_model"] = int_res.model_name
            metadata["interview_mode"] = int_res.interview_mode
            metadata["questions_count"] = len(int_res.questions)

            return {
                "interview_response": int_res,
                "generated_answer": int_res.preparation_summary,
                "model_name": int_res.model_name,
                "agent_results": agent_results,
                "agents_used": agents_used,
                "metadata": metadata,
                "errors": errors + int_res.errors,
            }
        except Exception as exc:
            exec_time = (time.time() - start_time) * 1000
            error_msg = f"Interview Agent failed: {str(exc)}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
            agent_results["interview"] = AgentExecutionResult(
                agent_name="interview",
                status="failed",
                execution_time_ms=exec_time,
                result_summary=None,
                errors=[error_msg],
            )
            return {
                "agent_results": agent_results,
                "agents_used": agents_used,
                "errors": errors,
            }

    def context_aggregator_node(self, state: CareerIntelligenceState) -> Dict[str, Any]:
        """
        Node: Combines candidate context and specialized agent outputs into aggregated context.
        """
        candidate_id = state["candidate_id"]
        user_query = state["user_query"]
        target_role = state.get("target_role")
        tasks = state.get("tasks", [])
        rec_res = state.get("recommendation_response")
        eval_res = state.get("evaluation_response")
        int_res = state.get("interview_response")
        agent_results = state.get("agent_results", {})
        errors = state.get("errors", [])
        retrieved_context = state.get("retrieved_context")

        logger.info("Node [context_aggregator_node]: Aggregating outputs for Candidate ID %d", candidate_id)

        aggregated = self.aggregator.aggregate(
            candidate_id=candidate_id,
            user_query=user_query,
            target_role=target_role,
            tasks=tasks,
            recommendation_response=rec_res,
            evaluation_response=eval_res,
            interview_response=int_res,
            agent_results=agent_results,
            retrieved_context=retrieved_context,
            errors=errors,
        )

        return {
            "aggregated_context": aggregated,
        }

    def synthesis_node(self, state: CareerIntelligenceState) -> Dict[str, Any]:
        """
        Node: Final Synthesis Agent synthesizing all findings into MultiAgentResponse.
        """
        candidate_id = state["candidate_id"]
        user_query = state["user_query"]
        target_role = state.get("target_role")
        response_lang = state.get("response_language", "en")
        lang_metadata = state.get("language_metadata")
        tasks = state.get("tasks", [])
        rec_res = state.get("recommendation_response")
        eval_res = state.get("evaluation_response")
        int_res = state.get("interview_response")
        agent_results = state.get("agent_results", {})
        errors = list(state.get("errors", []))
        metadata = dict(state.get("metadata", {}))

        logger.info(
            "Node [synthesis_node]: Synthesizing response for Candidate ID %d in language '%s'",
            candidate_id,
            response_lang,
        )

        multi_res = self.synth_agent.synthesize(
            candidate_id=candidate_id,
            query=user_query,
            target_role=target_role,
            tasks=tasks,
            recommendation_response=rec_res,
            evaluation_response=eval_res,
            interview_response=int_res,
            agent_results=agent_results,
            errors=errors,
            language=response_lang,
            language_metadata=lang_metadata,
        )

        metadata["synthesis_model"] = multi_res.model_name
        metadata["agents_used"] = multi_res.agents_used

        # Combine answers into unified narrative
        unified_answer = f"{multi_res.summary}\n\n{multi_res.final_guidance}".strip()

        return {
            "multi_agent_response": multi_res,
            "generated_answer": unified_answer,
            "status": multi_res.status,
            "model_name": multi_res.model_name,
            "metadata": metadata,
            "errors": multi_res.errors,
        }

    def rag_retrieval(self, state: CareerIntelligenceState) -> Dict[str, Any]:
        """
        General RAG Node: Multi-modal retrieval fusing ChromaDB & Neo4j KG.
        """
        candidate_id = state["candidate_id"]
        user_query = state["user_query"]
        normalized_query = state.get("normalized_query") or user_query
        errors = list(state.get("errors", []))
        metadata = dict(state.get("metadata", {}))

        logger.info("Node [rag_retrieval]: Executing RAG retrieval for Candidate ID %d", candidate_id)

        try:
            # For optimal semantic vector retrieval, use normalized query when available
            context: RAGRetrievedContext = self.context_builder.build_retrieval_context(
                candidate_id=candidate_id,
                query=normalized_query,
                top_k=5,
            )

            metadata["retrieval_sources"] = list(context.metadata.get("sources", []))
            metadata["semantic_chunks_count"] = context.metadata.get("semantic_chunks_count", 0)
            metadata["graph_skills_count"] = context.metadata.get("graph_skills_count", 0)
            metadata["graph_projects_count"] = context.metadata.get("graph_projects_count", 0)

            return {
                "retrieved_context": context,
                "retrieval_metadata": context.metadata,
                "status": "retrieved",
                "metadata": metadata,
            }
        except Exception as exc:
            error_msg = f"RAG retrieval failed: {str(exc)}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
            return {
                "status": "retrieval_failed",
                "errors": errors,
                "metadata": metadata,
                "generated_answer": f"Retrieval error: {error_msg}",
            }

    def response_generation(self, state: CareerIntelligenceState) -> Dict[str, Any]:
        """
        General Generation Node: Grounded generative answer synthesis using Groq LLM in response language.
        """
        candidate_id = state["candidate_id"]
        user_query = state["user_query"]
        response_lang = state.get("response_language", "en")
        context = state.get("retrieved_context")
        errors = list(state.get("errors", []))
        metadata = dict(state.get("metadata", {}))

        logger.info(
            "Node [response_generation]: Generating grounded response for Candidate ID %d in language '%s'",
            candidate_id,
            response_lang,
        )

        if not context:
            error_msg = "Cannot generate response: Retrieved context is missing."
            logger.warning(error_msg)
            errors.append(error_msg)
            return {
                "status": "generation_failed",
                "errors": errors,
                "generated_answer": "Unable to generate an answer because retrieval context is not available.",
            }

        try:
            prompt = self.prompt_builder.build_prompt(
                query=user_query, context=context, language=response_lang
            )
            provider_response = self.llm_provider.generate_text(
                system_prompt=prompt.system_prompt,
                user_message=prompt.user_message,
                temperature=0.2,
            )

            answer = provider_response.content.strip()
            model_name = provider_response.model

            metadata["model_name"] = model_name
            metadata["prompt_length"] = len(prompt.user_message)
            metadata["answer_length"] = len(answer)

            return {
                "generated_answer": answer,
                "model_name": model_name,
                "status": "completed",
                "metadata": metadata,
            }
        except Exception as exc:
            error_msg = f"Response generation failed: {str(exc)}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
            return {
                "status": "generation_failed",
                "errors": errors,
                "generated_answer": f"Generation error: {error_msg}",
            }

    # ----------------------------------------------------
    # Graph Routing Logic
    # ----------------------------------------------------

    def _route_after_request_processor(
        self, state: CareerIntelligenceState
    ) -> Literal["task_router_node", "__end__"]:
        if state.get("errors"):
            return "__end__"
        return "task_router_node"

    def _route_after_task_router(
        self, state: CareerIntelligenceState
    ) -> Literal["recommendation_node", "evaluation_node", "interview_node", "rag_retrieval", "__end__"]:
        if state.get("errors"):
            return "__end__"
        tasks = state.get("tasks", [])
        if "recommendation" in tasks:
            return "recommendation_node"
        if "evaluation" in tasks:
            return "evaluation_node"
        if "interview" in tasks:
            return "interview_node"
        return "rag_retrieval"

    def _route_after_recommendation_node(
        self, state: CareerIntelligenceState
    ) -> Literal["evaluation_node", "interview_node", "context_aggregator_node"]:
        tasks = state.get("tasks", [])
        if "evaluation" in tasks:
            return "evaluation_node"
        if "interview" in tasks:
            return "interview_node"
        return "context_aggregator_node"

    def _route_after_evaluation_node(
        self, state: CareerIntelligenceState
    ) -> Literal["interview_node", "context_aggregator_node"]:
        tasks = state.get("tasks", [])
        if "interview" in tasks:
            return "interview_node"
        return "context_aggregator_node"

    def _route_after_interview_node(
        self, state: CareerIntelligenceState
    ) -> Literal["context_aggregator_node"]:
        return "context_aggregator_node"

    def _route_after_rag_retrieval(
        self, state: CareerIntelligenceState
    ) -> Literal["response_generation", "__end__"]:
        if state.get("errors"):
            return "__end__"
        return "response_generation"

    def _build_graph(self):
        """Constructs and compiles the StateGraph workflow with multi-agent coordination."""
        workflow = StateGraph(CareerIntelligenceState)

        # Register nodes
        workflow.add_node("request_processor", self.request_processor)
        workflow.add_node("task_router_node", self.task_router_node)
        workflow.add_node("recommendation_node", self.recommendation_node)
        workflow.add_node("evaluation_node", self.evaluation_node)
        workflow.add_node("interview_node", self.interview_node)
        workflow.add_node("context_aggregator_node", self.context_aggregator_node)
        workflow.add_node("synthesis_node", self.synthesis_node)
        workflow.add_node("rag_retrieval", self.rag_retrieval)
        workflow.add_node("response_generation", self.response_generation)

        # Wire edges
        workflow.add_edge(START, "request_processor")
        workflow.add_conditional_edges(
            "request_processor",
            self._route_after_request_processor,
            {
                "task_router_node": "task_router_node",
                "__end__": END,
            },
        )
        workflow.add_conditional_edges(
            "task_router_node",
            self._route_after_task_router,
            {
                "recommendation_node": "recommendation_node",
                "evaluation_node": "evaluation_node",
                "interview_node": "interview_node",
                "rag_retrieval": "rag_retrieval",
                "__end__": END,
            },
        )
        workflow.add_conditional_edges(
            "recommendation_node",
            self._route_after_recommendation_node,
            {
                "evaluation_node": "evaluation_node",
                "interview_node": "interview_node",
                "context_aggregator_node": "context_aggregator_node",
            },
        )
        workflow.add_conditional_edges(
            "evaluation_node",
            self._route_after_evaluation_node,
            {
                "interview_node": "interview_node",
                "context_aggregator_node": "context_aggregator_node",
            },
        )
        workflow.add_conditional_edges(
            "interview_node",
            self._route_after_interview_node,
            {
                "context_aggregator_node": "context_aggregator_node",
            },
        )
        workflow.add_edge("context_aggregator_node", "synthesis_node")
        workflow.add_edge("synthesis_node", END)

        workflow.add_conditional_edges(
            "rag_retrieval",
            self._route_after_rag_retrieval,
            {
                "response_generation": "response_generation",
                "__end__": END,
            },
        )
        workflow.add_edge("response_generation", END)

        return workflow.compile()

    def run(
        self,
        candidate_id: int,
        query: str,
        target_role: Optional[str] = None,
        language: Optional[str] = None,
    ) -> CareerIntelligenceState:
        """Executes the orchestrator workflow for given candidate_id, query, target_role, and language."""
        initial_state: CareerIntelligenceState = {
            "candidate_id": candidate_id,
            "user_query": query,
            "original_query": query,
            "normalized_query": None,
            "detected_language": "en",
            "language_name": "English",
            "language_confidence": 1.0,
            "response_language": language if language else "",
            "language_metadata": {},
            "target_role": target_role,
            "intent": "unknown",
            "tasks": [],
            "retrieved_context": None,
            "generated_answer": None,
            "recommendation_response": None,
            "evaluation_response": None,
            "interview_response": None,
            "multi_agent_response": None,
            "agent_results": {},
            "aggregated_context": None,
            "agents_used": [],
            "model_name": None,
            "retrieval_metadata": {},
            "status": "initialized",
            "metadata": {},
            "errors": [],
        }
        final_state = self.app.invoke(initial_state)
        return final_state


# Global singleton instance
career_orchestrator = CareerOrchestrator()

