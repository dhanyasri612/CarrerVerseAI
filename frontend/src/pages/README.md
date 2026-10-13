# Frontend Pages & Editorial Chapters (`src/pages`)

The `src/pages` directory contains the top-level route views in CareerVerse AI. The platform is organized around an **Editorial Chapter Narrative**, where each chapter guides the candidate from baseline evidence to active interview readiness.

---

## 📖 Chapter Guide & Page Catalog

| Chapter / Page | File | Route | Description |
| :--- | :--- | :--- | :--- |
| **Landing & Onboarding** | `LandingPage.jsx` | `/` | Introduction to CareerVerse AI; presents platform capabilities and chapter journey. |
| **Authentication** | `LoginPage.jsx`<br>`RegisterPage.jsx` | `/login`<br>`/register` | User registration and login forms with real-time validation and JWT session handling. |
| **Chapter 01: Your Story** | `ProfilePage.jsx` | `/profile` | Comprehensive Candidate Dossier combining parsed resume credentials, connected GitHub repos, LeetCode stats, HackerRank badges, and certifications. |
| **Chapter 02: Your Options** | `CareerDiscoveryPage.jsx` | `/discovery`<br>`/career-navigator` | Explores grounded career directions derived from candidate signals, with fit scores, rationales, and deep links to gap analyses. |
| **Chapter 03: Career Compass** | `CareerQuizPage.jsx` | `/career-quiz`<br>`/quiz` | Reflective situational assessment diagnosing architectural instincts, trade-off preferences, and leadership inclination. |
| **Chapter 04: Your Gaps** | `SkillGapPage.jsx` | `/skill-gap` | Two-column diagnostic comparing verified candidate evidence against target role requirements. Features clickable "Prep Guide" modals with resources. |
| **Chapter 05: Your Journey** | `LearningRoadmapPage.jsx` | `/career-roadmap`<br>`/roadmap` | Interactive learning roadmap supporting 3 view modes:<br>1. **roadmap.sh Tech Tree** (interactive node graph)<br>2. **Pipeline Flowchart** (visual stage highway)<br>3. **Curriculum Guide** (editorial mission checklist). |
| **Chapter 06: Alex Interview Room** | `InterviewPage.jsx` | `/interview`<br>`/ai/interview` | Conversational technical interview room. Features voice audio synthesis, code workbench, multi-turn adaptive follow-ups, topic filters, and Tanglish/Hinglish support. |
| **DSA Practice Workbench** | `DsaPracticePage.jsx` | `/dsa-practice` | Live algorithmic problem-solving environment with code editor, test case execution, incremental hint assistance, and complexity analysis. |
| **Career Intelligence** | `CareerIntelligencePage.jsx` | `/ai/intelligence` | Executive report synthesized by the LangGraph multi-agent workflow, combining roles, gaps, and interview prep. |
| **Resume Studio** | `ResumePage.jsx` | `/resume` | PDF resume upload, parsing inspection, and extraction preview. |

---

## 🧭 Navigation & Session Flow

```
   [Register / Login]
           │
           ▼
[Chapter 01: Your Story] (/profile)
  ├── Upload Resume & Parse
  └── Connect LeetCode & GitHub
           │
           ▼
[Chapter 02: Your Options] (/discovery)
  └── Select Target Career Role
           │
           ├──────────────────────────┐
           ▼                          ▼
[Chapter 03: Career Compass]   [Chapter 04: Your Gaps]
  (/career-quiz)                 (/skill-gap)
           │                          │
           └────────────┬─────────────┘
                        ▼
           [Chapter 05: Your Journey]
             (/career-roadmap)
             - Tech Tree Graph
             - Milestone Missions
                        │
                        ▼
           [Chapter 06: Interview Room]
             (/interview)
             - Alex AI Conversational Room
             - DSA Code Workbench
                        │
                        ▼
           [Career Intelligence Report]
             (/ai/intelligence)
```

---

## 🎨 Consistent Chapter Elements

Every chapter page incorporates standard editorial components:
- **Chapter Kicker & Number:** e.g., `04  /  Your Journey`
- **Main Headline & Deck:** Publication-style serif typography and descriptive summary.
- **Direction Selector:** Interactive role pills for switching target careers.
- **Grounding Disclosures:** Clarifies which verified sources informed the displayed output.
- **Chapter Footer Navigation:** Seamless bidirectional links between sequential chapters (e.g., `<- Chapter 03` / `Chapter 05 ->`).
