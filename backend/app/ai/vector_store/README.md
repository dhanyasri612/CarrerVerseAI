# ChromaDB Vector Store Engine (`app/ai/vector_store`)

The `app/ai/vector_store` module manages the persistent vector storage layer for candidate intelligence embeddings using **ChromaDB**. It provides indexing, updating, and bounded cosine-similarity search across dense 384-dimensional candidate profile vectors.

---

## 🗄️ Core Concepts & Collection Architecture

- **Collection Name:** `candidate_profiles`
- **Embedding Space:** 384-dimensional dense vectors generated via `SentenceTransformers` (`all-MiniLM-L6-v2`).
- **Distance Metric:** Cosine similarity.
- **Persistence Directory:** Configured via `CHROMADB_DIR` (defaults to `./chroma_db`).
- **Document ID Format:** `candidate_{user_id}` (ensures exactly one active vector record per candidate).

---

## 📁 Module Components

| File | Purpose |
| :--- | :--- |
| **`chroma_client.py`** | `ChromaVectorStore` manages the persistent ChromaDB client, handles ephemeral memory fallbacks, sanitizes primitive metadata dictionaries, and performs candidate vector upserts and retrievals. |
| **`semantic_search.py`** | `SemanticSearchEngine` queries the `candidate_profiles` collection using pre-computed query vectors, applies tenant-level metadata filtering, and returns ranked similarity scores. |

---

## 🔒 Metadata Sanitization & Candidate Isolation

ChromaDB requires metadata dictionaries to contain only primitive types (`str`, `int`, `float`, `bool`). `chroma_client.py` sanitizes complex candidate profile models into clean primitive metadata:

```python
metadata = {
    "user_id": candidate_embedding.user_id,
    "model_name": candidate_embedding.model_name,
    "skills_count": len(skills),
    "primary_skills": ", ".join(skills[:15]),
    "updated_at": datetime.utcnow().isoformat(),
}
```

When executing candidate-bounded searches, queries pass explicit `where` metadata filters:
```python
results = collection.query(
    query_embeddings=[query_vector],
    n_results=top_k,
    where={"user_id": candidate_id}
)
```
This guarantees mathematical isolation: a candidate's vector search can never retrieve another candidate's profile records.
