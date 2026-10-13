import { Link } from "react-router-dom";
import {
  BrainCircuit,
  ArrowRight,
  User,
  Sparkles,
  Compass,
  Target,
  Milestone,
  Mic,
  CheckCircle2,
  FileText,
  GitBranch,
  Code2,
  Award,
  Layers,
  Bot,
  HelpCircle,
} from "lucide-react";

const journeySteps = [
  {
    step: "01",
    title: "Profile",
    desc: "Aggregate resume, GitHub, LeetCode, and certifications.",
    icon: User,
  },
  {
    step: "02",
    title: "Assess",
    desc: "Take a personalized assessment grounded in your background.",
    icon: Sparkles,
  },
  {
    step: "03",
    title: "Discover",
    desc: "Find career roles matching your verified skills & projects.",
    icon: Compass,
  },
  {
    step: "04",
    title: "Find Skill Gaps",
    desc: "Compare your evidence against real job role requirements.",
    icon: Target,
  },
  {
    step: "05",
    title: "Build Roadmap",
    desc: "Follow structured milestone stages with practical tasks.",
    icon: Milestone,
  },
  {
    step: "06",
    title: "Practice Interview",
    desc: "Simulate text & voice interviews with adaptive follow-ups.",
    icon: Mic,
  },
  {
    step: "07",
    title: "Career Intelligence",
    desc: "Receive synthesized executive strategy & readiness reports.",
    icon: BrainCircuit,
  },
];

const aiAgents = [
  {
    id: "agent-1",
    title: "Career Profile Agent",
    role: "Profile Intelligence & Verification",
    desc: "Extracts and unifies candidate evidence across resumes, GitHub repositories, coding platforms, and certifications.",
    icon: User,
  },
  {
    id: "agent-2",
    title: "Career Recommendation Agent",
    role: "Semantic Role Matching",
    desc: "Identifies top career paths and roles using LangGraph semantic search, vector embeddings, and Neo4j Knowledge Graph retrieval.",
    icon: Compass,
  },
  {
    id: "agent-3",
    title: "Skill Gap Analyst",
    role: "Evidence-Based Gap Evaluation",
    desc: "Evaluates demonstrated skills against target job specifications to highlight critical missing skills and strengths.",
    icon: Target,
  },
  {
    id: "agent-4",
    title: "Learning Roadmap Agent",
    role: "Actionable Learning Path Generation",
    desc: "Generates multi-stage learning roadmaps complete with prerequisites, estimated effort, and practical project builds.",
    icon: Milestone,
  },
  {
    id: "agent-5",
    title: "Interview Strategist",
    role: "Targeted Question Formulator",
    desc: "Formulates role-based, skill-gap-focused, and project-grounded questions tailored to candidate weak spots.",
    icon: HelpCircle,
  },
  {
    id: "agent-6",
    title: "Virtual AI Interviewer",
    role: "Conversational Interview Simulation",
    desc: "Conducts realistic interactive interviews in text or browser voice mode with adaptive follow-ups in English, Tamil, and Hindi.",
    icon: Mic,
  },
  {
    id: "agent-7",
    title: "Interview Evaluator",
    role: "Real-Time Answer Assessment",
    desc: "Assesses response quality and technical depth after each answer, highlighting specific strengths and improvement areas.",
    icon: CheckCircle2,
  },
  {
    id: "agent-8",
    title: "Career Intelligence Synthesizer",
    role: "Executive Strategy Coordination",
    desc: "Synthesizes inputs from all multi-agent workflows into a unified career intelligence and interview readiness report.",
    icon: BrainCircuit,
  },
];

const dataSources = [
  { name: "Resume PDF", icon: FileText, desc: "NLP parsing & entity extraction" },
  { name: "GitHub", icon: GitBranch, desc: "Repositories, languages & readme sync" },
  { name: "LeetCode", icon: Code2, desc: "Problem difficulty breakdown & rankings" },
  { name: "HackerRank", icon: Award, desc: "Verified skill badges & certificates" },
  { name: "Certifications", icon: Layers, desc: "Verified professional credentials" },
  { name: "Career Goals", icon: Target, desc: "Target job roles & aspirations" },
];

