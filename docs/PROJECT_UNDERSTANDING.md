# CareerVerse AI — Read-Only Project Understanding Report

**Investigation date:** 15 Oct 2026
**Workspace state audited:** branch `main` @ `ad70849` **plus 25 uncommitted modified files** (+466/−75) and several untracked files.
**Method:** Static source tracing of the live workspace, environment/port probes, and execution of the existing test suites only. No source files, dependencies, env vars, or databases were modified. This report is the only file created.

---

## 1. Actual Project Architecture

```
Frontend (React 19 + Vite SPA)                     Backend (FastAPI)
├─ src/main.jsx → src/App.jsx (route table)        ├─ app/main.py  ← entry point (imports models/routers,
├─ src/services/api.js  (axios, Bearer token)      │   runs Base.metadata.create_all + ensure_resume_cache_columns)
│   baseURL = VITE_API_BASE_URL (:8000)            ├─ app/routers/*        (17 routers, REST + JSON bodies)
├─ src/services/careerService.js  (all AI APIs     ├─ app/services/*       (business logic, 13.9k LOC)
│   + module-level profile/resume caches)          ├─ app/ai/agents/*      (LangGraph StateGraph orchestrator)
├─ src/services/{auth,resume,activity,             ├─ app/ai/rag/*         (RAGContextBuilder + RAGGenerator)
│   speech}Service.js                              ├─ app/ai/vector_store/* (ChromaDB, cosine, 384-d)
├─ src/context/AuthContext.jsx (localStorage       ├─ app/ai/knowledge_graph/* (Neo4j driver + graph builder)
│   cv_token / cv_user)                            ├─ app/ai/embeddings/*  (sentence-transformers all-MiniLM-L6-v2)
└─ src/pages/* (17 page files; 15 reachable — see V1)          ├─ app/ai/providers/*   (Groq | Ollama factory)
                                                   ├─ app/models/*         (17 model modules → PostgreSQL)
                                                   └─ app/parsers/*        (regex/PyMuPDF resume + cert parsers)

Stores: PostgreSQL (DATABASE_URL=postgresql://dhanyasrik@localhost:5432/careerverse_db)
        ChromaDB persistent dir backend/chroma_db (2.2 MB data present)
        Neo4j bolt://localhost:7687 (currently NOT reachable — see §5)
```

**LangGraph pipeline** (`app/ai/agents/orchestrator.py`, `CareerOrchestrator._build_graph`, ~lines 700–764):
`request_processor` → `task_router` → (`recommendation_node` → `evaluation_node` → `interview_node`, chained via conditional edges) → `context_aggregator_node` → `synthesis_node` → END, with a general-RAG fallback path `rag_retrieval` → `response_generation`.
Shared state is the `CareerIntelligenceState` TypedDict (`app/ai/agents/state.py`). High-level entry points: `app/ai/agents/service.py::run_career_intelligence / run_career_recommendation / run_skill_gap_evaluation / run_interview_preparation / run_multi_agent_career_intelligence`.

**Authentication (verified):** JWT HS256 (`python-jose`), OAuth2 bearer via `app/core/dependencies.py::get_current_user` (token `sub` = email; 60-min default expiry). Frontend stores `cv_token` in localStorage; the axios interceptor injects `Authorization: Bearer …` and dispatches `cv:logout` on any 401 (`frontend/src/services/api.js:20–31`). There is **no token-expiry validation on page load** — only a 401 response clears the session.

**Verified vs inferred:** Every frontend→backend path cited above was traced in source (verified). Runtime behavior of live LLM/GitHub/LeetCode APIs was not observed (inferred from code + tests).

## 2. Technology Stack and Startup Flow

