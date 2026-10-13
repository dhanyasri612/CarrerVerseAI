# Dense Vector Embeddings Engine (`app/ai/embeddings`)

The `app/ai/embeddings` module converts structured and semi-structured candidate intelligence into **normalized 384-dimensional dense vector embeddings** suitable for semantic search and neural retrieval.

---

## 🧮 Model & Vector Specifications

- **Base Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Output Dimensions:** 384 dimensions
- **Normalization:** L2 Euclidean normalization (ensures cosine similarity equals the dot product)
- **Framework:** PyTorch (`torch`) with single-thread CPU execution optimization for fast inference in web workers.

---

## 📁 Module Components

| File | Purpose |
| :--- | :--- |
| **`encoder.py`** | `EmbeddingEncoder` manages lazy loading of the SentenceTransformer model into memory, encodes individual strings or batches into normalized numpy arrays, and handles fast-test fallbacks. |
| **`text_builder.py`** | `CandidateTextBuilder` aggregates a candidate's multi-source profile signals (skills, work history, projects, certifications, LeetCode metrics, GitHub repositories) into a cohesive natural-language text representation optimized for semantic vector density. |

---

## 📄 Candidate Document Synthesis Pipeline

`text_builder.py` structures candidate signals into distinct weighted sections before vector encoding:

```
=== Candidate Technical Profile ===
Target Role / Specialization: Backend & Systems Engineer
Verified Technical Skills: Python, FastAPI, Docker, PostgreSQL, Neo4j, Redis, Kubernetes
Employment Experience:
  - Staff Backend Engineer at Nexus AI: Microservices architecture, high-throughput APIs
Projects & Repositories:
  - CareerVerse AI: Distributed multi-agent career engine with LangGraph
Algorithmic Problem Solving:
  - LeetCode: 250 problems solved, focus on Trees, DP, and Graph algorithms
Verified Certifications:
  - AWS Certified Solutions Architect Associate
```

This rich semantic representation ensures that queries such as *"Who has experience architecting microservices with relational databases?"* achieve high cosine similarity matches against candidate profiles even when exact keyword tokens differ.
