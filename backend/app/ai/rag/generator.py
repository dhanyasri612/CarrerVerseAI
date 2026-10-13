import logging
from typing import Any, Dict, Optional

from app.ai.providers.base import ModelProvider
from app.ai.providers.factory import get_model_provider
from app.ai.rag.context_builder import RAGContextBuilder, rag_context_builder
from app.ai.rag.prompt_builder import RAGPromptBuilder, rag_prompt_builder
from app.schemas.rag import RAGGenerationResponse, RAGRetrievedContext

logger = logging.getLogger("careerverse.ai.rag.generator")


class RAGGenerator:
    """
    Orchestrates grounded generative responses by piping multi-modal retrieval context
    through strict grounding prompts into the configured LLM provider.
    """

    def __init__(
        self,
        context_builder: RAGContextBuilder = rag_context_builder,
        prompt_builder: RAGPromptBuilder = rag_prompt_builder,
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

    def generate_response(
        self,
        candidate_id: int,
        query: str,
        top_k: int = 5,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        language: str = "en",
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> RAGGenerationResponse:
        """
        Executes end-to-end grounded RAG:
        1. Multi-modal retrieval (ChromaDB + Neo4j) -> RAGRetrievedContext
        2. Grounded prompt assembly -> RAGPrompt
        3. LLM inference via Groq provider -> ProviderResponse
        4. Structured output assembly -> RAGGenerationResponse
        """
        logger.info("Initiating RAG Generation for Candidate ID: %d, Query: '%s'", candidate_id, query[:50])

        # 1. Multi-modal retrieval
        context: RAGRetrievedContext = self.context_builder.build_retrieval_context(
            candidate_id=candidate_id,
            query=query,
            top_k=top_k,
            where_filter=where_filter,
        )

        # 2. Grounded prompt construction
        prompt = self.prompt_builder.build_prompt(
            query=query,
            context=context,
            language=language,
        )

        # 3. LLM generation
        provider_response = self.llm_provider.generate_text(
            system_prompt=prompt.system_prompt,
            user_message=prompt.user_message,
            temperature=temperature,
            max_completion_tokens=max_tokens,
        )

        answer_text = provider_response.content.strip()
        model_name = provider_response.model

        logger.info(
            "RAG generation completed successfully for Candidate ID: %d (Model: %s, Answer Length: %d)",
            candidate_id,
            model_name,
            len(answer_text),
        )

        return RAGGenerationResponse(
            candidate_id=candidate_id,
            query=query,
            answer=answer_text,
            model_name=model_name,
            retrieval_metadata=context.metadata,
            prompt_length=len(prompt.user_message),
            context_length=len(context.context_text),
        )


# Global singleton instance
rag_generator = RAGGenerator()
