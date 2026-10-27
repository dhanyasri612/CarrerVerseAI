import pytest
import os
import time

def test_chroma_semantic_search_bounded():
    """Regression test ensuring ChromaDB semantic search executes without deadlocking."""
    from app.ai.vector_store.semantic_search import SemanticSearchEngine
    engine = SemanticSearchEngine()
    
    # 1. Cold load query (must finish within 25s without deadlocking)
    start_cold = time.time()
    result_cold = engine.search_candidates("Full Stack Python Developer", top_k=3)
    duration_cold = time.time() - start_cold
    assert duration_cold < 25.0, f"Cold semantic search took too long ({duration_cold:.2f}s)"

    # 2. Warm query (must execute in under 2.0s)
    start_warm = time.time()
    result_warm = engine.search_candidates("Backend Engineer FastAPI", top_k=3)
    duration_warm = time.time() - start_warm
    assert duration_warm < 2.0, f"Warm semantic search took too long ({duration_warm:.2f}s)"
    assert hasattr(result_warm, "results")
    assert isinstance(result_warm.results, list)
