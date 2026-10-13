# CareerVerse AI — Multi-Agent & RAG AI Engine

The `app/ai` directory contains the complete intelligent decision-making, reasoning, and context retrieval architecture for CareerVerse AI. It implements a **hybrid retrieval and multi-agent reasoning architecture** that pairs semantic vector search with relational knowledge graph reasoning.

---

## 🏛️ AI Architecture Pipeline

```
Candidate Evidence (Resume, GitHub, LeetCode, Certifications)
                       │
                       ▼
          [1. Embeddings & Text Builder]
     (SentenceTransformers 384-D Vector Encoding)
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
  [ChromaDB Vector Store]    [Neo4j Knowledge Graph]
 (Unstructured Semantic)    (Explicit Relational Entities)
          │                         │
          └────────────┬────────────┘
                       ▼
          [2. Grounded Context Fusion (RAG)]
        (Filters candidate-isolated evidence only)
                       │
                       ▼
          [3. LangGraph Multi-Agent Workflows]
     ┌──────────────────────────────────────────────┐
     │ • Recommendation Agent (Role matching)       │
     │ • Evaluation Agent (Skill gap & severity)    │
     │ • Interview Agent (Adaptive follow-ups)      │
     │ • Multi-Agent Orchestrator (Full report)     │
     └──────────────────────────────────────────────┘
                       │
                       ▼
      [4. Multilingual LLM Provider]
       (Groq LLaMA 3.3 / Ollama Qwen)
                       │
                       ▼
        Structured, Grounded Response
```

---

## 📂 Submodule Directory Breakdown

| Directory | Core Purpose & Technical Implementation |
| :--- | :--- |
| **[`agents/`](./agents/README.md)** | **LangGraph Multi-Agent Workflows:** StateGraph orchestration, conditional routing, and specialized agents for recommendations, skill gap analysis, and interviews. |
| **[`knowledge_graph/`](./knowledge_graph/README.md)** | **Neo4j Graph Modeling:** Graph schema definitions, constraint management, Cypher queries, and graph builder for candidate skills, projects, and technologies. |
| **[`rag/`](./rag/README.md)** | **Hybrid RAG Engine:** Fuses semantic similarity search results from ChromaDB with explicit relationship paths from Neo4j into unified candidate context. |
| **[`vector_store/`](./vector_store/README.md)** | **ChromaDB Vector Storage:** Persistent client management, candidate embedding collections, and bounded cosine similarity search. |
| **[`embeddings/`](./embeddings/README.md)** | **Dense Vector Encoders:** Uses `sentence-transformers/all-MiniLM-L6-v2` with L2 normalization to generate 384-D vector representations. |
| **[`language/`](./language/)** | **Multilingual Prompt Engineering:** Language detection and natural prompt tuning for English, conversational Tanglish, and Hinglish. |
| **[`stores/`](./stores/)** | **Store Synchronization:** Coordinates atomic synchronization between PostgreSQL, ChromaDB, and Neo4j upon candidate profile changes. |
| **[`providers/`](./providers/)** | **LLM Provider Abstraction:** Standardized interface supporting Groq (`llama-3.3-70b-versatile`) and local Ollama (`qwen2.5:7b`). |

---

## 🔒 Key Design Guarantees

1. **Candidate Data Isolation:** All vector and graph queries are strictly filtered by the authenticated `candidate_id` extracted from the JWT token. Candidate data never leaks across profiles.
2. **Evidence-Grounded Inferences:** The agents are constrained to cite verified candidate evidence (e.g., specific projects, solved algorithmic problems, verified certifications) and cannot hallucinate credentials.
3. **Graceful Degradation:** If Neo4j or ChromaDB is temporarily unreachable, the RAG engine degrades gracefully to available sources without failing the entire request.
4. **Resilient Error Translation:** Upstream provider failures (rate limits, timeouts) are translated into clean, non-leaking HTTP exceptions (`502`, `503`, `504`).
