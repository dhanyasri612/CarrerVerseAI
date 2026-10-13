from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CandidateTextDocument(BaseModel):
    """Structured text representations of candidate intelligence for embedding."""
    model_config = ConfigDict(extra="ignore")

    user_id: int
    full_text: str = Field(..., description="Comprehensive synthesis of candidate intelligence")
    skills_text: str = Field(..., description="Dense narrative of verified technical skills and taxonomy")
    experience_text: str = Field(..., description="Chronological and role-based engineering experience narrative")
    projects_text: str = Field(..., description="Detailed technical project implementations and stacks")
    credentials_text: str = Field(..., description="Certifications, LeetCode, and HackerRank achievements")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata for filtering and downstream retrieval")


class CandidateEmbeddingOutput(BaseModel):
    """Dense vector embeddings generated for a candidate profile."""
    model_config = ConfigDict(extra="ignore")

    user_id: int
    global_embedding: List[float] = Field(..., description="384-dimensional dense vector of the full candidate intelligence")
    skills_embedding: Optional[List[float]] = Field(None, description="Dense vector of skills narrative")
    experience_embedding: Optional[List[float]] = Field(None, description="Dense vector of experience and projects narrative")
    dimension: int = Field(384, description="Dimensionality of the embedding vector")
    model_name: str = Field("sentence-transformers/all-MiniLM-L6-v2", description="Embedding model identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict)