export default function LandingPage() {
  return (
    <div className="landing-page">
      {/* Top Navigation */}
      <header className="landing-nav">
        <div className="landing-brand">
          <div className="brand-logo-icon" aria-hidden="true">
            <BrainCircuit size={22} />
          </div>
          <div>
            <div className="brand-name">CareerVerse AI</div>
            <div className="brand-subtitle">AI Career Intelligence</div>
          </div>
        </div>

        <nav className="landing-nav-links" aria-label="Landing Page Navigation">
          <a href="#journey" className="landing-nav-link">Career Journey</a>
          <a href="#agents" className="landing-nav-link">AI Career Team</a>
          <a href="#sources" className="landing-nav-link">Connected Sources</a>
        </nav>

        <div className="landing-nav-actions">
          <Link to="/login" className="ghost-button">
            Sign In
          </Link>
          <Link to="/register" className="primary-button">
            Get Started <ArrowRight size={15} aria-hidden="true" />
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="landing-hero" id="hero">
        <div className="hero-pill-badge">
          <Bot size={14} aria-hidden="true" />
          Multi-Agent Career Intelligence Platform
        </div>

        <h1 className="hero-headline">
          Evidence-grounded career intelligence for <span>your next career move</span>.
        </h1>

        <p className="hero-subtitle">
          CareerVerse AI is an AI-powered career intelligence platform that understands your profile,
          discovers suitable career paths, identifies missing skills, builds a learning roadmap,
          and prepares you for interviews.
        </p>

        <div className="hero-cta-row">
          <Link to="/register" className="primary-button" style={{ padding: "12px 24px", fontSize: "1rem" }}>
            Analyze My Career <ArrowRight size={16} aria-hidden="true" />
          </Link>
          <a href="#journey" className="ghost-button" style={{ padding: "12px 22px", fontSize: "1rem" }}>
            Explore Career Journey
          </a>
        </div>
      </section>

      {/* Career Journey Section */}
      <section className="landing-section" id="journey">
        <div className="journey-preview-container">
          <div className="journey-track-header">
            <div className="eyebrow">The CareerVerse Journey</div>
            <h2 className="section-title">From Candidate Profile to Career Progress</h2>
            <p className="section-description">
              A continuous loop of evidence discovery, skill validation, actionable learning, and interview preparation.
            </p>
          </div>

          <div className="journey-step-flow">
            {journeySteps.map((step) => {
              const Icon = step.icon;
              return (
                <div key={step.step} className="journey-node-card">
                  <span className="journey-node-step">STEP {step.step}</span>
                  <Icon className="journey-node-icon" aria-hidden="true" />
                  <div className="journey-node-title">{step.title}</div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* AI Career Team Architecture */}
      <section className="landing-section" id="agents">
        <div className="section-header" style={{ textAlign: "center", maxWidth: 700, margin: "0 auto 32px auto" }}>
          <div className="eyebrow">Multi-Agent AI Architecture</div>
          <h2 className="section-title">Your Dedicated AI Career Team</h2>
          <p className="section-description">
            Eight specialized LangGraph agents collaborate in real time to analyze your evidence,
            recommend roles, diagnose skill gaps, and run adaptive interview simulations.
          </p>
        </div>

        <div className="agent-team-grid">
          {aiAgents.map((agent) => {
            const Icon = agent.icon;
            return (
              <div key={agent.id} className="agent-team-card">
                <div className="agent-card-icon-wrap" aria-hidden="true">
                  <Icon size={20} />
                </div>
                <div className="agent-card-title">{agent.title}</div>
                <div className="agent-card-desc">{agent.desc}</div>
                <div className="agent-card-meta">{agent.role}</div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Connected Data Sources */}
      <section className="landing-section" id="sources">
        <div className="section-header" style={{ textAlign: "center", maxWidth: 700, margin: "0 auto 32px auto" }}>
          <div className="eyebrow">Unified Multi-Source Signals</div>
          <h2 className="section-title">Connected Evidence, Zero Guesswork</h2>
          <p className="section-description">
            CareerVerse AI pulls real signals across your engineering footprint to ground all AI recommendations in factual candidate data.
          </p>
        </div>

        <div className="sources-grid">
          {dataSources.map((source) => {
            const Icon = source.icon;
            return (
              <div key={source.name} className="source-item-card">
                <Icon className="source-item-icon" aria-hidden="true" />
                <div className="source-item-name">{source.name}</div>
                <p className="section-description" style={{ fontSize: "0.75rem" }}>{source.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div>
            <strong>CareerVerse AI</strong> · Evidence-grounded career intelligence
          </div>
          <div>
            FastAPI · LangGraph · ChromaDB · Neo4j · React
          </div>
        </div>
      </footer>
    </div>
  );
}