| Layer    | Technology (versions from manifests)                                                                                      |
| -------- | ------------------------------------------------------------------------------------------------------------------------- |
| Frontend | React 19.2, react-router-dom 7.18, axios, lucide-react, marked; Vite 8; Vitest 5 + Testing Library; Playwright 1.64 (dev) |
| Backend  | FastAPI 0.139, SQLAlchemy 2.0.51, Pydantic 2.13, python-jose, passlib/bcrypt, python-dotenv                               |
| AI       | langgraph 0.2.76, langchain-core, groq 0.37 SDK, sentence-transformers 6.0.1 (torch CPU), langdetect                      |
| Stores   | PostgreSQL (psycopg2), ChromaDB 1.5.9 (embedded persistent), Neo4j 5.28.1 driver                                          |
| Files    | PyMuPDF 1.28 (PDF text), httpx (GitHub/LeetCode/HackerRank/LinkedIn REST)                                                 |

**Startup (from `backend/README.md:82` and `frontend/package.json`):**

- Backend: `cd backend && uvicorn app.main:app --port 8000 --reload` — config from `backend/.env` (loaded by `app/core/config.py`). Current `.env`: `AI_PROVIDER=groq`, `GROQ_MODEL=openai/gpt-oss-20b` (code/config default is `qwen/qwen3.8-27b`), GROQ_API_KEY and GITHUB_TOKEN present, Neo4j creds default.
- Frontend: `cd frontend && npm run dev` (Vite, port 5173). `.env`: `VITE_API_BASE_URL=http://localhost:8000`.
- No Docker/Makefile/Procfile exists. No migration runner (Alembic absent); schema comes from `Base.metadata.create_all` at import plus the narrow additive `ensure_resume_cache_columns()` (`app/database/database.py:16–40`).
- **Runtime snapshot during audit:** PostgreSQL :5432 OPEN; Neo4j :7687 CLOSED; backend :8000 not running; Vite :5173 not running; Ollama :11434 closed (irrelevant — Groq selected).

## 3. Feature Inventory

Status legend: **Working** = wired end-to-end with passing tests; **Partial** = implemented but with verified gaps; **Broken** = verified defect prevents correct operation; **UI-only/Mock** = presents fabricated data; **Unverified** = code exists but no test/evidence of runtime correctness.

