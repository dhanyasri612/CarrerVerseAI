# CareerVerse AI — Frontend Application

The **CareerVerse AI Frontend** is a modern, responsive web application built with **React 18** and **Vite**. It features a publication-grade **Editorial Design System** that presents career navigation as a progressive journey divided into six chapters.

---

## 🎨 Editorial Design System & Styling Architecture

The user interface uses custom CSS variables and utility classes defined in `src/index.css`:

```
┌────────────────────────────────────────────────────────┐
│ CHAPTER 02                                             │
│ 02  /  Your Options                                    │
│ Your experience does not point to one future.          │
│ Explore possible directions as questions about fit...   │
└────────────────────────────────────────────────────────┘
```

### Core Design Tokens (`cv-` namespace):
- `--cv-paper`: Crisp archival background (`#faf7f2` in light / `#0c0d0e` in dark mode).
- `--cv-ink`: High-contrast editorial ink typography (`#1f1d1a` / `#f0eee9`).
- `--cv-accent`: Refined evergreen accent (`#16a34a`).
- `--cv-rule`: Subtle divider borders (`#e8e4dc` / `#232528`).
- `--cv-font-serif`: Heading typography with editorial gravitas.
- `--cv-font-mono`: Monospace styling for code workbench and timestamps.

### Key Layout Primitives:
- `.cv-chapter-intro`: Editorial header displaying chapter number, kicker, headline, and deck.
- `.cv-editorial-section`: Structured section with left-aligned section index (e.g. `01 / WHAT YOU BRING`) and right-aligned content area.
- `.cv-evidence-lines` / `.cv-evidence-line`: Two-column key-value ledger displaying verified candidate evidence.
- `.cv-note-block`: Callout container for AI status disclosures and grounding notes.

---

## 📂 Directory Layout

```
frontend/
├── src/
│   ├── main.jsx                     # Application bootstrap & React 18 createRoot
│   ├── App.jsx                      # Route definitions & AuthProvider wrapper
│   ├── index.css                    # Master editorial design system & CSS tokens
│   ├── pages/                       # Chapter pages (see pages/README.md)
│   ├── components/                  # Reusable UI & visualization components
│   │   ├── AsyncState.jsx           # LoadingState, ErrorState, EmptyState primitives
│   │   ├── Navbar.jsx               # Editorial navigation bar & chapter indicator
│   │   ├── roadmap/                 # TechTree & Pipeline flowchart views
│   │   └── career/                  # Skill prep guides, interview modals
│   ├── services/                    # API client layer
│   │   ├── api.js                   # Axios instance with JWT interceptor & error parsing
│   │   └── careerService.js         # Domain API bindings & caching utilities
│   ├── context/
│   │   └── AuthContext.jsx          # JWT session management & user state
│   └── test/                        # Vitest integration test suites (86 tests)
├── package.json                     # NPM scripts & dependencies
└── vite.config.js                   # Vite configuration
```

---

## 🚀 Running Locally & Scripts

```bash
# 1. Install Dependencies
npm install

# 2. Run Vite Development Server (Port 5173)
npm run dev

# 3. Run Automated Tests with Vitest (86 tests)
npm test

# 4. Compile Production Build
npm run build
```

---

## 🧪 Frontend Test Suites (`src/test/`)

The frontend includes 86 automated integration tests across 8 test suites:

- `phase8.test.jsx`: 65 comprehensive integration tests covering recommendation UI, skill gap layouts, conversational interview flows, multi-agent intelligence, and auth tokens.
- `careerIntelligence.test.jsx`: Tests multi-agent intelligence report rendering.
- `careerNavigator.test.jsx`: Tests Career Discovery direction cards, fit score rendering, and evidence fallbacks.
- `careerQuiz.test.jsx`: Tests Career Compass quiz questions, answer submissions, and result synthesis.
- `skillGap.test.jsx`: Tests evidence-grounded skill gap analysis and target role switching.
- `learningRoadmap.test.jsx`: Tests roadmap chapter views, view mode switching (TechTree, Pipeline, Curriculum), and retry states.
- `dsaPracticePage.test.jsx`: Tests DSA workbench controls.
- `profileCache.test.js`: Tests frontend client profile caching.

---

## 📖 Chapter Pages Documentation

For detailed guides on each page in the application, see the [Pages Documentation](file:///Users/dhanyasrik/Projects/CarrerVerseAI/frontend/src/pages/README.md).
