from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.knowledge_graph import CandidateSubgraphResponse
from app.schemas.semantic_search import SemanticSearchResultItem


class RAGRequest(BaseModel):
    """Candidate question for grounded retrieval-augmented generation."""

    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(5, ge=1, le=20)
    temperature: float = Field(0.2, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=4000)
    language: str = Field("en", min_length=2, max_length=10)


class RAGRetrievedContext(BaseModel):
    """
    Unified container for multi-modal candidate retrieval context combining:
    1. ChromaDB semantic vector search results
    2. Neo4j structured knowledge graph subgraph
    3. Deterministic synthesized grounding text (no LLM)
    """
    model_config = ConfigDict(extra="ignore")

    candidate_id: int = Field(..., description="Integer candidate user ID")
    query: str = Field(..., description="Original natural-language search query")
    semantic_results: List[SemanticSearchResultItem] = Field(
        default_factory=list,
        description="Top nearest neighbor semantic matches retrieved from ChromaDB",
    )
    graph_context: Optional[CandidateSubgraphResponse] = Field(
        None,
        description="Explicit structured entity subgraph retrieved from Neo4j",
    )
    context_text: str = Field(
        ...,
        description="Deterministic structured context text combining graph and semantic intelligence",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Retrieval audit metadata including counts, scores, and timestamp",
    )


class RAGPrompt(BaseModel):
    """Encapsulates structured prompt components sent to the LLM."""
    model_config = ConfigDict(extra="ignore")

    system_prompt: str = Field(..., description="System instructions enforcing strict grounding")
    user_message: str = Field(..., description="User message embedding retrieved context and question")
    query: str = Field(..., description="Original user question")


class RAGGenerationResponse(BaseModel):
    """Structured response container for grounded RAG generation."""
    model_config = ConfigDict(extra="ignore")

    candidate_id: int = Field(..., description="Integer candidate user ID")
    query: str = Field(..., description="Original user question")
    answer: str = Field(..., description="Grounded LLM-generated answer")
    model_name: str = Field(..., description="Identifier of the generative model used")
    retrieval_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Audit metadata from vector and graph retrieval",
    )
    prompt_length: int = Field(0, description="Character count of generated prompt")
    context_length: int = Field(0, description="Character count of retrieved context")

