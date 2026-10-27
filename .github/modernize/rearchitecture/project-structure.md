# Project structure

- Project type: fullstack application with a React/Vite frontend and FastAPI backend.
- Frontend entrypoints: `frontend/src/main.jsx`, `frontend/src/App.jsx`.
- Frontend layers: route/page components, shared layout/components, design-system primitives, contexts, service adapters, and tests.
- Major user areas: authentication, profile evidence, resume parsing, career discovery, skill-gap analysis, learning roadmap, interview practice, and career intelligence.
- Backend layers: FastAPI routers, service layer, SQLAlchemy models, schemas, AI agents/providers, and vector/knowledge-graph stores.
- The redesign boundary is the authenticated frontend shell and chapter pages; backend APIs remain the source of truth.
