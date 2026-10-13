# CareerVerse AI — Autonomous Multi-Agent Career Intelligence & Interview Platform

> **CareerVerse AI** is an enterprise-grade career navigation platform powered by a hybrid multi-agent AI architecture, combining **LangGraph multi-agent workflows**, **ChromaDB vector similarity search**, **Neo4j knowledge graph modeling**, and **retrieval-augmented generation (RAG)** to provide grounded career guidance, evidence-based skill gap evaluations, interactive learning roadmaps, and adaptive conversational technical interviews.

---

## 🏛️ System Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │        CareerVerse AI Frontend         │
                      │  (React 18 + Vite + Editorial Design)  │
                      └───────────────────┬────────────────────┘
                                          │ HTTP / REST & WebSockets
                                          ▼
                      ┌────────────────────────────────────────┐
                      │           FastAPI Backend API          │
                      │   (Auth, Routers, Business Services)   │
                      └───────┬────────────────────────┬───────┘
                              │                        │
         PostgreSQL Database  │                        │  Multi-Source Ingestion
   (Users, Resumes, Sessions) │                        │  (PDF, GitHub, LeetCode)
                              ▼                        ▼
                      ┌────────────────────────────────────────┐
                      │    Unified Candidate Profile Engine    │
                      └───────────────────┬────────────────────┘
                                          │ Sync Pipelines
                     ┌────────────────────┴────────────────────┐
                     ▼                                         ▼
        ┌─────────────────────────┐               ┌─────────────────────────┐
        │   ChromaDB Vector Store │               │  Neo4j Knowledge Graph  │
        │  (384-D Dense Vectors)  │               │ (Graph Relations & Path)│
        └────────────┬────────────┘               └────────────┬────────────┘
                     │                                         │
                     └────────────────────┬────────────────────┘
                                          │ Hybrid Context Fusion
                                          ▼
                      ┌────────────────────────────────────────┐
                      │     LangGraph Multi-Agent Workflows    │
                      │   ┌────────────────────────────────┐   │
                      │   │  Recommendation Agent          │   │
                      │   │  Evaluation (Skill Gap) Agent  │   │
                      │   │  Interview Preparation Agent   │   │
                      │   │  Career Intelligence Executive │   │
                      │   └────────────────────────────────┘   │
                      │         LLM: Groq / Ollama (Qwen)      │
                      └────────────────────────────────────────┘
```

---

## ✨ Core Features & Editorial Chapters

| Chapter / Feature | Purpose | Underlying Technology |
| :--- | :--- | :--- |
| **01. Candidate Dossier (`/profile`)** | Centralized profile story synthesizing resumes, GitHub repos, LeetCode stats, HackerRank scores, and certifications. | PostgreSQL, PyMuPDF, PyGitHub, GraphQL Scrapers |
| **02. Career Discovery (`/discovery`)** | Identifies grounded career directions matching candidate strengths with fit scores and evidence citations. | LangGraph Recommendation Agent, ChromaDB, Neo4j |
| **03. Career Compass (`/career-quiz`)** | Situational technical assessment diagnosing architectural instincts and leadership style. | LangGraph Agent, PostgreSQL Session State Machine |
| **04. Skill Gap Analysis (`/skill-gap`)** | Diagnostic breakdown of demonstrated vs. missing proficiencies against real industry target roles. | LangGraph Evaluation Agent, Neo4j Graph traversal |
| **05. Learning Journey (`/career-roadmap`)** | Personalized milestones, interactive roadmap.sh-style tech trees, and progressive hands-on curriculum. | TechTree Graph, Visual Pipeline, Dynamic Roadmap Engine |
| **06. Alex AI Interview Room (`/interview`)** | Interactive technical interview agent featuring code workbench, audio playback, and adaptive questions. | LangGraph Interview Agent, SpeechSynthesis, Tanglish/Hinglish |
| **07. Career Intelligence (`/ai/intelligence`)** | Executive synthesis integrating role trajectories, skill deficit analysis, and interview readiness. | Multi-Agent Orchestrator, Hybrid RAG Engine |

---

## 📁 Repository Directory Structure

```
CarrerVerseAI/
├── README.md                      # Master repository documentation (this file)
├── TESTING_AUDIT_REPORT.md        # Comprehensive QA audit & verification report
├── backend/                       # FastAPI backend application
│   ├── README.md                  # Backend architecture & configuration guide
│   ├── app/
│   │   ├── ai/                    # Core AI engine
│   │   │   ├── README.md          # AI system architecture overview
│   │   │   ├── agents/            # LangGraph multi-agent workflows
│   │   │   ├── knowledge_graph/   # Neo4j graph schemas, builder & Cypher queries
│   │   │   ├── rag/               # Hybrid context fusion & RAG generators
│   │   │   ├── vector_store/      # ChromaDB client & semantic similarity search
│   │   │   ├── embeddings/        # SentenceTransformers dense 384-D vector encoders
│   │   │   └── language/          # Multilingual adaptation (English, Tanglish, Hindi)
│   │   ├── routers/               # FastAPI route controllers
│   │   │   └── README.md          # Complete REST API reference
│   │   ├── services/              # Business logic & profile synthesis
│   │   │   └── README.md          # Service contracts & cache policies
│   │   ├── models/                # SQLAlchemy ORM models
│   │   └── schemas/               # Pydantic v2 validation contracts
│   └── tests/                     # 83 automated backend pytest suites
└── frontend/                      # React 18 + Vite frontend application
    ├── README.md                  # Frontend architecture & design system guide
    ├── src/
    │   ├── pages/                 # Editorial chapter pages
    │   │   └── README.md          # Page routes & editorial view guides
    │   ├── components/            # Reusable UI & visualization components
    │   ├── design-system/         # Editorial design tokens & typography
    │   └── test/                  # 86 automated Vitest integration tests
```

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- **Python:** 3.11+
- **Node.js:** v18+ & npm v9+
- **PostgreSQL:** Port `5432` (`careerverse_db`)
- **Neo4j:** Port `7687` (Bolt), `7474` (HTTP)
- **Groq API Key** or **Ollama** (`qwen2.5:7b`)

### 1. Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --port 8000 --reload
```
API Documentation will be available at: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install

# Start Vite dev server
npm run dev -- --port 5173
```
Web application will be available at: `http://localhost:5173`

---

## 🧪 Automated Testing & Verification

The project includes 100% passing test suites across backend and frontend:

```bash
# Run backend tests (83 tests)
cd backend && .venv/bin/pytest -v

# Run frontend tests (86 tests)
cd frontend && npm test

# Run frontend production build
cd frontend && npm run build
```

See [TESTING_AUDIT_REPORT.md](file:///Users/dhanyasrik/Projects/CarrerVerseAI/TESTING_AUDIT_REPORT.md) for full audit metrics and live verification evidence.

---

## 🔒 Security & Data Isolation
- **Tenant Isolation:** All AI context generation, vector search, and graph traversal strictly extract candidate identity from authenticated JWT claims.
- **Evidence Grounding:** Anti-hallucination validation ensures AI recommendations, questions, and roadmaps are grounded directly in candidate evidence.
- **Credential Protection:** Secrets and tokens are securely loaded via environment variables and never logged or serialized in responses.

---

## 📜 License
Proprietary & Confidential — CareerVerse AI Team.