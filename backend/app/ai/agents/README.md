# LangGraph Multi-Agent Workflows (`app/ai/agents`)

The `app/ai/agents` module implements a stateful, cyclic multi-agent orchestration architecture built using **LangGraph**. It replaces brittle single-prompt chains with specialized, cooperating agents that share a validated `AgentState`.

---

## 🤖 Agent Roles & Responsibilities

| Agent Component | Implementation File | Key Responsibilities |
| :--- | :--- | :--- |
| **Multi-Agent Orchestrator** | `orchestrator.py` | Compiles the LangGraph `StateGraph`, manages workflow state transitions, coordinates parallel sub-agent executions, and aggregates outputs. |
| **Recommendation Agent** | `recommendation_agent.py` | Analyzes candidate evidence (projects, repos, algorithms, experience) and matches against industry job roles with confidence scores and rationale. |
| **Evaluation Agent** | `evaluation_agent.py` | Compares candidate skills against target role benchmarks; identifies demonstrated, partial, and missing skills with gap severity ratings. |
| **Interview Preparation Agent** | `interview_agent.py` | Generates grounded interview questions (algorithmic, architecture, scenario), evaluates candidate answers, and generates adaptive follow-ups. |
| **Synthesis Agent** | `synthesis_agent.py` | Synthesizes multi-agent outputs into an executive Career Intelligence briefing. |
| **Task Router** | `task_router.py` | Inspects user query intent and context to route execution to the optimal specialized workflow path. |
| **Role Requirements Repository** | `role_requirements.py` | Provides industry-standard competency benchmarks for software engineering, data science, DevOps, and AI roles. |

---

## 🔄 LangGraph Workflow Graph

```
                   ┌──────────────┐
                   │  User Query  │
                   └──────┬───────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   Task Router    │
                 └────────┬─────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
   [Recommend]       [Evaluate]       [Interview]
   (Discovery)       (Skill Gap)      (Alex Room)
         │                │                │
         └────────────────┼────────────────┘
                          ▼
               ┌─────────────────────┐
               │   Synthesis Agent   │
               └──────────┬──────────┘
                          │
                          ▼
                 Structured Response
```

---

## 📝 Agent State Model (`state.py`)

All agents operate over a shared, typed `AgentState` containing:
- `candidate_id`: Authenticated user ID (strictly resolved from JWT)
- `query`: Candidate or recruiter question/prompt
- `target_role`: Target job title (e.g., "Backend Developer")
- `language`: Target language code (`en`, `ta`, `hi`)
- `retrieved_context`: Fused evidence from ChromaDB and Neo4j
- `recommendations`: Discovered role alternatives
- `skill_gaps`: Structured gap analysis and improvement priorities
- `interview_questions`: Grounded interview challenges with follow-ups
- `execution_status`: Status tracker (`success`, `partial_fallback`, `error`)

---

## 💡 Key Entrypoints (`service.py`)

The high-level functions called by FastAPI routers include:
- `run_career_recommendation(candidate_id, query, language)`
- `run_skill_gap_evaluation(candidate_id, target_role, query, language)`
- `run_interview_preparation(candidate_id, query, target_role, language)`
- `run_multi_agent_career_intelligence(candidate_id, query, target_role, language)`
