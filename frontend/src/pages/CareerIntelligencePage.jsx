import React, { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  ArrowRight,
  BookOpen,
  Brain,
  Check,
  CheckCircle2,
  Copy,
  ExternalLink,
  FileText,
  GitBranch,
  Layers3,
  Printer,
  RefreshCw,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  Target,
  UserRound,
  Zap,
} from "lucide-react";
import { EmptyState, ErrorState } from "../components/AsyncState";
import { getApiError } from "../services/api";
import { aiIntelligence, getProfileSnapshot } from "../services/careerService";
import { useAIActivity } from "../context/AIActivityContext";
import { marked } from "marked";
import "../careerIntelligence.css";

function formatMarkdownReport(input) {
  if (!input) return "";
  let text = String(input).replace(/\\n/g, "\n");

  // 1. Separate headings followed immediately by table or text:
  // e.g. "## Verified Facts (from the retrieved context) | Item | Detail | Confidence |"
  text = text.replace(/(#{1,4}[^\n\|]+?)\s*\|\s*([A-Za-z])/g, "$1\n\n| $2");

  // 2. If a heading is preceded by non-newline characters:
  text = text.replace(/([^\n\s])\s+(#{1,4}\s+)/g, "$1\n\n$2");

  // 3. Separate blockquotes (e.g. "| > *Note:*" or "text > *Note:*")
  text = text.replace(/\|\s*>\s*/g, "|\n\n> ");
  text = text.replace(/([^\n\s])\s+(>\s*\*?Note\*?:?)/g, "$1\n\n$2");

  // 4. Separate horizontal rules (e.g. "text --- ## Heading" or "| --- ## Heading")
  text = text.replace(/\|\s+---\s+(#{1,4}|[A-Za-z])/g, "|\n\n---\n\n$1");
  text = text.replace(/([A-Za-z0-9\.\>])\s+---\s+(#{1,4}|[A-Za-z])/g, "$1\n\n---\n\n$2");

  // 5. In tables: insert newline between rows (| |)
  text = text.replace(/\|\s*\|\s*/g, "|\n| ");

  // 6. Separate list items after headings or text (e.g. "### Caveats - The current profile...")
  text = text.replace(/(#{1,4}[^\n]+?)\s*-\s+([A-Za-z])/g, "$1\n\n- $2");
  text = text.replace(/([^\n])\s+-\s+([A-Za-z])/g, "$1\n- $2");

  return text.trim();
}

function MarkdownReport({ content, className = "" }) {
  const cleaned = content ? formatMarkdownReport(content) : "";
  const html = useMemo(() => {
    if (!cleaned) return "";
    try {
      return marked.parse(cleaned, { gfm: true, breaks: true });
    } catch {
      return cleaned;
    }
  }, [cleaned]);

  if (!content) return null;

  return (
    <div
      className={`cv-markdown-content ${className}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}

const DEFAULT_QUERY =
  "Based on everything CareerVerse knows about me, what should I focus on next in my career?";

const PRESET_QUERIES = [
  {
    label: "360° Career Dossier",
    query: "Based on everything CareerVerse knows about me, what should I focus on next in my career?",
    icon: Sparkles,
  },
  {
    label: "SDE-1 to SDE-2 Promotion",
    query: "Evaluate my profile against senior software engineering benchmarks and outline priority gaps to reach the next level.",
    icon: Target,
  },
  {
    label: "Backend & Systems Pivot",
    query: "Recommend high-throughput backend infrastructure roles, evaluate my skill gaps, and prepare technical interview focus areas.",
    icon: Layers3,
  },
  {
    label: "Interview Readiness Audit",
    query: "Analyze my technical and behavioral interview readiness, generate target questions, and outline a 30-day prep roadmap.",
    icon: Brain,
  },
];

const TEAM = [
  ["profile", "Career Profile Analyst", UserRound, "Resume & GitHub Signals"],
  ["recommendation", "Career Navigator", Target, "Direction Matching"],
  ["evaluation", "Skill Gap Analyst", Layers3, "Competency Delta"],
  ["roadmap", "Career Pathfinder", BookOpen, "Milestone Architecture"],
  ["interview", "Interview Strategist", FileText, "Interview Blueprint"],
  ["virtual_interview", "Virtual AI Interviewer", Brain, "Live Interactive Drill"],
  ["interview_evaluator", "Interview Evaluator", CheckCircle2, "Response Assessment"],
  ["synthesis", "Career Intelligence Synthesizer", Sparkles, "Executive Dossier"],
];

function friendlyError(error) {
  const status = error?.response?.status;
  if (status === 401) return "Your session has expired. Please sign in again.";
  if ([429, 502, 503, 504].includes(status)) {
    return "Career Intelligence is temporarily unavailable. Please try again shortly.";
  }
  if (status === 400 || status === 422) {
    return "The career question could not be processed. Please try a more specific question.";
  }
  return getApiError(error, "Career Intelligence could not complete this report.");
}

function listFrom(value) {
  if (!Array.isArray(value)) return [];
  return value.filter((item) => typeof item === "string" && item.trim());
}

function valueList(value) {
  return Array.isArray(value) ? value : [];
}

function hasProfileSignals(profile) {
  return [
    profile?.unified_skills?.length,
    profile?.projects?.length,
    profile?.experience?.length,
    profile?.certifications_summary?.total_certifications,
    profile?.resume_summary?.uploaded,
    profile?.github_summary?.connected,
    profile?.leetcode_summary?.connected,
    profile?.hackerrank_summary?.connected,
  ].some(Boolean);
}

export default function CareerIntelligencePage() {
  const [searchParams] = useSearchParams();
  const { startActivity, endActivity } = useAIActivity();
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [role, setRole] = useState(searchParams.get("role") || "");
  const [language, setLanguage] = useState("en");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [profile, setProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [copiedBrief, setCopiedBrief] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getProfileSnapshot()
      .then((snapshot) => {
        if (!cancelled) setProfile(snapshot?.unified || null);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setProfileLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const runReport = async (event, customQuery) => {
    event?.preventDefault();
    const activeQuery = (customQuery || query).trim();
    if (!activeQuery) {
      setError("Tell Career Intelligence what you want to understand next.");
      return;
    }
    setBusy(true);
    setError("");
    setResult(null);
    startActivity("intelligence", "Career Intelligence Core", "Synthesizing multi-agent career dossier...");

    try {
      const data = await aiIntelligence(activeQuery, role.trim() || null, language || null);
      setResult(data);
      endActivity("completed", "Career Intelligence report generated");
    } catch (err) {
      setError(friendlyError(err));
      endActivity("error", "Intelligence synthesis failed");
    } finally {
      setBusy(false);
    }
  };

  const handleCopyBrief = () => {
    if (!result) return;
    const textToCopy = `Career Intelligence Report\nTarget Role: ${result.target_role || "Engineering Focus"}\n\nSummary:\n${result.summary || ""}\n\nKey Strategic Guidance:\n${result.final_guidance || ""}`;
    navigator.clipboard?.writeText(textToCopy);
    setCopiedBrief(true);
    setTimeout(() => setCopiedBrief(false), 2000);
  };

  const reportHasContent = useMemo(() => {
    if (!result) return false;
    return Boolean(
      result.summary ||
        result.final_guidance ||
        result.recommendations?.length ||
        result.skill_gaps?.length ||
        result.interview_preparation?.length ||
        result.interview_details
    );
  }, [result]);

  return (
    <main className="career-intelligence-page cv-intel-container">
      {/* ─── HERO HEADER ─────────────────────────────────────────────────── */}
      <header className="cv-intel-hero">
        <div>
          <div className="cv-intel-hero-badge">
            <Sparkles size={14} /> MULTI-AGENT SYNTHESIS ENGINE
          </div>
          <h1 className="cv-intel-hero-title">
            Career <span className="accent">Intelligence Report</span>
          </h1>
          <p className="cv-intel-hero-desc">
            A grounded, multi-agent strategy dossier that unifies verified resume metrics, GitHub repositories, LeetCode algorithms, competency gap analyses, and live interview insights into an actionable executive roadmap.
          </p>
        </div>

        {result && (
          <div className="cv-intel-hero-actions">
            <button
              type="button"
              onClick={handleCopyBrief}
              className="cv-intel-btn-secondary"
              title="Copy executive brief to clipboard"
            >
              {copiedBrief ? <Check size={14} color="#16a34a" /> : <Copy size={14} />}
              <span>{copiedBrief ? "Copied Brief!" : "Copy Brief"}</span>
            </button>
          </div>
        )}
      </header>

      {/* ─── LOW PROFILE SIGNAL NOTICE ──────────────────────────────────── */}
      {!profileLoading && profile && !hasProfileSignals(profile) && (
        <section className="ci-low-signal cv-intel-warning-banner">
          <div>
            <h3>Your career intelligence report needs more profile evidence.</h3>
            <p>
              Complete your profile, upload your verified resume, or connect your GitHub/LeetCode accounts before relying on a preliminary report.
            </p>
          </div>
          <div className="cv-intel-warning-actions ci-low-signal-actions">
            <Link className="primary primary-button" to="/profile">
              <UserRound size={14} /> Complete Profile
            </Link>
            <Link className="ghost ghost-button" to="/resume">
              <FileText size={14} /> Update Resume
            </Link>
            <Link className="ghost ghost-button" to="/github">
              <GitBranch size={14} /> Connect Sources
            </Link>
          </div>
        </section>
      )}

      {/* ─── STRATEGIC INQUIRY CONTROLLER & FORM ────────────────────────── */}
      <section className="cv-intel-form-card">
        <div className="cv-intel-form-header">
          <div className="cv-intel-form-title">
            <Brain size={18} color="var(--cv-accent, #4f46e5)" />
            <span>What strategic career decision should CareerVerse analyze?</span>
          </div>
          <div className="cv-intel-presets-bar">
            {PRESET_QUERIES.map((preset) => {
              const Icon = preset.icon;
              return (
                <button
                  key={preset.label}
                  type="button"
                  onClick={() => {
                    setQuery(preset.query);
                  }}
                  className="cv-intel-preset-chip"
                  title={preset.query}
                >
                  <Icon size={12} color="var(--cv-accent, #4f46e5)" />
                  <span>{preset.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        <form onSubmit={runReport} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div className="cv-intel-textarea-wrapper">
            <textarea
              id="ci-query"
              className="cv-intel-textarea"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. Based on my verified GitHub and resume background, what should I focus on next?"
              disabled={busy}
              rows={2}
            />
          </div>

          <div className="cv-intel-inputs-row">
            <div className="cv-intel-field-group">
              <label htmlFor="ci-role" className="cv-intel-label">
                <Target size={13} color="var(--cv-accent, #4f46e5)" />
                Target Role Override (Optional)
              </label>
              <input
                id="ci-role"
                className="cv-intel-input"
                type="text"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                placeholder="e.g. Backend Developer, Staff Infrastructure Engineer"
                disabled={busy}
              />
            </div>

            <div className="cv-intel-field-group">
              <label htmlFor="ci-language" className="cv-intel-label">
                <Sparkles size={13} color="var(--cv-accent, #4f46e5)" />
                Report Language
              </label>
              <select
                id="ci-language"
                className="cv-intel-select"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                disabled={busy}
              >
                <option value="en">English (Global)</option>
                <option value="ta">தமிழ் (Tamil)</option>
                <option value="hi">हिन्दी (Hindi)</option>
              </select>
            </div>
          </div>

          {error && (
            <div className="ci-error" role="alert" style={{ color: "#ef4444", fontSize: "0.88rem", fontWeight: 600 }}>
              {error}
            </div>
          )}

          <div className="cv-intel-submit-row">
            <span style={{ fontSize: "0.8rem", color: "var(--cv-muted, #64748b)" }}>
              Multi-agent synthesis automatically coordinates across 8 domain specialists.
            </span>
            <button
              type="submit"
              className="cv-intel-submit-btn"
              disabled={busy}
            >
              {busy ? (
                <>
                  <RefreshCw size={16} className="cv-spin" />
                  <span>Synthesizing Intelligence Dossier…</span>
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  <span>Generate Career Intelligence</span>
                </>
              )}
            </button>
          </div>
        </form>
      </section>

      {/* ─── LOADING SYNTHESIS CARD ─────────────────────────────────────── */}
      {busy && (
        <section className="cv-intel-loading-card">
          <div className="cv-intel-spinner-pulse">
            <Sparkles size={28} />
          </div>
          <div>
            <h3 style={{ margin: "0 0 0.35rem 0", fontSize: "1.2rem", fontWeight: 800, color: "var(--cv-text, #0f172a)" }}>
              Multi-Agent Intelligence in Progress
            </h3>
            <p style={{ margin: 0, fontSize: "0.9rem", color: "var(--cv-muted, #64748b)", maxWidth: "520px", lineHeight: 1.5 }}>
              Coordinating Profile Analyst, Career Navigator, Competency Evaluator, and Interview Strategist to build your grounded career dossier…
            </p>
          </div>
        </section>
      )}

      {/* ─── REPORT DOSSIER CONTENT ─────────────────────────────────────── */}
      {!busy && result && reportHasContent && (
        <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
          {/* Agent Taskforce Pipeline */}
          <AgentPipeline result={result} />

          {/* Key Executive Metrics */}
          <ExecutiveMetrics result={result} />

          {/* Quick Table of Contents Bar */}
          <nav className="cv-intel-toc-bar" aria-label="Report Table of Contents">
            <a href="#section-summary" className="cv-intel-toc-pill">01 · Executive Summary</a>
            {result.recommendations?.length > 0 && <a href="#section-directions" className="cv-intel-toc-pill">02 · Career Directions</a>}
            <a href="#section-matrix" className="cv-intel-toc-pill">03 & 04 · Strengths & Gaps</a>
            <a href="#section-journey" className="cv-intel-toc-pill">05 · Action Roadmap</a>
            <a href="#section-interview" className="cv-intel-toc-pill">06 · Interview Focus</a>
            <a href="#section-actions" className="cv-intel-toc-pill">07 · Launchpad</a>
            <a href="#section-evidence" className="cv-intel-toc-pill">08 · Verified Evidence</a>
          </nav>

          {/* Editorial Report Dossier */}
          <EditorialReportDossier result={result} />
        </div>
      )}

      {/* ─── EMPTY STATE (WITHOUT INVENTING SECTIONS) ────────────────────── */}
      {!busy && result && !reportHasContent && (
        <EmptyState title="Career intelligence is not available yet.">
          {result.summary || "The intelligence service did not return enough structured information for a report. Add profile evidence or try again."}
        </EmptyState>
      )}
    </main>
  );
}

/* ─── MULTI-AGENT PIPELINE COMPONENT ─────────────────────────────────────── */
function AgentPipeline({ result }) {
  const actual = result.agent_results || {};
  const used = new Set(result.agents_used || []);

  return (
    <section className="cv-intel-agents-card ci-team-section">
      <div className="cv-intel-agents-header">
        <div className="cv-intel-agents-title">
          <Brain size={18} color="var(--cv-accent, #4f46e5)" />
          <span id="ci-team-title">AI Career Team Orchestration</span>
        </div>
        <span style={{ fontSize: "0.76rem", color: "var(--cv-muted, #64748b)", fontWeight: 500 }}>
          8 Autonomous Specialized Agents Activated
        </span>
      </div>

      <div className="cv-intel-agents-grid ci-team-grid">
        {TEAM.map(([key, label, Icon, roleDescription]) => {
          const detail = actual[key];
          const isUsed = Boolean(detail) || used.has(key);
          const statusText = detail ? detail.status : isUsed ? "Participated" : "Architecture context";
          const isSuccess = detail?.status === "success" || statusText === "success";

          return (
            <div
              key={key}
              className={`cv-intel-agent-item ci-team-item ${isUsed || detail ? "used" : ""}`}
            >
              <div className="cv-intel-agent-icon-box">
                <Icon size={18} />
              </div>
              <div className="cv-intel-agent-details">
                <div className="cv-intel-agent-name">{label}</div>
                <div className={`cv-intel-agent-status ${isSuccess ? "success" : ""}`}>
                  <span>{statusText}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

/* ─── EXECUTIVE METRICS SNAPSHOT ─────────────────────────────────────────── */
function ExecutiveMetrics({ result }) {
  const gaps = (result.skill_gaps || []).filter((item) => item.gap_level !== "none");
  const strengths = listFrom(result.evaluation_details?.strengths);
  const targetRole = result.target_role || result.recommendations?.[0]?.title || "Full-Stack Software Engineer";
  const interviewQuestions = valueList(result.interview_preparation).length
    ? result.interview_preparation
    : valueList(result.interview_details?.questions);

  return (
    <section className="cv-intel-kpi-grid">
      <div className="cv-intel-kpi-card" style={{ "--kpi-color": "#4f46e5" }}>
        <div className="cv-intel-kpi-label">
          <span>Primary Target Direction</span>
          <Target size={14} color="#4f46e5" />
        </div>
        <div className="cv-intel-kpi-value" style={{ fontSize: "1.15rem" }}>
          {targetRole}
        </div>
        <p className="cv-intel-kpi-subtext">Optimal career path alignment</p>
      </div>

      <div className="cv-intel-kpi-card" style={{ "--kpi-color": "#16a34a" }}>
        <div className="cv-intel-kpi-label">
          <span>Verified Strengths</span>
          <CheckCircle2 size={14} color="#16a34a" />
        </div>
        <div className="cv-intel-kpi-value">
          {strengths.length > 0 ? `${strengths.length} Core Areas` : "Established"}
        </div>
        <p className="cv-intel-kpi-subtext">Backed by profile & project evidence</p>
      </div>

      <div className="cv-intel-kpi-card" style={{ "--kpi-color": "#f59e0b" }}>
        <div className="cv-intel-kpi-label">
          <span>Priority Growth Deltas</span>
          <Layers3 size={14} color="#f59e0b" />
        </div>
        <div className="cv-intel-kpi-value">
          {gaps.length > 0 ? `${gaps.length} Target Areas` : "None Critical"}
        </div>
        <p className="cv-intel-kpi-subtext">Key competencies for promotion / hire</p>
      </div>

      <div className="cv-intel-kpi-card" style={{ "--kpi-color": "#06b6d4" }}>
        <div className="cv-intel-kpi-label">
          <span>Interview Preparedness</span>
          <Brain size={14} color="#06b6d4" />
        </div>
        <div className="cv-intel-kpi-value">
          {interviewQuestions.length > 0 ? `${interviewQuestions.length} Questions Ready` : "Drill Ready"}
        </div>
        <p className="cv-intel-kpi-subtext">Domain drills in AI Interview Studio</p>
      </div>
    </section>
  );
}

/* ─── EDITORIAL REPORT DOSSIER (NEAT & STRUCTURED) ───────────────────────── */
function EditorialReportDossier({ result }) {
  const gaps = (result.skill_gaps || []).filter((item) => item.gap_level !== "none");
  const strengths = listFrom(result.evaluation_details?.strengths);
  const interviewDetails = result.interview_details || {};
  const interviewQuestions = valueList(result.interview_preparation).length
    ? result.interview_preparation
    : valueList(interviewDetails.questions);
  const evidence = result.evidence || {};
  const targetRole = result.target_role || result.recommendations?.[0]?.title;
  const interviewSignals = [
    interviewDetails.preparation_summary,
    interviewQuestions.length,
    interviewDetails.status,
  ].some(Boolean);

  return (
    <div id="career-intelligence-report" className="cv-intel-report-container">
      {/* ── 00 · REPORT DOSSIER HEADER ── */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          padding: "1.5rem 2rem",
          background: "var(--cv-paper, #ffffff)",
          borderRadius: "18px",
          border: "1px solid var(--cv-rule, #e2e8f0)",
          boxShadow: "0 2px 12px rgba(0,0,0,0.03)",
          flexWrap: "wrap",
          gap: "1rem",
        }}
      >
        <div>
          <div style={{ display: "inline-flex", alignItems: "center", gap: "6px", fontSize: "0.74rem", fontWeight: 800, color: "var(--cv-accent, #4f46e5)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.25rem" }}>
            <Sparkles size={13} /> Career Intelligence Synthesizer
          </div>
          <h1 style={{ fontSize: "1.75rem", fontWeight: 800, margin: "0.2rem 0 0.35rem 0", color: "var(--cv-text, #0f172a)" }}>
            Career Intelligence
          </h1>
          <p style={{ margin: 0, fontSize: "0.92rem", color: "var(--cv-muted, #64748b)" }}>
            Your next career focus · {targetRole ? `Synthesized for ${targetRole}.` : "Synthesized from your available CareerVerse profile evidence."}
          </p>
        </div>

        <button
          type="button"
          onClick={() => window.print()}
          className="cv-intel-btn-secondary ci-print-button"
        >
          <Printer size={15} /> Print / Save PDF
        </button>
      </div>

      {/* ── 01 · EXECUTIVE SUMMARY & STRATEGIC DIRECTION ── */}
      <section id="section-summary" className="cv-intel-section-card">
        <div className="cv-intel-section-header">
          <div className="cv-intel-section-tag">
            <span className="cv-intel-section-num cv-section-num">01</span>
            <span className="cv-intel-section-eyebrow cv-eyebrow">
              EXECUTIVE SUMMARY & CURRENT DIRECTION
            </span>
          </div>
        </div>

        <MarkdownReport
          content={result.summary || "Your profile supports a backend engineering direction."}
          className="cv-intel-lead-summary cv-body-lg"
        />

        {result.final_guidance && (
          <div className="cv-intel-guidance-box">
            <div className="cv-intel-guidance-heading">
              <Sparkles size={14} /> AI Strategic Directive
            </div>
            <MarkdownReport
              content={result.final_guidance}
              className="cv-intel-guidance-text"
            />
          </div>
        )}
      </section>

      {/* ── 02 · STRONGEST SIGNALS & RECOMMENDED DIRECTIONS ── */}
      {result.recommendations?.length > 0 && (
        <section id="section-directions" className="cv-intel-section-card">
          <div className="cv-intel-section-header">
            <div className="cv-intel-section-tag">
              <span className="cv-intel-section-num cv-section-num">02</span>
              <span className="cv-intel-section-eyebrow cv-eyebrow">
                STRONGEST SIGNALS & CAREER DIRECTIONS
              </span>
            </div>
          </div>

          <div className="cv-intel-recs-grid">
            {result.recommendations.map((rec, i) => (
              <div key={i} className="cv-intel-rec-card">
                <div>
                  <div className="cv-intel-rec-top">
                    <span className="cv-intel-rec-category">{rec.category || "Role Path"}</span>
                    <span className="cv-intel-section-num">0{i + 1}</span>
                  </div>
                  <h3 className="cv-intel-rec-title">{rec.title}</h3>
                  {rec.rationale && (
                    <p className="cv-intel-rec-rationale">{rec.rationale}</p>
                  )}
                </div>

                <div className="cv-intel-tags-row">
                  {[
                    ...(rec.supporting_skills || []),
                    ...(rec.supporting_projects || []),
                    ...(rec.supporting_technologies || []),
                  ].map((item, idx) => (
                    <span key={idx} className="cv-intel-tag">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ── 03 & 04 · WHAT YOU DEMONSTRATE & WHAT IS HOLDING YOU BACK ── */}
      <section id="section-matrix" className="cv-intel-matrix-row">
        {/* Demonstrated Strengths (03) */}
        <div className="cv-intel-matrix-col strengths">
          <div className="cv-intel-matrix-heading">
            <div className="cv-intel-section-tag">
              <span className="cv-intel-section-num cv-section-num" style={{ background: "#dcfce7", color: "#15803d" }}>03</span>
              <span className="cv-intel-section-eyebrow cv-eyebrow" style={{ color: "#15803d" }}>
                WHAT YOU DEMONSTRATE (STRENGTHS)
              </span>
            </div>
          </div>
          <h3 className="cv-intel-matrix-title">
            <CheckCircle2 size={18} color="#16a34a" />
            <span>Demonstrated strengths</span>
          </h3>
          <div className="cv-intel-items-list">
            {strengths.length > 0 ? (
              strengths.map((s, i) => (
                <div key={i} className="cv-intel-item-row">
                  <CheckCircle2 size={16} color="#16a34a" style={{ marginTop: "2px", flexShrink: 0 }} />
                  <div className="cv-intel-item-title">{s}</div>
                </div>
              ))
            ) : (
              <span style={{ fontSize: "0.84rem", color: "var(--cv-muted, #64748b)" }}>
                Demonstrated strengths will appear upon profile connection.
              </span>
            )}
          </div>
        </div>

        {/* Priority Gaps (04) */}
        <div className="cv-intel-matrix-col gaps">
          <div className="cv-intel-matrix-heading">
            <div className="cv-intel-section-tag">
              <span className="cv-intel-section-num cv-section-num" style={{ background: "#fef3c7", color: "#b45309" }}>04</span>
              <span className="cv-intel-section-eyebrow cv-eyebrow" style={{ color: "#b45309" }}>
                WHAT IS HOLDING YOU BACK (GAPS)
              </span>
            </div>
          </div>
          <h3 className="cv-intel-matrix-title">
            <Layers3 size={18} color="#d97706" />
            <span>Priority development areas</span>
          </h3>
          <div className="cv-intel-items-list">
            {gaps.length > 0 ? (
              gaps.map((g, i) => (
                <div key={i} className="cv-intel-item-row" style={{ flexDirection: "column", gap: "4px" }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
                    <span className="cv-intel-item-title">{g.skill}</span>
                    <span style={{ fontSize: "0.68rem", fontWeight: 700, padding: "2px 6px", borderRadius: "4px", background: "#fef3c7", color: "#92400e" }}>
                      {g.gap_level ? `${g.gap_level.toUpperCase()} DELTA` : "GAP"}
                    </span>
                  </div>
                  {g.explanation && (
                    <div className="cv-intel-item-desc">{g.explanation}</div>
                  )}
                </div>
              ))
            ) : (
              <span style={{ fontSize: "0.84rem", color: "var(--cv-muted, #64748b)" }}>
                No critical priority gaps identified.
              </span>
            )}
          </div>
        </div>
      </section>

      {/* ── 05 · YOUR CAREER JOURNEY ── */}
      {(result.final_guidance || result.evaluation_details?.improvement_areas?.length > 0) && (
        <section id="section-journey" className="cv-intel-section-card">
          <div className="cv-intel-section-header">
            <div className="cv-intel-section-tag">
              <span className="cv-intel-section-num cv-section-num">05</span>
              <span className="cv-intel-section-eyebrow cv-eyebrow">
                YOUR CAREER JOURNEY
              </span>
            </div>
          </div>

          <h3 style={{ fontSize: "1.25rem", fontWeight: 800, margin: "0.25rem 0 0.5rem 0", color: "var(--cv-text, #0f172a)" }}>
            A practical direction for your next build
          </h3>

          {result.evaluation_details?.improvement_areas?.length > 0 && (
            <div className="cv-intel-journey-steps">
              {result.evaluation_details.improvement_areas.map((item, idx) => (
                <div key={idx} className="cv-intel-step-card">
                  <div className="cv-intel-step-index">{idx + 1}</div>
                  <div className="cv-intel-step-text">{item}</div>
                </div>
              ))}
            </div>
          )}

          <div>
            <Link
              to={`/career-roadmap${targetRole ? `?role=${encodeURIComponent(targetRole)}` : ""}`}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "0.4rem",
                color: "var(--cv-accent, #4f46e5)",
                fontWeight: 700,
                fontSize: "0.88rem",
                textDecoration: "none",
                marginTop: "0.5rem",
              }}
            >
              <span>View Career Pathfinder</span>
              <ArrowRight size={14} />
            </Link>
          </div>
        </section>
      )}

      {/* ── 06 · INTERVIEW INSIGHTS & PRACTICE ── */}
      <section id="section-interview" className="cv-intel-section-card">
        <div className="cv-intel-section-header">
          <div className="cv-intel-section-tag">
            <span className="cv-intel-section-num cv-section-num">06</span>
            <span className="cv-intel-section-eyebrow cv-eyebrow">
              INTERVIEW INSIGHTS & PRACTICE
            </span>
          </div>
        </div>

        {interviewSignals ? (
          <div>
            <h3 style={{ fontSize: "1.25rem", fontWeight: 800, margin: "0.25rem 0 0.75rem 0", color: "var(--cv-text, #0f172a)" }}>
              Preparation grounded in your direction
            </h3>
            {interviewQuestions.length > 0 && (
              <div className="cv-intel-questions-grid">
                {interviewQuestions.slice(0, 4).map((item, index) => (
                  <div key={index} className="cv-intel-question-card">
                    <span className="cv-intel-q-badge">Q{index + 1}</span>
                    <span className="cv-intel-q-text">{item.question}</span>
                    <Link
                      to={`/ai/interview${targetRole ? `?role=${encodeURIComponent(targetRole)}` : ""}`}
                      className="cv-intel-btn-secondary"
                      style={{ padding: "0.4rem 0.75rem", fontSize: "0.75rem", textDecoration: "none" }}
                    >
                      Practice →
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div>
            <h3 style={{ fontSize: "1.25rem", fontWeight: 800, margin: "0.25rem 0 0.5rem 0", color: "var(--cv-text, #0f172a)" }}>
              No interview signals yet
            </h3>
            <p style={{ margin: "0 0 1.25rem 0", fontSize: "0.88rem", color: "var(--cv-muted, #64748b)" }}>
              Complete Interview Practice to add interview signals to this report.
            </p>
            <Link
              to={`/ai/interview${targetRole ? `?role=${encodeURIComponent(targetRole)}` : ""}`}
              className="primary-button cv-intel-submit-btn"
              style={{ textDecoration: "none", display: "inline-flex", width: "fit-content" }}
            >
              <Brain size={15} /> Practice Interview
            </Link>
          </div>
        )}
      </section>

      {/* ── 07 · RECOMMENDED NEXT ACTIONS ── */}
      <section id="section-actions" className="cv-intel-section-card">
        <div className="cv-intel-section-header">
          <div className="cv-intel-section-tag">
            <span className="cv-intel-section-num cv-section-num">07</span>
            <span className="cv-intel-section-eyebrow cv-eyebrow">
              RECOMMENDED NEXT ACTIONS
            </span>
          </div>
        </div>

        <h3 style={{ fontSize: "1.25rem", fontWeight: 800, margin: "0.25rem 0 0.75rem 0", color: "var(--cv-text, #0f172a)" }}>
          Turn the report into momentum
        </h3>

        <div className="cv-intel-launchpad-grid ci-action-links">
          <Link to="/career-discovery" className="cv-intel-launchpad-tile">
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <Target size={16} color="var(--cv-accent, #4f46e5)" />
              <span>Explore Career Paths</span>
            </div>
            <ArrowRight size={14} color="var(--cv-muted, #64748b)" />
          </Link>
          <Link to="/skill-gap" className="cv-intel-launchpad-tile">
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <Layers3 size={16} color="var(--cv-accent, #4f46e5)" />
              <span>Analyze Skill Gaps</span>
            </div>
            <ArrowRight size={14} color="var(--cv-muted, #64748b)" />
          </Link>
          <Link to="/career-roadmap" className="cv-intel-launchpad-tile">
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <BookOpen size={16} color="var(--cv-accent, #4f46e5)" />
              <span>View Learning Roadmap</span>
            </div>
            <ArrowRight size={14} color="var(--cv-muted, #64748b)" />
          </Link>
          <Link to="/ai/interview" className="cv-intel-launchpad-tile">
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <Brain size={16} color="var(--cv-accent, #4f46e5)" />
              <span>Practice Interview</span>
            </div>
            <ArrowRight size={14} color="var(--cv-muted, #64748b)" />
          </Link>
        </div>
      </section>

      {/* ── 08 · VERIFIED EVIDENCE AUDIT TRAIL ── */}
      <section id="section-evidence" className="cv-intel-section-card" style={{ background: "var(--cv-surface, #f8fafc)" }}>
        <div className="cv-intel-section-header">
          <div className="cv-intel-section-tag">
            <span className="cv-intel-section-num cv-section-num">08</span>
            <span className="cv-intel-section-eyebrow cv-eyebrow">
              VERIFIED / SOURCE EVIDENCE
            </span>
          </div>
        </div>

        <p style={{ margin: "0 0 0.5rem 0", fontSize: "0.85rem", color: "var(--cv-muted, #64748b)" }}>
          Signals returned by the intelligence pipeline.
        </p>

        <div className="cv-intel-evidence-grid">
          {[
            ...(evidence.sources || evidence.evidence_sources || []),
            ...(evidence.skills || []),
            ...(evidence.projects || []),
          ].map((item, idx) => (
            <span key={idx} className="cv-intel-evidence-pill">
              <ShieldCheck size={14} color="var(--cv-accent, #4f46e5)" />
              <span>{item}</span>
            </span>
          ))}
        </div>
      </section>
    </div>
  );
}