| #   | Feature                          | Frontend                                                                                        | API (prefix)                                                                                   | Backend core                                                                                  | AI / Data deps                                                   | Tests                                                             | Status                                                                                                                                                                    |
| --- | -------------------------------- | ----------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Auth (register/login/me)         | `pages/LoginPage.jsx`, `RegisterPage.jsx`, `context/AuthContext.jsx`, `services/authService.js` | `/auth/*`                                                                                      | `routers/auth.py`, `services/auth_service.py`                                                 | Postgres `users`, JWT                                            | `test_backend_stabilization.py` (pass)                            | Working                                                                                                                                                                   |
| 2   | Resume upload + parse            | `pages/ResumePage.jsx`, `services/careerService.js`                                             | `/resume/*`, `/parser/*`                                                                       | `services/resume_service.py`, `parser_service.py`, `parsers/resume_parser.py` + 7 sub-parsers | Postgres resumes/parsed_resumes; PyMuPDF; AI-store sync          | `test_resume_cache.py`, `test_resume_*_parser.py` (pass)          | Working (parsing is regex-heuristic; quality unverified)                                                                                                                  |
| 3   | Unified candidate profile        | `pages/ProfilePage.jsx` (`getProfileSnapshot`)                                                  | `/candidate-intelligence/unified-profile`                                                      | `services/unified_profile_service.py` (896 ln)                                                | Postgres + all source models                                     | `test_candidate_intelligence.py` (11 pass)                        | Working                                                                                                                                                                   |
| 4   | GitHub sync + repo understanding | `ProfilePage`, `ResumePage`, `IntelligencePage`                                                 | `/github/*`                                                                                    | `services/github_service.py`, `repository_understanding_service.py` (751 ln)                  | GitHub REST + token; LLM; `GitHubRepositoryDocument/File` models | `test_teaching_service.py` (pass, mocked)                         | Partial — code solid; live API unverified                                                                                                                                 |
| 5   | LeetCode / HackerRank sync       | `ProfilePage`, `DsaPracticePage`                                                                | `/leetcode/*`, `/hackerrank/*`                                                                 | `services/leetcode_service.py` (GraphQL), `hackerrank_service.py`                             | Public REST/GraphQL, freshness cache                             | `test_source_freshness.py` (pass)                                 | Partial — live unverified                                                                                                                                                 |
| 6   | LinkedIn                         | **none**                                                                                        | `/linkedin/*` (OAuth2 + sync)                                                                  | `services/linkedin_service.py` (294 ln)                                                       | LinkedIn OIDC                                                    | none dedicated                                                    | **Partial / unreachable** — no frontend code calls `/linkedin/*` (only `linkedin_summary?.connected` read at `ProfilePage.jsx:135`)                                       |
| 7   | Certifications                   | `ProfilePage` (upload, Drive import)                                                            | `/certifications/*`                                                                            | `services/certification_service.py` (1041 ln), `parsers/certificate_extractor.py`             | PyMuPDF extraction; platform sync                                | `test_certifications.py` (pass)                                   | Working (Drive import fetches a public URL; unverified live)                                                                                                              |
| 8   | Career Discovery                 | `pages/CareerDiscoveryPage.jsx` (`discoverCareers`)                                             | `POST /ai/career/recommend`                                                                    | `ai/agents/recommendation_agent.py` + prompt                                                  | LangGraph, ChromaDB, Neo4j, Groq                                 | `test_candidate_intelligence.py` (pass, mocked LLM)               | Working shell; groundedness depends on §6 degradation chain                                                                                                               |
| 9   | Skill Gap                        | `pages/SkillGapPage.jsx` (`getSkillGapAnalysis`)                                                | `POST /ai/career/skill-gap`; `POST /ai/skill-gap/analyze`; legacy `GET /skill-gap/{r}/{j}`     | `ai/agents/evaluation_agent.py`; `services/skill_gap_ai_service.py`; `skill_gap_service.py`   | LangGraph; role registry `ai/agents/role_requirements.py`        | `test_skill_gap_ai.py`, `test_skill_gap_frontend_logic.py` (pass) | Working                                                                                                                                                                   |
| 10  | Learning Roadmap                 | `pages/LearningRoadmapPage.jsx` (`getLearningRoadmap`)                                          | `/ai/skill-gap/analyze`, then **client-side fallback synthesis** in `careerService.js:131–211` | roadmap field produced by `skill_gap_ai_service`                                              | LangGraph                                                        | via skill-gap tests                                               | Partial — page rebuilds a roadmap client-side from skill-gap output when the roadmap array is empty; legacy `/career-roadmap/{r}/{j}` only used by old `IntelligencePage` |

