import json
import logging
import threading
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings

from app.core.config import CHROMADB_DIR
from app.schemas.embedding import CandidateEmbeddingOutput

logger = logging.getLogger("careerverse.ai.vector_store")

CANDIDATE_COLLECTION_NAME = "candidate_profiles"


class ChromaVectorStore:
    """
    Manages persistent ChromaDB vector storage for candidate intelligence embeddings.
    Provides collection initialization, embedding upsert, metadata sanitization, and vector retrieval.
    """

    def __init__(
        self,
        persist_directory: str = CHROMADB_DIR,
        collection_name: str = CANDIDATE_COLLECTION_NAME,
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self._client = None
        self._collection = None
        self._lock = threading.Lock()

    @property
    def client(self):
        """Lazy load and initialize persistent ChromaDB client with ephemeral fallback."""
        with self._lock:
            if self._client is None:
                logger.info("Initializing persistent ChromaDB client at: %s", self.persist_directory)
            try:
                self._client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(anonymized_telemetry=False, is_persistent=True),
                )
                self._client.heartbeat()
            except (Exception, BaseException) as exc:
                logger.warning("PersistentClient failed (%s); using in-memory Client", exc)
                try:
                    self._client = chromadb.Client(
                        Settings(anonymized_telemetry=False, is_persistent=False, allow_reset=True)
                    )
                except Exception as inner_exc:
                    logger.warning("Ephemeral Client fallback failed (%s); vector store disabled", inner_exc)
                    self._client = None
        return self._client

    @property
    def collection(self):
        """Get or create the candidate profile collection configured with cosine similarity."""
        if self._collection is None:
            c = self.client
            if c is None:
                return None
            try:
                self._collection = c.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"},
                )
            except Exception as exc:
                logger.warning("Could not initialize Chroma collection '%s': %s", self.collection_name, exc)
                self._collection = None
        return self._collection

    @staticmethod
    def _sanitize_metadata(raw_metadata: Dict[str, Any], user_id: int, model_name: str) -> Dict[str, Any]:
        """
        Sanitizes metadata dictionary to ensure all values conform to ChromaDB's primitive requirements
        (str, int, float, bool). Nested dicts/lists are converted to strings.
        """
        clean: Dict[str, Any] = {
            "candidate_id": int(user_id),
            "model_name": str(model_name),
            "embedding_type": "candidate_global",
        }
        for k, v in raw_metadata.items():
            if v is None:
                continue
            if isinstance(v, (str, int, float, bool)):
                clean[k] = v
            elif isinstance(v, (list, dict)):
                clean[k] = json.dumps(v, ensure_ascii=True)
            else:
                clean[k] = str(v)
        return clean

    @staticmethod
    def format_candidate_id(user_id: int) -> str:
        """Returns stable, reproducible document ID for candidate."""
        return f"candidate_{user_id}"

    def store_candidate(
        self,
        candidate_embedding: CandidateEmbeddingOutput,
        document_text: Optional[str] = None,
    ) -> Optional[str]:
        """
        Stores or updates (upserts) a candidate embedding and associated metadata in ChromaDB.
        """
        coll = self.collection
        if coll is None:
            logger.warning("Vector store unavailable; skipped storing candidate %s", candidate_embedding.user_id)
            return None

        doc_id = self.format_candidate_id(candidate_embedding.user_id)
        metadata = self._sanitize_metadata(
            raw_metadata=candidate_embedding.metadata,
            user_id=candidate_embedding.user_id,
            model_name=candidate_embedding.model_name,
        )

        try:
            coll.upsert(
                ids=[doc_id],
                embeddings=[candidate_embedding.global_embedding],
                metadatas=[metadata],
                documents=[document_text or ""],
            )
            logger.info("Stored candidate embedding for ID '%s' in collection '%s'", doc_id, self.collection_name)
            return doc_id
        except Exception as exc:
            logger.warning("Failed to upsert candidate %s to Chroma: %s", doc_id, exc)
            return None

    def get_candidate(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a candidate vector, metadata, and document text by candidate user ID.
        """
        coll = self.collection
        if coll is None:
            return None

        doc_id = self.format_candidate_id(user_id)
        try:
            result = coll.get(
                ids=[doc_id],
                include=["embeddings", "metadatas", "documents"],
            )
        except Exception as exc:
            logger.warning("Error reading candidate %s from Chroma: %s", doc_id, exc)
            return None

        if not result or not result.get("ids") or len(result["ids"]) == 0:
            return None

        returned_id = result["ids"][0]
        metadata = (result["metadatas"][0] or {}) if result.get("metadatas") is not None else {}
        try:
            metadata_candidate_id = int(metadata.get("candidate_id", -1))
        except (TypeError, ValueError):
            logger.warning("Ignoring Chroma record %s with invalid candidate metadata", returned_id)
            return None

        if returned_id != doc_id or metadata_candidate_id != int(user_id):
            logger.warning(
                "Ignoring Chroma record %s because it is not owned by candidate %s",
                returned_id,
                user_id,
            )
            return None

        return {
            "id": returned_id,
            "embedding": result["embeddings"][0] if result.get("embeddings") is not None else None,
            "metadata": metadata,
            "document": result["documents"][0] if result.get("documents") is not None else "",
        }

    def delete_candidate(self, user_id: int) -> bool:
        """Deletes a candidate embedding by user ID."""
        coll = self.collection
        if coll is None:
            return False
        doc_id = self.format_candidate_id(user_id)
        try:
            coll.delete(ids=[doc_id])
            return True
        except Exception as exc:
            logger.warning("Failed to delete candidate %s from Chroma: %s", doc_id, exc)
            return False

    def count(self) -> int:
        """Returns total count of stored embeddings in collection."""
        coll = self.collection
        if coll is None:
            return 0
        try:
            return coll.count()
        except Exception:
            return 0


# Global vector store singleton instance
chroma_vector_store = ChromaVectorStore()
