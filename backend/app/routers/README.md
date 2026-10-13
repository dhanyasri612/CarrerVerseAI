# FastAPI Routers & API Reference (`app/routers`)

The `app/routers` module defines the HTTP API routes and request controllers for CareerVerse AI. All endpoints enforce authentication via dependency injection (`get_current_user`), validate inputs with Pydantic v2 schemas, and map exceptions to HTTP status codes.

---

## 🧭 Complete API Endpoint Catalog

### 1. Authentication (`auth.py` — prefix: `/auth`)
| Method | Path | Summary | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | User Registration | Creates a new user account with bcrypt-hashed password. |
| `POST` | `/auth/login` | User Login | Authenticates credentials and returns a signed JWT bearer token. |

### 2. Candidate Profile (`profile.py` — prefix: `/profile`)
| Method | Path | Summary | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/profile` | Get Profile | Retrieves current user profile attributes (contact, bio, location). |
| `PUT` | `/profile` | Update Profile | Updates profile attributes and triggers safe background AI store sync. |

### 3. Resume Management (`resume.py` & `parser.py`)
| Method | Path | Summary | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/resume/upload` | Upload Resume | Uploads a PDF resume and saves metadata to PostgreSQL. |
| `GET` | `/resume` | List Resumes | Returns all uploaded resumes for the authenticated user. |
| `POST` | `/parser/resume/{id}` | Parse Resume | Parses PDF text, extracting skills, education, experience, and projects. |
| `GET` | `/parser/resume/{id}` | Get Parsed Resume | Retrieves the cached parsed resume JSON structure. |

### 4. Candidate Intelligence (`candidate_intelligence.py`)
| Method | Path | Summary | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/candidate-intelligence/unified-profile` | Unified Profile | Aggregates skills across resumes, GitHub, LeetCode, HackerRank, and certifications. |

### 5. Multi-Agent AI Endpoints (`ai.py` — prefix: `/ai`)
| Method | Path | Summary | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/ai/rag` | Grounded RAG Query | Answers queries using fused ChromaDB vector search and Neo4j graph context. |
| `POST` | `/ai/career/recommend` | Career Discovery | Generates evidence-grounded career role recommendations with fit scores. |
| `POST` | `/ai/career/skill-gap` | Skill Gap Analysis | Compares candidate skills against role requirements; outputs gap severity. |
| `POST` | `/ai/career/interview/session` | Create Interview Session | Starts an interactive technical interview room with an adaptive problem statement. |
| `POST` | `/ai/career/interview/session/{id}/answer` | Submit Interview Turn | Evaluates user code/answer and generates adaptive follow-up challenges. |
| `POST` | `/ai/career/interview/session/{id}/complete` | Complete Interview | Concludes interview session, generates scorecard, and performance evaluation. |
| `GET` | `/ai/career/interview/questions/history` | Spaced Repetition History | Retrieves answered interview questions with 30-day cooldown flags. |
| `POST` | `/ai/career/quiz/session` | Start Career Compass | Creates a situational technical diagnostic quiz session. |
| `POST` | `/ai/career/quiz/session/{id}/answer` | Submit Quiz Answer | Records question answer and updates situational trajectory score. |
| `POST` | `/ai/career/quiz/session/{id}/complete` | Complete Career Quiz | Synthesizes candidate archetypes and recommended career avenues. |
| `POST` | `/ai/career/intelligence` | Executive AI Report | Multi-agent synthesis unifying recommendations, gap analysis, and interview prep. |

### 6. External Platform Integrations
| Module | Path | Description |
| :--- | :--- | :--- |
| `github.py` | `POST /github/sync/{username}` | Syncs GitHub public repositories, languages, README files, and commit activity. |
| `leetcode.py` | `POST /leetcode/sync/{username}` | Syncs LeetCode solved counts (Easy/Medium/Hard), ranking, and submission history. |
| `hackerrank.py` | `POST /hackerrank/sync/{username}` | Syncs HackerRank badges, verified stars, and domain scores. |
| `certification.py` | `POST /certifications/upload` | Parses certificate PDFs via PyMuPDF; extracts issuing organization and skills. |
| `linkedin.py` | `POST /linkedin/sync` | Ingests professional experience and verified credential records. |

### 7. Jobs & Learning Roadmaps
| Module | Path | Description |
| :--- | :--- | :--- |
| `job.py` | `GET /job`, `POST /job` | Catalogs industry positions with benchmark skills and requirements. |
| `career_roadmap.py` | `GET /roadmap/{resume_id}/{job_id}` | Generates milestone stages, prerequisites, and learning objectives. |
| `skill_gap.py` | `POST /skill-gap/analyze/{resume_id}/{job_id}` | Resume-to-job skill alignment diagnostic. |