| 11 | Career Quiz | `pages/CareerQuizPage.jsx` | `/ai/career/quiz/session*` (4 endpoints) | `services/profile_quiz_service.py` | RAG context + LLM; **hardcoded fallback questions** (`_fallback_questions`, line 115) | `test_profile_quiz.py` (pass) | Working (silently falls back to canned questions on LLM failure) |
| 12 | Interview Room (conversational) | `pages/InterviewPage.jsx` (2399 ln), `components/LiveInterviewStudio.jsx`, `InterviewModeSelection.jsx` | `/ai/career/interview/session*`, `/sessions`, `/questions/history`, `/cyra-chat`, `/resources-and-modes`, `PATCH …/language` | `services/conversational_interview_service.py` (3260 ln), `models/interview_session.py` | RAG, Neo4j evidence, LLM with one JSON-repair retry (`_provider_json`), 30-day cooldown/diversity loop, per-language localization | `test_conversational_interview.py` (16 tests, pass with fake providers) | Working per unit tests; live LLM behavior unverified |
| 13 | DSA Practice | `pages/DsaPracticePage.jsx` (2970 ln), `components/career/DsaPracticeModal.jsx` | `/leetcode/dsa-recommendations`, `/dsa-hint`, `/dsa/generate-rag`, `/dsa-evaluate` | `services/dsa_service.py` (1221 ln) | In-process Python `exec()` judge; **LLM judge fallback** for other languages; deterministic failure fallback | `test_dsa_interactive_hints.py` (**1 failing**), rest pass | **Broken aspects** — see §5 V3 |
| 14 | Teaching Studio | `pages/TeachingStudioPage.jsx` (1988 ln) exists | `/ai/career/teaching/*` (10 endpoints: curriculum, evaluate-and-teach, interact, progress, concept-map, knowledge-profile, skill-path, project-path, repository-understanding, chat) | `services/teaching_service.py` (2114 ln), `skill_learning_service.py`, `learner_knowledge_service.py`, `models/teaching_progress.py` | LLM + curated static curricula + repo documents | `test_teaching_service.py` (15 pass) | **Broken (UI unreachable)** — route + nav entry removed in uncommitted working-tree changes (§5 V1). Curriculum content is largely hardcoded lesson catalogs (`teaching_service.py:598+`, `skill_learning_service.py:28+`) |
| 15 | Career Intelligence | `pages/CareerIntelligencePage.jsx` | `POST /ai/career/intelligence` | full orchestrator → `MultiAgentResponse` | all AI stores | `test_candidate_intelligence.py` (pass) | Working shell; same grounding caveats |
| 16 | Multilingual (en/ta/hi/te/kn/ml + es/fr/de) | `services/speechService.js`, language pickers in Interview/Teaching pages | `language` field on all `/ai/career/*` requests | `ai/language/{detector,normalizer,prompt_builder}.py`, `schemas/language.py` (single source of truth: 9 codes) | Web Speech API TTS/STT (client-side only) | `test_multilingual_regression.py` (11), `test_multilingual_language_lifecycle.py` (4), FE `multilingualLifecycle.test.js`, `speechService.multilingual.test.js` (all pass) | Working per tests; model script-compliance and browser voice availability are platform-dependent (documented limitation) |
| 17 | Dashboard / Streaks | `pages/DashboardReimagined.jsx`, `services/activityTracker.js`, `components/MonthlyStreakTracker.jsx` | `/jobs/`, profile snapshot | `services/job_service.py` | localStorage only | `monthlyStreakTracker.test.jsx` (pass) | **UI-only / Mock** — `activityTracker.js:21–81` seeds ~60 days of _fabricated_ practice history for every fresh user; metrics are not backend-verified |
| 18 | Jobs CRUD | none (dashboard read-only `getJobs`) | `/jobs/*` incl. recruiter-only create/update/delete | `routers/job.py`, `core/dependencies.require_recruiter_or_admin` | Postgres `jobs` | `test_job_service.py` (pass) | Backend-only; no management UI |

**Dead/unreachable frontend code (verified by grep):** `pages/TeachingStudioPage.jsx` (unrouted after working-tree edit), `pages/DashboardPage.jsx` (superseded by `DashboardReimagined`), `components/Layout.jsx` (superseded by `LayoutReimagined`), `data/mockData.js` (no non-test importer).

## 4. Important End-to-End Workflows (verified by source tracing)

1. **Resume → AI grounding:** `ResumePage.uploadResume` → `POST /resume/upload` (`resume_service.upload_resume`: PDF-only, SHA-256 dedupe) → `POST /parser/parse/{id}` (`parser_service.parse_resume_by_id`, cache keyed on `content_hash` + `RESUME_PARSER_VERSION`) → writes `ParsedResume` → `sync_candidate_ai_stores_safe` → `unified_profile_service.build_unified_candidate_profile` → `ai/stores/candidate_store_sync.persist_candidate_ai_stores` → Chroma upsert (`candidate_{id}` doc) + Neo4j subgraph rebuild. Store failures are isolated and never roll back Postgres.
2. **Interview session lifecycle:** `createInterviewSession` (modes incl. `technical/dsa/sql/system_design/…`, `schemas/interview_session.py:8–24`) → `POST /ai/career/interview/session` → per turn `submit_interview_answer` (intent classification → LLM evaluation with `_fallback_evaluation` → `_generate_question_with_diversity` enforcing 30-day cooldown, concept dedupe, ≤3 retries → Postgres JSON transcript) → `complete_interview_session` → final report (with `_fallback_final_report`). Frontend persists `cv_active_session_id` and `?session_id=` for resume-on-refresh.
3. **Career AI query:** page → `careerService.aiRecommend / aiSkillGap / aiIntelligence` → `/ai/career/*` router (JWT-derived `candidate_id`; the frontend never supplies it) → `agents/service.run_career_intelligence` → `CareerOrchestrator.run` (LangGraph `app.invoke`) → `RAGContextBuilder` dual retrieval (Chroma `where={candidate_id}` + Neo4j subgraph) → agent prompts → provider JSON parse with one repair attempt (`_provider_json`) → typed Pydantic schemas. Errors map through `routers/ai.py::_handle_ai_error` (502/503/504/429 without leaking internals).
4. **DSA evaluation:** `DsaPracticePage` → `POST /leetcode/dsa-evaluate` → `dsa_service.evaluate_dsa_code_submission`: skeleton heuristic → Python in-process `exec` with restricted builtins (`dsa_service.py:1025–1047`) → else LLM judge → else deterministic failure response.
5. **Cyra chat:** `LiveInterviewStudio` → `POST /ai/career/interview/cyra-chat` → `generate_cyra_chat_response` (grounded prompt with multilingual mandate).

