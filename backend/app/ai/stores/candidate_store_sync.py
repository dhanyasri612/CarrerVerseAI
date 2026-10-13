"""
Production synchronization of PostgreSQL unified candidate profiles into
ChromaDB (embeddings) and Neo4j (knowledge graph).

Postgres writes always complete first. Chroma and Neo4j failures are isolated
and never roll back candidate records.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.ai.embeddings.encoder import EmbeddingEncoder, embedding_encoder
from app.ai.embeddings.text_builder import CandidateTextBuilder
from app.ai.knowledge_graph.graph_builder import CandidateGraphBuilder, candidate_graph_builder
from app.ai.vector_store.chroma_client import ChromaVectorStore, chroma_vector_store
from app.models.user import User
from app.schemas.candidate_intelligence import UnifiedProfileResponse

logger = logging.getLogger("careerverse.ai.stores.sync")

STATUS_SUCCESS = "success"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"


@dataclass
class CandidateStoreSyncResult:
    candidate_id: int
    chroma_status: str = STATUS_SKIPPED
    neo4j_status: str = STATUS_SKIPPED
    chroma_document_id: Optional[str] = None
    graph_counts: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    chroma_error: Optional[str] = None
    neo4j_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def persist_candidate_ai_stores(
    profile: UnifiedProfileResponse,
    *,
    vector_store: Optional[ChromaVectorStore] = None,
    encoder: Optional[EmbeddingEncoder] = None,
    graph_builder: Optional[CandidateGraphBuilder] = None,
) -> CandidateStoreSyncResult:
    """
    Encode the unified profile, upsert the candidate's Chroma vector, and
    rebuild that candidate's Neo4j subgraph. Each store is independent.
    """
    candidate_id = int(profile.user_profile.id)
    result = CandidateStoreSyncResult(candidate_id=candidate_id)
    store = vector_store or chroma_vector_store
    enc = encoder or embedding_encoder
    builder = graph_builder or candidate_graph_builder

    try:
        document = CandidateTextBuilder.build_document(profile)
        embedding = enc.encode_candidate(document)
        if int(embedding.user_id) != candidate_id:
            raise ValueError(
                f"Embedding user_id {embedding.user_id} does not match candidate_id {candidate_id}"
            )
        doc_id = store.store_candidate(embedding, document_text=document.full_text)
        stored = store.get_candidate(candidate_id)
        stored_cid = None
        if stored and stored.get("metadata"):
            stored_cid = stored["metadata"].get("candidate_id")
        if stored_cid is not None and int(stored_cid) != candidate_id:
            raise ValueError(
                f"Chroma metadata candidate_id {stored_cid} does not match {candidate_id}"
            )
        result.chroma_document_id = doc_id
        result.chroma_status = STATUS_SUCCESS
    except Exception as exc:
        error_msg = f"Chroma sync failed for candidate {candidate_id}: {exc}"
        logger.error(error_msg, exc_info=True)
        result.chroma_status = STATUS_FAILED
        result.chroma_error = str(exc)
        result.errors.append(error_msg)

    try:
        graph_result = builder.rebuild_candidate_graph(profile)
        result.graph_counts = graph_result.get("counts") or {}
        result.neo4j_status = STATUS_SUCCESS
    except Exception as exc:
        error_msg = f"Neo4j sync failed for candidate {candidate_id}: {exc}"
        logger.error(error_msg, exc_info=True)
        result.neo4j_status = STATUS_FAILED
        result.neo4j_error = str(exc)
        result.errors.append(error_msg)

    return result


def sync_candidate_ai_stores(
    db: Session,
    current_user: User,
    *,
    vector_store: Optional[ChromaVectorStore] = None,
    encoder: Optional[EmbeddingEncoder] = None,
    graph_builder: Optional[CandidateGraphBuilder] = None,
) -> CandidateStoreSyncResult:
    """Build the unified profile from Postgres, then persist to Chroma and Neo4j."""
    from app.services.unified_profile_service import build_unified_candidate_profile

    if current_user is None or not getattr(current_user, "id", None):
        return CandidateStoreSyncResult(
            candidate_id=0,
            chroma_status=STATUS_SKIPPED,
            neo4j_status=STATUS_SKIPPED,
            errors=["Cannot sync AI stores without a valid candidate user id."],
        )

    profile = build_unified_candidate_profile(db=db, current_user=current_user)
    return persist_candidate_ai_stores(
        profile,
        vector_store=vector_store,
        encoder=encoder,
        graph_builder=graph_builder,
    )


def sync_candidate_ai_stores_safe(
    db: Session,
    current_user: User,
    **kwargs: Any,
) -> CandidateStoreSyncResult:
    """
    Best-effort sync used after Postgres commits. Never raises to the caller.
    """
    try:
        return sync_candidate_ai_stores(db, current_user, **kwargs)
    except Exception as exc:
        candidate_id = int(getattr(current_user, "id", 0) or 0)
        error_msg = f"Candidate AI store sync aborted for candidate {candidate_id}: {exc}"
        logger.error(error_msg, exc_info=True)
        return CandidateStoreSyncResult(
            candidate_id=candidate_id,
            chroma_status=STATUS_FAILED,
            neo4j_status=STATUS_FAILED,
            errors=[error_msg],
        )
