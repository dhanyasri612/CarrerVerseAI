# CareerVerse AI — Backend API & AI Engine

The **CareerVerse AI Backend** is built on **FastAPI**, **PostgreSQL**, **ChromaDB**, **Neo4j**, and **LangGraph**, providing high-performance REST APIs, multi-source profile aggregation, hybrid semantic and knowledge graph retrieval, and multi-agent AI workflows.

---

## 🏗️ Architecture & Component Layout

```
backend/
├── app/
│   ├── main.py                     # FastAPI application entrypoint & middleware configuration
│   ├── core/                       # Core configuration, settings, dependencies & security
│   │   ├── config.py               # Environment variable loading & validation
│   │   ├── dependencies.py         # JWT authentication & request dependency injection
│   │   └── security.py             # Bcrypt password hashing & verification
│   ├── database/                   # SQLAlchemy engine, session maker & Base declarative
│   ├── models/                     # Relational ORM models (User, Resume, Session, etc.)
│   ├── schemas/                    # Pydantic v2 request & response validation schemas
│   ├── routers/                    # Route controllers grouped by functional domain
│   ├── services/                   # Business logic, profile parsing & external integrations
│   └── ai/                         # Multi-agent workflows, vector store, knowledge graph & RAG
├── tests/                          # Automated Pytest suite (83 tests)
├── alembic/                        # Database migration scripts
├── requirements.txt                # Python package dependencies
└── .env                            # Environment configuration (git-ignored)
```

---

## ⚙️ Environment Configuration (`.env`)

Configure the following environment variables in `backend/.env`:

```env
# Application
PROJECT_NAME="CareerVerse AI"
ENVIRONMENT="development"
CORS_ORIGINS="http://localhost:5173,http://localhost:3000"

# PostgreSQL Database
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/careerverse_db"

# JWT Authentication
SECRET_KEY="your-super-secret-jwt-signing-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI Provider Configuration (Groq or Ollama)
AI_PROVIDER="groq"
GROQ_API_KEY="gsk_..."
GROQ_MODEL="llama-3.3-70b-versatile"
# OLLAMA_HOST="http://localhost:11434"
# OLLAMA_MODEL="qwen2.5:7b"

# ChromaDB Vector Store
CHROMADB_DIR="./chroma_db"
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# Neo4j Knowledge Graph
NEO4J_URI="bolt://localhost:7687"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your-neo4j-password"
NEO4J_DATABASE="neo4j"

# External Integrations (Optional)
GITHUB_ACCESS_TOKEN="ghp_..."
```

---

## 🚀 Running the Backend Server

```bash
# 1. Activate Virtual Environment
source .venv/bin/activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Run FastAPI Development Server
uvicorn app.main:app --port 8000 --reload
```

Once started:
- **Interactive OpenAPI Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc UI:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint:** `GET http://localhost:8000/`

---

## 🧪 Testing & Quality Assurance

The backend includes a comprehensive 83-test pytest suite:

```bash
# Run all tests with verbose output
.venv/bin/pytest -v

# Run specific functional test suites
.venv/bin/pytest tests/test_conversational_interview.py
.venv/bin/pytest tests/test_skill_gap_ai.py
.venv/bin/pytest tests/test_candidate_store_sync.py
.venv/bin/pytest tests/test_source_freshness.py
```

### Test Coverage Highlights:
- **Data Isolation:** Verified candidate profiles never cross-pollinate in vector or graph queries.
- **Provider Translation:** Translates upstream timeouts and 5xx errors into user-friendly HTTP exceptions without leaking API internals.
- **Deduplication:** Merges redundant certification and skill entries automatically.
- **Multi-Source Freshness:** Tested 24h cache window policies for LeetCode, GitHub, and HackerRank syncs.

---

## 📦 Key Submodules & Subdirectory Guides

- [AI Engine Architecture](file:///Users/dhanyasrik/Projects/CarrerVerseAI/backend/app/ai/README.md)
- [LangGraph Multi-Agent Workflows](file:///Users/dhanyasrik/Projects/CarrerVerseAI/backend/app/ai/agents/README.md)
- [Neo4j Knowledge Graph Modeling](file:///Users/dhanyasrik/Projects/CarrerVerseAI/backend/app/ai/knowledge_graph/README.md)
- [Hybrid RAG Retrieval Engine](file:///Users/dhanyasrik/Projects/CarrerVerseAI/backend/app/ai/rag/README.md)
- [ChromaDB Vector Store](file:///Users/dhanyasrik/Projects/CarrerVerseAI/backend/app/ai/vector_store/README.md)
- [Dense Vector Embeddings](file:///Users/dhanyasrik/Projects/CarrerVerseAI/backend/app/ai/embeddings/README.md)
- [API Routes & Controller Reference](file:///Users/dhanyasrik/Projects/CarrerVerseAI/backend/app/routers/README.md)
- [Business Services & Integration Layer](file:///Users/dhanyasrik/Projects/CarrerVerseAI/backend/app/services/README.md)
