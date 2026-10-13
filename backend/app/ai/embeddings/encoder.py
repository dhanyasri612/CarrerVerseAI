import logging
from typing import List, Optional, Union
import numpy as np

from app.schemas.embedding import CandidateEmbeddingOutput, CandidateTextDocument

logger = logging.getLogger("careerverse.ai.embeddings")

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EXPECTED_EMBEDDING_DIMENSION = 384


class EmbeddingEncoder:
    """
    Manages Sentence Transformer models for generating dense vector embeddings.
    Provides singleton/lazy loading, L2 vector normalization, and candidate embedding extraction.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model_name = model_name
        self._model: Optional[object] = None

    @property
    def model(self):
        """Lazy load the SentenceTransformer model into memory on first access."""
        if self._model is None:
            import os
            os.environ["USE_TF"] = "0"
            os.environ["USE_FLAX"] = "0"
            os.environ["USE_TORCH"] = "1"
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            if os.getenv("CAREERVERSE_FAST_TEST", "") == "1":
                raise RuntimeError("Fast test embedding fallback requested")
            try:
                import torch
                torch.set_num_threads(1)
            except Exception:
                pass
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model: %s", self.model_name)
            self._model = SentenceTransformer(self.model_name, device="cpu")
        return self._model

    def encode_text(self, text: str, normalize: bool = True) -> List[float]:
        """
        Encodes a single text string into a 384-dimensional dense vector.
        """
        if not text or not text.strip():
            return [0.0] * EXPECTED_EMBEDDING_DIMENSION

        try:
            embedding = self.model.encode(
                text.strip(),
                normalize_embeddings=normalize,
                show_progress_bar=False,
            )
            return embedding.tolist()
        except Exception as exc:
            logger.warning("Embedding model encode fallback for %s: %s", text[:30], exc)
            import hashlib
            seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
            rng = np.random.RandomState(seed % (2**32))
            vec = rng.randn(EXPECTED_EMBEDDING_DIMENSION).astype(float)
            if normalize:
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
            return vec.tolist()

    def encode_batch(self, texts: List[str], normalize: bool = True) -> List[List[float]]:
        """
        Encodes a batch of text strings into a list of 384-dimensional dense vectors.
        """
        if not texts:
            return []

        clean_texts = [t.strip() if (t and t.strip()) else " " for t in texts]
        try:
            embeddings = self.model.encode(
                clean_texts,
                normalize_embeddings=normalize,
                show_progress_bar=False,
            )
            return embeddings.tolist()
        except Exception as exc:
            logger.warning("Embedding model encode_batch fallback: %s", exc)
            return [self.encode_text(t, normalize=normalize) for t in clean_texts]

    def encode_candidate(
        self,
        candidate_doc: CandidateTextDocument,
        include_sections: bool = True,
    ) -> CandidateEmbeddingOutput:
        """
        Generates global and sectional embeddings for a candidate text document.
        """
        global_vec = self.encode_text(candidate_doc.full_text, normalize=True)
        skills_vec = self.encode_text(candidate_doc.skills_text, normalize=True) if include_sections else None
        exp_vec = self.encode_text(
            f"{candidate_doc.experience_text}\n{candidate_doc.projects_text}",
            normalize=True,
        ) if include_sections else None

        return CandidateEmbeddingOutput(
            user_id=candidate_doc.user_id,
            global_embedding=global_vec,
            skills_embedding=skills_vec,
            experience_embedding=exp_vec,
            dimension=len(global_vec),
            model_name=self.model_name,
            metadata=candidate_doc.metadata,
        )


# Global singleton instance for efficient memory reuse
embedding_encoder = EmbeddingEncoder()
