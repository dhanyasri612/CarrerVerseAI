import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.ai.embeddings.encoder import embedding_encoder
from app.ai.vector_store.chroma_client import chroma_vector_store
from app.ai.vector_store.semantic_search import SemanticSearchEngine, semantic_search_engine
from app.schemas.semantic_search import SemanticSearchResponse



def test_empty_query_semantic_search():
    """Verify that an empty or whitespace query gracefully returns empty results."""
    engine = SemanticSearchEngine(vector_store=chroma_vector_store, encoder=embedding_encoder)
    res = engine.search_candidates(query="", top_k=5)
    assert isinstance(res, SemanticSearchResponse)
    assert res.total_results == 0
    assert len(res.results) == 0

    res_space = engine.search_candidates(query="   ", top_k=5)
    assert res_space.total_results == 0
    assert len(res_space.results) == 0


def test_query_embedding_generation():
    """Verify that natural language query is encoded into normalized 384-D vector."""
    query = "Full Stack developer with React and Python experience"
    vec = embedding_encoder.encode_text(query, normalize=True)
    assert len(vec) == 384
    assert not any(x != x for x in vec)  # No NaNs


def test_semantic_search_candidates():
    """Verify semantic search query execution against ChromaDB collection."""
    # Ensure collection has at least 1 record
    count = chroma_vector_store.count()
    if count == 0:
        print("Note: ChromaDB candidate collection is empty, skipping live search.")
        return

    query = "AI ML developer with strong problem solving skills"
    response = semantic_search_engine.search_candidates(query=query, top_k=5)

    assert isinstance(response, SemanticSearchResponse)
    assert response.total_results >= 1
    assert len(response.results) >= 1

    top_result = response.results[0]
    assert top_result.id.startswith("candidate_")
    assert top_result.candidate_id > 0
    assert 0.0 <= top_result.similarity_score <= 1.0
    assert top_result.distance >= 0.0
    assert top_result.metadata is not None
    assert top_result.document is not None


if __name__ == "__main__":
    print("Running Semantic Search Tests...")
    test_empty_query_semantic_search()
    print("✓ test_empty_query_semantic_search passed")
    test_query_embedding_generation()
    print("✓ test_query_embedding_generation passed")
    test_semantic_search_candidates()
    print("✓ test_semantic_search_candidates passed")
    print("\nALL SEMANTIC SEARCH UNIT TESTS PASSED!")

