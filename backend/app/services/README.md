# Business Services & Domain Logic (`app/services`)

The `app/services` module implements the core business logic, profile intelligence aggregation, interview session state machines, and external integrations for CareerVerse AI. Routers remain thin controllers, delegating operations to this service layer.

---

## 💼 Service Modules Catalog

| Service Module | File | Responsibilities |
| :--- | :--- | :--- |
| **Conversational Interview Engine** | `conversational_interview_service.py` | Manages multi-turn interview room state machines, evaluates candidate answers, enforces adaptive follow-ups, calculates topic rubrics, and generates final evaluation dossiers. |
| **DSA Interactive Workbench** | `dsa_service.py` | Supplies data structure & algorithm coding challenges, test case evaluation, step-by-step hint progression, and time/space complexity analysis. |
| **Unified Profile Synthesizer** | `unified_profile_service.py` | Merges fragmented signals (resume, GitHub, LeetCode, HackerRank, certifications, basic profile) into a canonical unified candidate profile. |
| **Certification & Credential Ingestion** | `certification_service.py` | Extracts metadata from uploaded certificate PDFs via PyMuPDF, dedupes overlapping credentials, and queries verification endpoints. |
| **Source Freshness & External Sync** | `github_service.py`<br>`leetcode_service.py`<br>`hackerrank_service.py`<br>`linkedin_service.py` | Connects to external developer platforms. Enforces a 24-hour TTL freshness policy (`SYNC_FRESHNESS = timedelta(hours=24)`), returning cached data during valid windows and refreshing when stale. |
| **Career Compass / Quiz Service** | `profile_quiz_service.py` | Coordinates situational diagnostic sessions, advances question sequences, and maps responses to cognitive career archetypes. |
| **Skill Gap & Roadmap Services** | `skill_gap_ai_service.py`<br>`career_roadmap_service.py` | Resolves required competencies from benchmark roles, aggregates verified candidate evidence, and generates progressive milestones. |
| **Resume Extraction & Parser** | `parser_service.py`<br>`resume_service.py` | PDF parsing, regex section segmentation, and structured skill extraction. |

---

## ⏱️ Source Freshness & Caching Policy

To prevent third-party rate limiting (e.g., GitHub, LeetCode, HackerRank) and reduce latency, external platform syncs implement intelligent freshness checking:

```python
SYNC_FRESHNESS = timedelta(hours=24)

def _is_fresh(profile, target_username) -> bool:
    if not profile or profile.username.lower() != target_username.lower():
        return False
    age = datetime.utcnow() - profile.updated_at
    return age < SYNC_FRESHNESS
```

- **Normal Request:** If profile was refreshed within the last 24 hours, cached records are returned immediately.
- **Forced Request:** When requested with `?force=true`, the service bypasses the cache and queries live external APIs.