## 5. Verified Defects (evidence-backed)

**V1 — Teaching Studio UI was removed in the uncommitted working tree.** `git diff frontend/src/App.jsx` shows deletion of `import TeachingStudioPage` and of routes `/ai/teaching`, `/ai/teaching-studio`, `/teaching`; the `LayoutReimagined.jsx` diff shows removal of chapter nav “07 AI Teaching Room”. No other file references the page; visiting `/ai/teaching` now hits the `*` catch-all → redirect `/`. Ten backend `/ai/career/teaching/*` endpoints plus 15 passing backend tests back a feature with **zero UI access**. Regression relative to commit `ad70849`.

**V2 — Backend test suite: 1 failed / 121 passed (my run, 51 s).** `tests/test_dsa_interactive_hints.py::test_dsa_socratic_hint_dp_python` asserts `"return" not in res.hint.lower()`; the live Groq hint legitimately contains “return**ing**”. The test (a) depends on a live LLM call — `generate_dsa_interactive_hint` is not monkeypatched — and (b) its fixture `db.query(User).first()` silently returns `None` on a database without users. The “120/120 BE + 136/136 FE CLEAN” claim in commit `7037282` is not reproducible as-is.

**V3 — DSA judge integrity (`app/services/dsa_service.py`).**

- Fabricated metrics: `memoryMb="14.2"/"14.6"/"14.8"` and `time_complexity="O(N)"` hardcoded (lines 985–987, 1106–1109, 1213–1216); `runtimeMs` floor of 24 ms (line 1094).
- Skeleton heuristic (lines 957–965): **any** code containing the bare token `pass` (e.g. `except: pass`) is classified “starter skeleton” and fails every case with a canned error.
- Final fallback (lines 1193–1217) returns “Wrong Answer” with “candidate code produced invalid result” even when the code was never executed (non-Python language + LLM-judge failure).
- Execution is an unrestricted in-process `exec()` (line 1047) exposing `type`, with no timeout — see H1.

**V4 — Silent random-vector embedding fallback.** `app/ai/embeddings/encoder.py:58–68`: if SentenceTransformer fails to load or encode, `encode_text` returns an **md5-seeded random unit vector** instead of raising. Semantic search then “succeeds” with meaningless similarity, silently degrading every RAG-grounded feature.

**V5 — Silent Chroma in-memory fallback.** `app/ai/vector_store/chroma_client.py:45–53`: if `PersistentClient` init fails, an ephemeral in-memory client is used; `store_candidate` still returns a doc id and `candidate_store_sync` reports `chroma_status=success` — embeddings vanish on restart with no error surfaced.

**V6 — Neo4j permanent-unavailability caching.** `app/ai/knowledge_graph/neo4j_client.py:56–67`: `is_available()` caches `False` for the process lifetime (never retries), and `execute_query` returns `[]` on any error (lines 97–100). With Neo4j down on this machine (port 7687 closed), every graph retrieval is empty; `RAGContextBuilder` merely appends a warning string (`rag/context_builder.py:99–117`) and the pipeline proceeds as if grounded.

