import { useState } from "react";
import {
  FileText,
  GitBranch,
  Code2,
  Award,
  Database,
  Share2,
  Sparkles,
  Bot,
  Compass,
  Layers3,
  Route,
  Mic,
  Brain,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";

const PIPELINE_STEPS = [
  {
    id: "sources",
    step: "01",
    title: "Multi-Touchpoint Ingestion",
    subtitle: "Real Candidate Evidence",
    icon: Database,
    color: "#6366f1",
    description:
      "Gathers authenticated data across 5 distinct touchpoints: Resumes (OCR parsed), GitHub (repos & languages), LeetCode (problem metrics), HackerRank (verified badges), and Certifications.",
    metrics: [
      { label: "Sources", val: "5 Integrated Touchpoints" },
      { label: "Parsing", val: "Strict OCR & Regex Filters" },
      { label: "Isolation", val: "Candidate JWT Scoped" },
    ],
    pills: ["Resume PDF", "GitHub Repos", "LeetCode Stats", "HackerRank Badges", "Certifications"],
  },
  {
    id: "stores",
    step: "02",
    title: "Dual-Engine Representation",
    subtitle: "ChromaDB + Neo4j Graph",
    icon: Share2,
    color: "#8b5cf6",
    description:
      "Structured data is stored in PostgreSQL, dense candidate representations are embedded via sentence-transformers into ChromaDB, and interconnected skill-project relationships are mapped into Neo4j subgraphs.",
    metrics: [
      { label: "Embeddings", val: "384-dim MiniLM-L6" },
      { label: "Graph Nodes", val: "(Candidate)-[:HAS_SKILL]->(Skill)" },
      { label: "Consistency", val: "Auto-synced on Update" },
    ],
    pills: ["PostgreSQL", "ChromaDB Vector Store", "Neo4j Knowledge Graph"],
  },
  {
    id: "rag",
    step: "03",
    title: "Grounded RAG Context",
    subtitle: "Zero Hallucination Retrieval",
    icon: ShieldCheck,
    color: "#ec4899",
    description:
      "Combines semantic similarity from Chroma vectors with structured multi-hop graph traversals from Neo4j. The LLM receives only verified profile facts—preventing fabricated experience.",
    metrics: [
      { label: "Hybrid RAG", val: "Semantic + Structural" },
      { label: "Grounding", val: "100% Evidence Based" },
      { label: "Relevance", val: "Top-k Context Scoring" },
    ],
    pills: ["Semantic Matching", "Graph Traversal", "Unified Context Window"],
  },
  {
    id: "multi_agent",
    step: "04",
    title: "LangGraph Multi-Agent Team",
    subtitle: "Autonomous Agent Execution",
    icon: Bot,
    color: "#3b82f6",
    description:
      "Task router dispatches queries to specialized AI agents: Profile Analyst, Career Navigator, Skill Gap Analyst, Career Pathfinder, and Alex the Conversational Interviewer.",
    metrics: [
      { label: "Orchestration", val: "LangGraph StateGraph" },
      { label: "Persona", val: "Alex (Live Interviewer)" },
      { label: "Model", val: "qwen2.5:3b (Ollama)" },
    ],
    pills: [
      "Career Navigator",
      "Skill Gap Analyst",
      "Alex Interviewer",
      "Pathfinder Roadmap",
    ],
  },
  {
    id: "synthesis",
    step: "05",
    title: "Career Intelligence Synthesis",
    subtitle: "Actionable Career Strategy",
    icon: Sparkles,
    color: "#10b981",
    description:
      "The Synthesis Agent unifies all agent deductions into an executive career strategy: validated directions, prioritized skill gaps, sequential roadmap stages, and personalized interview insights.",
    metrics: [
      { label: "Output", val: "Executive Strategy Report" },
      { label: "Actionability", val: "Step-by-Step Milestones" },
      { label: "Traceability", val: "Source-Linked Evidence" },
    ],
    pills: ["Executive Summary", "Grounded Milestones", "Interview Insights", "Next Focus"],
  },
];

export default function HowCareerVerseWorks() {
  const [activeStep, setActiveStep] = useState(0);
  const current = PIPELINE_STEPS[activeStep];

  return (
    <section className="panel-card how-it-works-section" aria-labelledby="how-it-works-title">
      <div className="how-it-works-header">
        <div>
          <span className="eyebrow">
            <Sparkles size={14} className="icon-sparkle" /> Architectural Pipeline
          </span>
          <h2 id="how-it-works-title">How CareerVerse AI Works</h2>
          <p className="section-description">
            A continuous loop transforming raw multi-source evidence into personalized, grounded career intelligence.
          </p>
        </div>
      </div>

      {/* Pipeline Step Indicators */}
      <div className="pipeline-steps-nav" role="tablist" aria-label="Architecture Pipeline Steps">
        {PIPELINE_STEPS.map((s, idx) => {
          const StepIcon = s.icon;
          const isActive = idx === activeStep;
          return (
            <button
              key={s.id}
              role="tab"
              aria-selected={isActive}
              className={`pipeline-step-btn ${isActive ? "active" : ""}`}
              onClick={() => setActiveStep(idx)}
              type="button"
            >
              <div className="step-btn-top">
                <span className="step-num">{s.step}</span>
                <span className="step-icon-wrap" style={{ color: s.color }}>
                  <StepIcon size={16} />
                </span>
              </div>
              <strong className="step-btn-title">{s.title}</strong>
              <small className="step-btn-sub">{s.subtitle}</small>
            </button>
          );
        })}
      </div>

      {/* Active Step Showcase */}
      <div className="pipeline-detail-card" style={{ borderColor: `${current.color}40` }}>
        <div className="pipeline-detail-header">
          <div className="pipeline-detail-title-group">
            <span className="pipeline-step-badge" style={{ backgroundColor: `${current.color}15`, color: current.color }}>
              Stage {current.step}
            </span>
            <h3>{current.title}</h3>
            <p className="pipeline-detail-sub">{current.subtitle}</p>
          </div>
          <div className="pipeline-nav-arrows">
            <button
              className="ghost-button"
              disabled={activeStep === 0}
              onClick={() => setActiveStep((prev) => Math.max(0, prev - 1))}
              type="button"
            >
              Previous
            </button>
            <button
              className="primary-button"
              disabled={activeStep === PIPELINE_STEPS.length - 1}
              onClick={() => setActiveStep((prev) => Math.min(PIPELINE_STEPS.length - 1, prev + 1))}
              type="button"
            >
              Next Stage <ArrowRight size={14} />
            </button>
          </div>
        </div>

        <p className="pipeline-detail-description">{current.description}</p>

        {/* Live Architecture Metrics */}
        <div className="pipeline-metrics-grid">
          {current.metrics.map((m) => (
            <div className="pipeline-metric-box" key={m.label}>
              <span className="metric-label">{m.label}</span>
              <strong className="metric-val">{m.val}</strong>
            </div>
          ))}
        </div>

        {/* Tech / Entity Pills */}
        <div className="pipeline-pills-row">
          {current.pills.map((p) => (
            <span className="pipeline-pill" key={p}>
              <CheckCircle2 size={13} style={{ color: current.color }} /> {p}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
