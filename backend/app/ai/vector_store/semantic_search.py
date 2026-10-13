import logging
from typing import Any, Dict, List, Optional

from app.ai.embeddings.encoder import EmbeddingEncoder, embedding_encoder
from app.ai.vector_store.chroma_client import ChromaVectorStore, chroma_vector_store
from app.schemas.semantic_search import SemanticSearchResponse, SemanticSearchResultItem

logger = logging.getLogger("careerverse.ai.semantic_search")


class SemanticSearchEngine:
    """
    Orchestrates semantic similarity search across candidate embeddings in ChromaDB.
    Transforms natural language queries into dense embeddings and retrieves ranked candidates.
    """

    def __init__(
        self,
        vector_store: ChromaVectorStore = chroma_vector_store,
        encoder: EmbeddingEncoder = embedding_encoder,
    ):
        self.vector_store = vector_store
        self.encoder = encoder

    def search_candidates(
        self,
        query: str,
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
        owner_candidate_id: Optional[int] = None,
    ) -> SemanticSearchResponse:
        """
        Accepts a natural language query, generates its 384-D embedding,
        and queries ChromaDB for the most semantically relevant candidate profiles.
        When owner_candidate_id is set, results belonging to any other candidate are dropped.
        """
        if not query or not query.strip():
            return SemanticSearchResponse(query=query, top_k=top_k, total_results=0, results=[])

        # 1. Encode natural language query using existing SentenceTransformer encoder
        query_embedding = self.encoder.encode_text(query.strip(), normalize=True)

        # 2. Query ChromaDB collection by vector
        return self.search_by_embedding(
            query=query,
            query_embedding=query_embedding,
            top_k=top_k,
            where=where,
            owner_candidate_id=owner_candidate_id,
        )

    def search_by_embedding(
        self,
        query: str,
        query_embedding: List[float],
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
        owner_candidate_id: Optional[int] = None,
    ) -> SemanticSearchResponse:
        """
        Queries ChromaDB directly with a pre-computed 384-D query embedding vector.
        """
        collection = self.vector_store.collection

        # Ensure collection is not empty
        count = collection.count()
        if count == 0:
            logger.warning("ChromaDB candidate collection is empty.")
            return SemanticSearchResponse(query=query, top_k=top_k, total_results=0, results=[])

        # Limit top_k to existing collection size to prevent out of bounds query
        effective_k = min(top_k, count)

        # Execute vector query in ChromaDB
        query_kwargs: Dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": effective_k,
            "include": ["embeddings", "metadatas", "documents", "distances"],
        }
        if where:
            query_kwargs["where"] = where

        try:
            raw_results = collection.query(**query_kwargs)
        except Exception as exc:
            logger.warning("ChromaDB query failed (isolation-preserving empty result): %s", exc)
            return SemanticSearchResponse(query=query, top_k=top_k, total_results=0, results=[])

        # Parse and format results
        items: List[SemanticSearchResultItem] = []
        if raw_results and raw_results["ids"] and len(raw_results["ids"]) > 0:
            ids = raw_results["ids"][0]
            metadatas = raw_results["metadatas"][0] if raw_results.get("metadatas") else [{}] * len(ids)
            documents = raw_results["documents"][0] if raw_results.get("documents") else [""] * len(ids)
            distances = raw_results["distances"][0] if raw_results.get("distances") else [0.0] * len(ids)

            for doc_id, meta, doc, dist in zip(ids, metadatas, documents, distances):
                # Cosine distance to similarity: similarity = 1.0 - distance
                similarity = max(0.0, min(1.0, 1.0 - float(dist)))
                
                # Extract integer candidate ID from metadata or ID string
                candidate_id = int(meta.get("candidate_id", 0)) if meta and "candidate_id" in meta else 0
                if candidate_id == 0 and doc_id.startswith("candidate_"):
                    try:
                        candidate_id = int(doc_id.split("_")[1])
                    except (IndexError, ValueError):
                        candidate_id = 0

                items.append(
                    SemanticSearchResultItem(
                        id=doc_id,
                        candidate_id=candidate_id,
                        similarity_score=round(similarity, 4),
                        distance=round(float(dist), 4),
                        metadata=meta or {},
                        document=doc,
                    )
                )

        if owner_candidate_id is not None:
            items = [item for item in items if int(item.candidate_id) == int(owner_candidate_id)]

        logger.info("Semantic search for '%s' returned %d results", query[:50], len(items))
        return SemanticSearchResponse(
            query=query,
            top_k=top_k,
            total_results=len(items),
            results=items,
        )


# Global singleton instance for semantic search
semantic_search_engine = SemanticSearchEngine()