**V7 — Fabricated user activity.** `frontend/src/services/activityTracker.js:21–81` (`ensureSeededActivities`) writes ~60 days of invented DSA/interview/teaching activity into localStorage on first use; `DashboardReimagined` and `MonthlyStreakTracker` display these as real metrics.

**V8 — LinkedIn unreachable from the UI.** Full OAuth2 backend exists (`routers/linkedin.py`, `services/linkedin_service.py`) but zero frontend calls to `/linkedin/*` (grep-verified). Backend-only feature.

**V9 — Route-table damage.** `App.jsx:55`: `<Route path="/resume" from="/resume" …>` — `from` is not a valid react-router Route prop (ignored; route still matches, but it is editing damage). Duplicate `/interview` redirect definitions exist at `App.jsx:48` and `:68` (first match wins; confusing but functional).

**V10 — CWD-dependent upload storage.** `resume_service.UPLOAD_DIR = "uploads/resumes"` is relative; resume PDFs exist in _both_ `/uploads/resumes` and `/backend/uploads/resumes`, proving the server was started from different working directories. DB records point at paths that exist for only one CWD (`parser_service` then returns “Resume file not found on disk” for the other).

**V11 — Working tree ≠ reported state.** 25 modified files (multilingual prompts, `conversational_interview_service.py` +177 lines, `dsa_service.py`, `routers/ai.py`, schemas, FE pages) are uncommitted while the last commit claims “all checks CLEAN”. `TESTING_AUDIT_REPORT.md` (“100% PASS, 14 pytest / 104 vitest”) does not describe this tree (actual: 122 backend / 138 frontend tests collected today).

## 6. Suspected Issues (hypotheses — not yet proven)

- **H1:** In-process `exec()` of user code with `type` exposed and no timeout can hang the single `uvicorn --reload` worker (infinite loop) and is likely sandbox-escapable; any authenticated user can execute arbitrary Python in the server process.
- **H2:** Module-level caches in `careerService.js` (`profileSnapshot`, `resumeMetadata`) are only invalidated by same-tab mutations; multi-tab or external data changes serve stale data.
- **H3:** `frontend/dist/` (built 13 Oct) is stale versus src changes (14–15 Oct); any `vite preview`/static serving shows an outdated UI (possibly the version _with_ Teaching Studio), masking V1.
- **H4:** Config drift: default `GROQ_MODEL` (`qwen/qwen3.8-27b` in `config.py` and `.env.example`) ≠ `.env` value (`openai/gpt-oss-20b`); docs also quote obsolete language defaults (`SUPPORTED_LANGUAGES=en,ta,hi` in `.env.example` vs code default `en,ta,hi,te,kn,ml`).
- **H5:** Backend tests that hit live Groq (`test_dsa_interactive_hints.py`, cyra tests in `test_conversational_interview.py`) are network-, key-, and wording-dependent → inherently flaky (V2 is one instance).
- **H6:** `backend/test_e2e_pipeline.py` and `frontend/e2e_browser_test.cjs` / `e2e_assertive_verification.cjs` require live servers; any claims sourced from them in `research/` or `TESTING_AUDIT_REPORT.md` are unverifiable in the current environment.
- **H7:** SQLAlchemy `SAWarning: Identity map already had an identity … GitHubRepositoryDocument` at `repository_understanding_service.py:348` (observed during my test run) suggests duplicate-object flushes that could corrupt repo-document persistence under load.

## 7. Existing Test Coverage and Known Limitations

