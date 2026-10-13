# Grounded Hybrid RAG Engine (`app/ai/rag`)

The `app/ai/rag` module implements a **Hybrid Retrieval-Augmented Generation (RAG)** pipeline. Instead of relying solely on unstructured text chunks or isolated embeddings, this engine fuses **unstructured semantic vector retrieval** (ChromaDB) with **explicit relational knowledge graph context** (Neo4j).

---

## 🔬 Hybrid Retrieval Architecture

```
                       User Prompt / Candidate Query
                                     │
                                     ▼
                      ┌──────────────────────────────┐
                      │    RAG Context Aggregator    │
                      │    (`context_builder.py`)    │
                      └──────────────┬───────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
  [1. ChromaDB Vector Retrieval]          [2. Neo4j Graph Retrieval]
  - Query embedding generation            - Candidate subgraph traversal
  - Candidate vector lookup               - Skills, projects, tech relations
  - Cosine similarity ranking             - Provenance & source tracking
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     │
                                     ▼
                      ┌──────────────────────────────┐
                      │    Formatted Context Fusion  │
                      │    (`prompt_builder.py`)     │
                      └──────────────┬───────────────┘
                                     │
                                     ▼
                      ┌──────────────────────────────┐
                      │    Grounded LLM Generator    │
                      │       (`generator.py`)       │
                      └──────────────┬───────────────┘
                                     │
                                     ▼
                      Verified, Evidence-Backed Response
```

---

## 📁 Module Components

| File | Purpose |
| :--- | :--- |
| **`context_builder.py`** | Coordinates simultaneous querying of ChromaDB and Neo4j. Filters all returned documents and subgraphs strictly against the authenticated candidate ID. Handles store failures with fallback warnings. |
| **`prompt_builder.py`** | Compiles retrieved candidate signals into structured Markdown sections (Candidate Summary, Evidenced Skills, Projects, Graph Relational Context) with strict anti-hallucination constraints. |
| **`generator.py`** | `RAGResponseGenerator` orchestrates end-to-end execution, calls the active LLM provider (Groq / Ollama), and packages the response into `RAGGenerationResponse` with retrieval metadata. |

---

## 🛡️ Anti-Hallucination Constraints

The RAG prompt builder enforces four core rules on LLM generation:
1. **Direct Evidence Citation:** The LLM must cite specific projects, repositories, or verified accomplishments from the retrieved context when recommending roles or assessing readiness.
2. **Missing Skill Disclosure:** If a role requirement is absent from the candidate's profile, the LLM must classify it as missing or unverified rather than assuming proficiency.
3. **Candidate Isolation:** The retrieval pipeline drops any vector or graph artifact that does not match `candidate_id == authenticated_user_id`.
4. **Honest Unknowns:** When context is insufficient to answer a specialized question, the generator admits the limitation and suggests connecting relevant profile sources.
