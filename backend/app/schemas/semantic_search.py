from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SemanticSearchResultItem(BaseModel):
    """Represents a single matched candidate from vector similarity search."""
    model_config = ConfigDict(extra="ignore")

    id: str = Field(..., description="ChromaDB document ID e.g. candidate_1")
    candidate_id: int = Field(..., description="Integer candidate user ID")
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0, where 1.0 is exact match)")
    distance: float = Field(..., description="Raw cosine distance from ChromaDB")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Stored candidate metadata attributes")
    document: Optional[str] = Field(None, description="Matched candidate text representation")


class SemanticSearchResponse(BaseModel):
    """Container for semantic search query results."""
    model_config = ConfigDict(extra="ignore")

    query: str = Field(..., description="Original input search query")
    top_k: int = Field(..., description="Number of requested nearest neighbors")
    total_results: int = Field(..., description="Number of results found")
    results: List[SemanticSearchResultItem] = Field(default_factory=list, description="Ranked list of similar candidates")