- **Backend:** 23 files in `backend/tests/` → 122 tests; my run: **121 passed, 1 failed, 8 warnings (51 s)**. Limitations: (1) 8 test files import `app.main`, and because `test_ai_foundation.py:3` sets `DATABASE_URL=sqlite:///./ai_foundation_test.db` first during collection, the whole suite runs on **SQLite, not the production PostgreSQL** — Postgres-specific behavior is untested; (2) import-time `create_all`/`ensure_resume_cache_columns` executes against that SQLite file; (3) several tests call the **live Groq API** and rely on pre-seeded DB rows.
- **Frontend:** 15 Vitest files → **138/138 passed (6.3 s)**; jsdom-based; covers multilingual, roadmap, quiz, DSA page, teaching studio, phase8 (65 tests), profile cache, streak tracker. Notable gap: tests import `TeachingStudioPage` directly, so they pass even though the page is unrouted (V1 is invisible to the suite).
- **E2E:** `backend/test_e2e_pipeline.py` (requests, needs `:8000`), `frontend/e2e_browser_test.cjs` / `e2e_assertive_verification.cjs` (Playwright + local Chrome, needs `:5173`) — not executed; not part of `npm test`/pytest defaults.
- **CI:** `.github/modernize/` contains rearchitecture docs only; no workflow files were observed running the suites.

## 8. Five Highest-Priority Investigation Targets

1. **Teaching Studio regression (V1).** Highest user-visible loss: a fully built, test-backed feature (10 endpoints, 15 tests, 1988-line page) is unreachable because of an uncommitted edit to `App.jsx`/`LayoutReimagined.jsx`. First decision point: intentional product removal or accident? Everything else about this feature is comparatively healthy.
2. **DSA judge correctness and sandboxing (V3/H1).** It both fabricates evidence (metrics, “Wrong Answer” verdicts without execution, false skeleton detection) and executes arbitrary user code in-process without timeout. Simultaneously a trust, security, and reliability defect — and the only currently failing backend test (V2) touches this module.
3. **The AI-grounding degradation chain (V4+V5+V6).** Random embeddings, in-memory Chroma fallback, and cached Neo4j unavailability each fail _silently_, so every “evidence-grounded” feature (discovery, skill gap, interview, quiz, intelligence) can quietly degrade to prompt-only LLM output while still reporting success. This single chain can explain most “the AI answer ignores my data” complaints.
4. **Test-suite validity (V2/H5).** The suite runs on SQLite instead of Postgres, exercises live LLMs in places, has a `None`-unsafe user fixture, and its results already contradict the “all green” claims in commits and `TESTING_AUDIT_REPORT.md`. Repair work needs a trustworthy baseline first (offline providers, seeded fixtures, a Postgres parity run).
5. **Configuration and state drift (V10/V11/H3/H4).** Uncommitted 25-file diff vs “CLEAN” commit, CWD-dependent upload paths, stale `dist/`, model-name drift between code/docs/env, and invalid Route props indicate mid-flight changes that were never re-verified end-to-end; they are the most likely source of “works on my machine” divergences for whoever runs this next.

## 9. Areas Not Inspected / Remaining Unknowns

- **Live runtime behavior:** backend and Vite servers were not running and were not started (read-only scope). No live HTTP request against the app was made; browser UX, WebRTC camera/mic flows, and TTS voice availability were not exercised.
- **Live external APIs:** Groq responses were observed only indirectly via the one test failure; GitHub/LeetCode/HackerRank/LinkedIn responses and rate limits were never called; the `GITHUB_TOKEN` was not validated.
- **Real PostgreSQL schema/data:** never connected to `careerverse_db`; the test suite itself substituted SQLite. Row-level data and whether `ensure_resume_cache_columns` has run against Postgres remain unknown.
- **Neo4j graph content:** server unreachable; only code-path analysis performed (`graph_builder`/`concept_graph_service` internals read only superficially).
- **Partially read services:** `teaching_service.py` lines ~700–2114 (evaluate/interact/chat), `repository_understanding_service.py` internals, `learner_knowledge_service.py`, `unified_profile_service.py` merge details, and the full bodies of `InterviewPage.jsx` / `DsaPracticePage.jsx` were analyzed at API-surface level only.
- **LLM output quality:** prompt effectiveness, multilingual compliance of `openai/gpt-oss-20b`, and grounding fidelity were not empirically evaluated.
- **Untracked docs** (`.agents/tasks/*`, `research/*`, `RESEARCH_PAPER_*`, `TESTING_AUDIT_REPORT.md`) were skimmed for orientation only; no claim from them is relied upon above without a source-code citation.
