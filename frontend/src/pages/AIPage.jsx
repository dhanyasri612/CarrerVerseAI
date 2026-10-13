/**
 * Phase 8B — AI Career Intelligence Page (Enhanced UX)
 *
 * Modes:
 *   "ai-recommend"    → POST /ai/career/recommend    → career role recommendations
 *   "ai-skill-gap"    → POST /ai/career/skill-gap    → skill-gap evaluation
 *   "ai-interview"    → /ai/career/interview/session → server-backed conversational interview
 *   "ai-intelligence" → POST /ai/career/intelligence → full multi-agent orchestration
 *
 * Key design decisions:
 *  - No AI logic lives here. All data comes from the backend.
 *  - Interview UX uses a persisted backend session. Answers are evaluated by the
 *    server and each follow-up question is generated from the live transcript.
 *  - Language is selected explicitly by the user OR auto-detected by the backend.
 *  - candidate_id is never sent from the frontend (derived server-side from JWT).
 *  - All four modes have loading → empty → success → error state coverage.
 */

import { useState, useRef, useEffect, useCallback } from "react";
import { Brain, Check, Mic, MicOff, Volume2 } from "lucide-react";
import { Link, useSearchParams } from "react-router-dom";
import { EmptyState, ErrorState } from "../components/AsyncState";
import { getApiError } from "../services/api";
import {
  aiIntelligence,
  createInterviewSession,
  getInterviewSession,
  submitInterviewAnswer,
  completeInterviewSession,
  aiRecommend,
  aiSkillGap,
} from "../services/careerService";
import { cleanTextForSpeech, findBestVoiceForLang } from "../services/speechService";

// ─── Language options ────────────────────────────────────────────────────────

const LANGUAGE_OPTIONS = [
  { value: "", label: "Auto-detect", native: "" },
  { value: "en", label: "English", native: "English" },
  { value: "ta", label: "Tamil", native: "தமிழ்" },
  { value: "hi", label: "Hindi", native: "हिन्दी" },
];

const LANG_LABELS = { en: "English", ta: "தமிழ்", hi: "हिन्दी" };

// ─── Supported roles for the role selector ───────────────────────────────────

const KNOWN_ROLES = [
  "Backend Developer",
  "Frontend Developer",
  "Full Stack Developer",
  "Software Developer",
  "Machine Learning Engineer",
  "Data Scientist",
];

// ─── Shared tag helpers ───────────────────────────────────────────────────────

function TagPill({ label, variant = "default" }) {
  return <span className={`cv-pill cv-pill-${variant}`}>{label}</span>;
}

function TagGroup({ items, variant = "default", max }) {
  if (!items?.length) return null;
  const visible = max ? items.slice(0, max) : items;
  const remaining = max ? items.length - max : 0;
  return (
    <div className="cv-pill-row">
      {visible.map((t) => (
        <TagPill key={t} label={t} variant={variant} />
      ))}
      {remaining > 0 && <span className="cv-pill-more">+{remaining} more</span>}
    </div>
  );
}

// ─── Language selector ────────────────────────────────────────────────────────

function LanguageSelector({ value, onChange, disabled }) {
  return (
    <div className="cv-lang-selector">
      <span className="cv-field-label">
        <span className="cv-field-icon" aria-hidden="true">
          🌐
        </span>
        Language
      </span>
      <div
        className="cv-lang-toggle-group"
        role="group"
        aria-label="Response language"
      >
        {LANGUAGE_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            type="button"
            className={`cv-lang-btn ${value === opt.value ? "cv-lang-btn-active" : ""}`}
            onClick={() => !disabled && onChange(opt.value)}
            disabled={disabled}
            aria-pressed={value === opt.value}
          >
            {opt.native || opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}

// ─── Loading animation messages ───────────────────────────────────────────────

const LOADING_MESSAGES = {
  "ai-recommend": [
    "Retrieving your skills and projects…",
    "Analysing your career profile…",
    "Generating personalised role matches…",
  ],
  "ai-skill-gap": [
    "Comparing your skills against role requirements…",
    "Identifying gaps and strengths…",
    "Building your skill gap report…",
  ],
  "ai-interview": [
    "Reviewing your projects and experience…",
    "Crafting personalised interview questions…",
    "Preparing your interview session…",
  ],
  "ai-intelligence": [
    "Routing your query to the right agents…",
    "Running career intelligence analysis…",
    "Synthesising recommendations, gaps and questions…",
  ],
};

function AILoadingState({ mode }) {
  const msgs = LOADING_MESSAGES[mode] || ["Analysing your profile…"];
  const [idx, setIdx] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setIdx((i) => (i + 1) % msgs.length), 2200);
    return () => clearInterval(t);
  }, [msgs.length]);
  return (
    <div
      className="cv-ai-loading"
      aria-live="polite"
      aria-label="AI is working"
    >
      <div className="cv-ai-loading-dots">
        <span />
        <span />
        <span />
      </div>
      <p className="cv-ai-loading-msg">{msgs[idx]}</p>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// RECOMMENDATION PAGE
// ═══════════════════════════════════════════════════════════════════════════════

function RecommendPage() {
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [validErr, setValidErr] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setValidErr("");
    if (!query.trim()) {
      setValidErr("Please enter a question.");
      return;
    }
    setBusy(true);
    setError("");
    setResult(null);
    try {
      setResult(await aiRecommend(query.trim(), language || null));
    } catch (err) {
      setError(
        getApiError(err, "The recommendation request could not be completed."),
      );
    } finally {
      setBusy(false);
    }
  };

  const recs = result?.recommendations || [];
  const narrative = result?.generated_answer || "";

  return (
    <div className="cv-ai-page">
      {/* ── Header ── */}
      <div className="cv-ai-hero">
        <div className="cv-ai-hero-icon" aria-hidden="true">
          💼
        </div>
        <div>
          <p className="eyebrow">AI · Recommendations</p>
          <h2 className="cv-ai-hero-title">Career Role Recommendations</h2>
          <p className="cv-ai-hero-desc">
            Ask in plain language — the AI reads your full profile and returns
            grounded role recommendations.
          </p>
        </div>
      </div>

      {/* ── Form ── */}
      <form className="cv-ai-form panel-card" onSubmit={handleSubmit}>
        <label className="cv-field-label" htmlFor="rec-query">
          <span className="cv-field-icon" aria-hidden="true">
            ✏️
          </span>
          Your question
        </label>
        <textarea
          id="rec-query"
          className="cv-ai-textarea"
          rows={3}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What career roles are suitable for me based on my skills?"
          disabled={busy}
          aria-required="true"
        />
        <div className="cv-ai-form-footer">
          <LanguageSelector
            value={language}
            onChange={setLanguage}
            disabled={busy}
          />
          {validErr && (
            <p className="cv-field-error" role="alert">
              {validErr}
            </p>
          )}
          <button
            className="primary-button cv-ai-submit-btn"
            type="submit"
            disabled={busy}
            aria-busy={busy}
          >
            {busy ? (
              <>
                <span className="spinner" aria-hidden="true" /> Analysing…
              </>
            ) : (
              "Get Recommendations →"
            )}
          </button>
        </div>
      </form>

      {/* ── Results ── */}
      {busy && <AILoadingState mode="ai-recommend" />}
      {!busy && error && (
        <ErrorState
          message={error}
          onRetry={() => {
            setError("");
            setResult(null);
          }}
        />
      )}
      {!busy && !error && result && (
        <div className="cv-ai-result">
          {/* Response language badge */}
          {result.language && result.language !== "en" && (
            <div className="cv-response-lang-bar">
              <span className="cv-response-lang-badge">
                {LANG_LABELS[result.language] || result.language}
              </span>
              <span className="cv-response-lang-note">
                Response in {LANG_LABELS[result.language] || result.language}
              </span>
            </div>
          )}
          {/* Narrative */}
          {narrative && (
            <div className="cv-ai-narrative panel-card">
              <p>{narrative}</p>
            </div>
          )}
          {/* Recommendation cards */}
          {recs.length === 0 ? (
            <EmptyState title="No structured recommendations returned">
              The AI generated a narrative response above. Try a more specific
              query.
            </EmptyState>
          ) : (
            <div className="cv-rec-grid">
              {recs.map((rec, i) => (
                <RecommendCard key={rec.title + i} rec={rec} />
              ))}
            </div>
          )}
        </div>
      )}
      {!busy && !error && !result && (
        <EmptyState title="Ready when you are">
          Enter your question above and press{" "}
          <strong>Get Recommendations</strong>.
        </EmptyState>
      )}
    </div>
  );
}

function RecommendCard({ rec }) {
  const [expanded, setExpanded] = useState(false);
  const hasEvidence =
    rec.supporting_skills?.length ||
    rec.supporting_technologies?.length ||
    rec.supporting_projects?.length ||
    rec.supporting_experience?.length;

  return (
    <article className="cv-rec-card panel-card">
      <div className="cv-rec-card-header">
        <div>
          <span className="eyebrow">{rec.category}</span>
          <h3 className="cv-rec-card-title">{rec.title}</h3>
        </div>
        {rec.confidence && (
          <span
            className="cv-rec-confidence"
            title="Advisory heuristic — not a statistical probability"
          >
            {rec.confidence.replace(" (Heuristic)", "")}
          </span>
        )}
      </div>
      <p className="cv-rec-rationale">{rec.rationale}</p>
      {hasEvidence ? (
        <>
          {rec.supporting_skills?.length > 0 && (
            <div className="cv-evidence-group">
              <p className="cv-evidence-label">Skills match</p>
              <TagGroup items={rec.supporting_skills} variant="skill" max={6} />
            </div>
          )}
          {expanded && (
            <>
              {rec.supporting_technologies?.length > 0 && (
                <div className="cv-evidence-group">
                  <p className="cv-evidence-label">Technologies</p>
                  <TagGroup
                    items={rec.supporting_technologies}
                    variant="tech"
                  />
                </div>
              )}
              {rec.supporting_projects?.length > 0 && (
                <div className="cv-evidence-group">
                  <p className="cv-evidence-label">Relevant projects</p>
                  <TagGroup items={rec.supporting_projects} variant="project" />
                </div>
              )}
              {rec.supporting_experience?.length > 0 && (
                <div className="cv-evidence-group">
                  <p className="cv-evidence-label">Experience</p>
                  <ul className="cv-evidence-list">
                    {rec.supporting_experience.map((e, i) => (
                      <li key={i}>{e}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
          {(rec.supporting_technologies?.length ||
            rec.supporting_projects?.length) > 0 && (
            <button
              className="cv-expand-btn"
              type="button"
              onClick={() => setExpanded((v) => !v)}
              aria-expanded={expanded}
            >
              {expanded ? "Show less" : "Show evidence"}
            </button>
          )}
        </>
      ) : null}
    </article>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// SKILL GAP PAGE
// ═══════════════════════════════════════════════════════════════════════════════

const GAP_META = {
  none: { label: "None", cls: "cv-gap-none" },
  low: { label: "Low", cls: "cv-gap-low" },
  medium: { label: "Medium", cls: "cv-gap-medium" },
  high: { label: "High", cls: "cv-gap-high" },
};

const STATUS_LABELS = {
  demonstrated: { label: "✓ Demonstrated", cls: "cv-status-ok" },
  partially_demonstrated: { label: "◑ Partial", cls: "cv-status-partial" },
  missing: { label: "✗ Missing", cls: "cv-status-missing" },
  insufficient_evidence: {
    label: "? Insufficient data",
    cls: "cv-status-unknown",
  },
};

function SkillGapPage() {
  const [role, setRole] = useState("");
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [validErr, setValidErr] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setValidErr("");
    if (!role.trim()) {
      setValidErr("Target role is required for this analysis.");
      return;
    }
    setBusy(true);
    setError("");
    setResult(null);
    try {
      setResult(
        await aiSkillGap(role.trim(), query.trim() || null, language || null),
      );
    } catch (err) {
      setError(
        getApiError(err, "The skill-gap request could not be completed."),
      );
    } finally {
      setBusy(false);
    }
  };

  const matched = result?.strengths || [];
  const gaps = (result?.skill_gaps || []).filter((g) => g.gap_level !== "none");
  const allGaps = result?.skill_gaps || [];

  return (
    <div className="cv-ai-page">
      <div className="cv-ai-hero">
        <div className="cv-ai-hero-icon" aria-hidden="true">
          📊
        </div>
        <div>
          <p className="eyebrow">AI · Skill Gap</p>
          <h2 className="cv-ai-hero-title">AI Skill-Gap Analysis</h2>
          <p className="cv-ai-hero-desc">
            Compare your verified profile against any target role to see what
            you already have and what to develop.
          </p>
        </div>
      </div>

      <form className="cv-ai-form panel-card" onSubmit={handleSubmit}>
        <div className="cv-ai-form-row-2col">
          <div>
            <label className="cv-field-label" htmlFor="gap-role">
              <span className="cv-field-icon" aria-hidden="true">
                🎯
              </span>
              Target role <span className="cv-required">required</span>
            </label>
            <input
              id="gap-role"
              className="cv-ai-input"
              type="text"
              list="gap-role-list"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="e.g. Backend Developer"
              disabled={busy}
              aria-required="true"
            />
            <datalist id="gap-role-list">
              {KNOWN_ROLES.map((r) => (
                <option key={r} value={r} />
              ))}
            </datalist>
          </div>
          <div>
            <label className="cv-field-label" htmlFor="gap-query">
              <span className="cv-field-icon" aria-hidden="true">
                ✏️
              </span>
              Custom question <span className="cv-optional">optional</span>
            </label>
            <input
              id="gap-query"
              className="cv-ai-input"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="What skills am I missing?"
              disabled={busy}
            />
          </div>
        </div>
        <div className="cv-ai-form-footer">
          <LanguageSelector
            value={language}
            onChange={setLanguage}
            disabled={busy}
          />
          {validErr && (
            <p className="cv-field-error" role="alert">
              {validErr}
            </p>
          )}
          <button
            className="primary-button cv-ai-submit-btn"
            type="submit"
            disabled={busy}
            aria-busy={busy}
          >
            {busy ? (
              <>
                <span className="spinner" aria-hidden="true" /> Analysing…
              </>
            ) : (
              "Analyse Gaps →"
            )}
          </button>
        </div>
      </form>

      {busy && <AILoadingState mode="ai-skill-gap" />}
      {!busy && error && (
        <ErrorState
          message={error}
          onRetry={() => {
            setError("");
            setResult(null);
          }}
        />
      )}
      {!busy && !error && result && (
        <div className="cv-ai-result">
          {result.status === "target_role_required" ||
          result.status === "invalid_role" ? (
            <div className="state-card error-state">
              <strong>Target role required</strong>
              <span>{result.summary}</span>
            </div>
          ) : (
            <>
              {/* Header */}
              <div className="cv-gap-result-header">
                <div className="cv-gap-result-title">
                  <h3>{result.target_role}</h3>
                  <p className="cv-ai-hero-desc">{result.summary}</p>
                </div>
                <div className="cv-gap-scorecards">
                  <div className="cv-gap-scorecard cv-scorecard-ok">
                    <span className="cv-scorecard-num">{matched.length}</span>
                    <span>Matched</span>
                  </div>
                  <div className="cv-gap-scorecard cv-scorecard-gap">
                    <span className="cv-scorecard-num">{gaps.length}</span>
                    <span>Gaps</span>
                  </div>
                </div>
              </div>

              {/* Two-column layout: matched vs gaps */}
              <div className="cv-gap-columns">
                <div className="panel-card cv-gap-column cv-gap-column-ok">
                  <h4 className="cv-gap-col-title">
                    <span aria-hidden="true">✓</span> Your Strengths
                  </h4>
                  {matched.length === 0 ? (
                    <p className="muted-copy">
                      No demonstrated strengths found for this role.
                    </p>
                  ) : (
                    <ul className="cv-strength-list">
                      {matched.map((s) => (
                        <li key={s} className="cv-strength-item">
                          <span
                            className="cv-strength-check"
                            aria-hidden="true"
                          >
                            ✓
                          </span>
                          {s}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
                <div className="panel-card cv-gap-column cv-gap-column-miss">
                  <h4 className="cv-gap-col-title">
                    <span aria-hidden="true">⚡</span> Skills to Develop
                  </h4>
                  {gaps.length === 0 ? (
                    <p className="muted-copy">
                      No significant gaps found — you are well-aligned with this
                      role.
                    </p>
                  ) : (
                    <ul className="cv-gap-pill-list">
                      {gaps.map((g) => (
                        <li
                          key={g.skill}
                          className={`cv-gap-pill ${GAP_META[g.gap_level]?.cls || ""}`}
                        >
                          <span className="cv-gap-pill-name">{g.skill}</span>
                          <span className="cv-gap-pill-level">
                            {GAP_META[g.gap_level]?.label}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>

              {/* Detailed breakdown */}
              {allGaps.length > 0 && (
                <div className="panel-card">
                  <h4 className="cv-section-title">Detailed Skill Breakdown</h4>
                  <div className="cv-gap-detail-list">
                    {allGaps.map((gap) => (
                      <SkillGapRow key={gap.skill} gap={gap} />
                    ))}
                  </div>
                </div>
              )}

              {/* Improvement areas */}
              {result.improvement_areas?.length > 0 && (
                <div className="panel-card cv-improvement-panel">
                  <h4 className="cv-section-title">
                    <span aria-hidden="true">🗺️</span> Recommended Next Steps
                  </h4>
                  <ol className="cv-improvement-list">
                    {result.improvement_areas.map((area, i) => (
                      <li key={i}>{area}</li>
                    ))}
                  </ol>
                </div>
              )}
            </>
          )}
        </div>
      )}
      {!busy && !error && !result && (
        <EmptyState title="Ready when you are">
          Enter a target role above and press <strong>Analyse Gaps</strong>.
        </EmptyState>
      )}
    </div>
  );
}

function SkillGapRow({ gap }) {
  const [open, setOpen] = useState(false);
  const meta = GAP_META[gap.gap_level] || GAP_META.medium;
  const statusMeta = STATUS_LABELS[gap.status] || {
    label: gap.status,
    cls: "",
  };
  return (
    <div className={`cv-gap-detail-row ${meta.cls}`}>
      <button
        className="cv-gap-detail-toggle"
        type="button"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
      >
        <div className="cv-gap-detail-main">
          <strong className="cv-gap-detail-skill">{gap.skill}</strong>
          <span className="cv-gap-detail-category">{gap.category}</span>
        </div>
        <div className="cv-gap-detail-badges">
          <span className={`cv-status-badge ${statusMeta.cls}`}>
            {statusMeta.label}
          </span>
          <span className={`cv-gap-level-badge ${meta.cls}`}>
            {meta.label} gap
          </span>
          <span className="cv-expand-arrow" aria-hidden="true">
            {open ? "▲" : "▼"}
          </span>
        </div>
      </button>
      {open && (
        <div className="cv-gap-detail-body">
          {gap.explanation && <p>{gap.explanation}</p>}
          {gap.candidate_evidence?.length > 0 && (
            <>
              <p className="cv-evidence-label">Evidence found</p>
              <TagGroup items={gap.candidate_evidence} variant="evidence" />
            </>
          )}
          {gap.evidence_sources?.length > 0 && (
            <p className="cv-evidence-sources">
              Sources: {gap.evidence_sources.join(", ")}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// INTERVIEW PAGE — Client-side conversational session
// ═══════════════════════════════════════════════════════════════════════════════

const INTERVIEW_MODES = [
  { value: "general", label: "General" },
  { value: "target_role", label: "Target Role" },
  { value: "project", label: "Projects" },
  { value: "skill", label: "Skills" },
  { value: "skill_gap", label: "Skill Gap" },
];

function getInterviewError(error, fallback) {
  const status = error?.response?.status;
  if (status === 401) return "Your session has expired. Please sign in again.";
  if (status === 404) return "This interview session is no longer available. Please start a new one.";
  if (status === 429 || status === 502 || status === 503 || status === 504) {
    return "The interview service is temporarily unavailable. Please try again shortly.";
  }
  if (status === 400 || status === 422) return "That interview action could not be completed. Please check your answer and try again.";
  return fallback;
}

function InterviewPage() {
  const [searchParams] = useSearchParams();
  const handedOffRole = searchParams.get("role") || "";
  // ── Setup phase ──
  const [interviewMode, setInterviewMode] = useState("target_role");
  const [role, setRole] = useState(handedOffRole);
  const [language, setLanguage] = useState("");
  const [validErr, setValidErr] = useState("");
  const [proctored, setProctored] = useState(false);
  const [proctorConsent, setProctorConsent] = useState(false);
  const [proctorChecks, setProctorChecks] = useState(null);
  const [proctorEvents, setProctorEvents] = useState([]);

  // ── Session phase ──
  // "setup" → "loading" → "active" → "done"
  const [phase, setPhase] = useState("setup");
  const [questions, setQuestions] = useState([]);
  const [_preparationSummary, setPreparationSummary] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [detectedMode, setDetectedMode] = useState("");
  const [session, setSession] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // ── Active interview state ──
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answer, setAnswer] = useState("");
  const [transcript, setTranscript] = useState([]); // [{role:"ai"|"user", text, meta?}]
  const [error, setError] = useState("");
  const [voiceMode, setVoiceMode] = useState(false);
  const [listening, setListening] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState("idle");
  const [voiceNotice, setVoiceNotice] = useState("");
  const currentQuestion = session?.current_question;

  const answerRef = useRef(null);
  const transcriptEndRef = useRef(null);
  const recognitionRef = useRef(null);
  const spokenQuestionRef = useRef("");

  const voiceInputSupported =
    typeof window !== "undefined" &&
    Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);
  const speechOutputSupported =
    typeof window !== "undefined" &&
    Boolean(window.speechSynthesis && window.SpeechSynthesisUtterance);

  // Auto-scroll transcript (guard: jsdom lacks scrollIntoView)
  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView?.({ behavior: "smooth" });
  }, [transcript]);

  // Focus answer input when a new question appears
  useEffect(() => {
    if (phase === "active") {
      answerRef.current?.focus();
    }
  }, [phase, currentIdx]);

  const speakQuestion = useCallback(() => {
    if (!currentQuestion?.question) return;
    if (!speechOutputSupported) {
      setVoiceNotice("Question playback is unavailable here. You can still answer by text.");
      return;
    }
    window.speechSynthesis.cancel();
    const cleanedText = cleanTextForSpeech(currentQuestion.question);
    const utterance = new window.SpeechSynthesisUtterance(cleanedText || currentQuestion.question);
    utterance.lang =
      { en: "en-US", ta: "ta-IN", hi: "hi-IN" }[language || "en"] || "en-US";
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    const voices = window.speechSynthesis.getVoices?.() || [];
    const compatibleVoice = findBestVoiceForLang(voices, language || "en");
    if (compatibleVoice) utterance.voice = compatibleVoice;
    window.speechSynthesis.speak(utterance);
  }, [currentQuestion, language, speechOutputSupported]);

  useEffect(() => {
    if (!voiceMode || phase !== "active" || !currentQuestion?.question) return undefined;
    const questionKey = `${session?.question_number || 1}:${currentQuestion.question}`;
    if (spokenQuestionRef.current === questionKey) return undefined;
    spokenQuestionRef.current = questionKey;
    speakQuestion();
    return () => window.speechSynthesis?.cancel?.();
  }, [voiceMode, phase, session?.question_number, currentQuestion?.question, speakQuestion]);

  useEffect(() => () => {
    recognitionRef.current?.stop?.();
    window.speechSynthesis?.cancel?.();
  }, []);

  useEffect(() => {
    if (!proctored || phase !== "active") return undefined;
    const record = (message) => setProctorEvents((events) => [...events.slice(-9), { message, at: new Date().toLocaleTimeString() }]);
    const onVisibility = () => { if (document.visibilityState !== "visible") record("Tab visibility changed."); };
    const onFullscreen = () => { if (!document.fullscreenElement) record("Fullscreen was exited."); };
    const onBlur = () => record("Window focus changed.");
    document.addEventListener("visibilitychange", onVisibility);
    document.addEventListener("fullscreenchange", onFullscreen);
    window.addEventListener("blur", onBlur);
    return () => {
      document.removeEventListener("visibilitychange", onVisibility);
      document.removeEventListener("fullscreenchange", onFullscreen);
      window.removeEventListener("blur", onBlur);
    };
  }, [proctored, phase]);

  const toggleListening = () => {
    const Recognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
      setVoiceNotice(
        "Voice interview is not available in this browser. You can continue with text.",
      );
      return;
    }
    if (listening) {
      setVoiceStatus("processing");
      recognitionRef.current?.stop();
      return;
    }
    const recognition = new Recognition();
    recognition.lang =
      { en: "en-IN", ta: "ta-IN", hi: "hi-IN" }[language || "en"] || "en-IN";
    recognition.interimResults = true;
    recognition.continuous = false;
    recognition.onstart = () => {
      setListening(true);
      setVoiceStatus("listening");
      setVoiceNotice(
        "Listening… speak your answer, then review the transcript.",
      );
    };
    recognition.onresult = (event) => {
      const transcriptText = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join(" ");
      setAnswer(transcriptText);
      setVoiceStatus("ready");
    };
    recognition.onerror = (event) => {
      setListening(false);
      setVoiceStatus("idle");
      setVoiceNotice(
        event.error === "not-allowed"
          ? "Microphone access was denied. You can continue with text."
          : "Voice input was unavailable. Please try again or continue with text.",
      );
    };
    recognition.onend = () => {
      setListening(false);
      setVoiceStatus("ready");
    };
    recognitionRef.current = recognition;
    recognition.start();
  };

  const switchToText = () => {
    recognitionRef.current?.stop?.();
    window.speechSynthesis?.cancel?.();
    setListening(false);
    setVoiceStatus("idle");
    setVoiceMode(false);
    setVoiceNotice("");
  };

  // Resume an active server-backed session after a refresh or route change.
  useEffect(() => {
    const savedSessionId = window.localStorage.getItem(
      "careerverse_interview_session_id",
    );
    if (!savedSessionId || phase !== "setup") return undefined;
    let cancelled = false;
    getInterviewSession(savedSessionId)
      .then((data) => {
        if (cancelled) return;
        setSession(data);
        setTargetRole(data.target_role || "");
        setDetectedMode(data.interview_mode || "general");
        setQuestions(data.current_question ? [data.current_question] : []);
        setTranscript(
          data.transcript?.flatMap((entry) => [
            {
              role: "ai",
              text: entry.question.question,
              question: entry.question,
            },
            { role: "user", text: entry.answer },
            {
              role: "ai",
              text: entry.evaluation.assessment,
              isEvaluation: true,
              evaluation: entry.evaluation,
            },
          ]) || [],
        );
        setPhase(data.status === "completed" ? "done" : "active");
      })
      .catch(() =>
        window.localStorage.removeItem("careerverse_interview_session_id"),
      );
    return () => {
      cancelled = true;
    };
  }, [phase]);

  // ── Start interview ──
  const handleStart = async (e) => {
    e.preventDefault();
    setValidErr("");
    if (interviewMode === "target_role" && !role.trim()) {
      setValidErr("Please enter a target role for this interview type.");
      return;
    }
    if (proctored && !proctorConsent) {
      setValidErr("Review and accept the proctored interview disclosure before continuing.");
      return;
    }
    if (proctored) {
      const checks = { microphone: false, camera: false, speech: voiceInputSupported, speaker: speechOutputSupported, fullscreen: Boolean(document.fullscreenEnabled) };
      try {
        if (navigator.mediaDevices?.getUserMedia) {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
          checks.microphone = stream.getAudioTracks().length > 0; checks.camera = stream.getVideoTracks().length > 0; stream.getTracks().forEach((track) => track.stop());
        }
      } catch { setValidErr("Microphone and camera access are required for this proctored mode. You can continue with standard interview mode."); return; }
      setProctorChecks(checks); setProctorEvents([]);
      if (document.documentElement.requestFullscreen) await document.documentElement.requestFullscreen().catch(() => {});
    }
    setPhase("loading");
    setError("");
    setTranscript([]);
    setCurrentIdx(0);

    try {
      const data = await createInterviewSession(
        role.trim() || null,
        interviewMode,
        language || "en",
      );
      if (!data.current_question) {
        setError("No interview questions were returned. Please try again.");
        setPhase("setup");
        return;
      }
      setSession(data);
      window.localStorage.setItem(
        "careerverse_interview_session_id",
        data.session_id,
      );
      setQuestions(data.current_question ? [data.current_question] : []);
      setTargetRole(data.target_role || role.trim() || "");
      setDetectedMode(data.interview_mode || interviewMode);
      setTranscript([]);
      setPhase("active");
    } catch (err) {
      setError(
        getInterviewError(err, "Could not start the interview. Please try again."),
      );
      setPhase("setup");
    }
  };

  // ── Submit answer, show next question ──
  const handleSubmitAnswer = async () => {
    if (!answer.trim()) return;
    if (!session?.session_id || isSubmitting) return;
    setIsSubmitting(true);
    setError("");
    const submittedAnswer = answer.trim();
    try {
      const data = await submitInterviewAnswer(
        session.session_id,
        submittedAnswer,
      );
      const currentQ = session.current_question;
      setSession(data);
      setTranscript((prev) => [
        ...prev,
        {
          role: "ai",
          text: currentQ.question,
          questionIdx: currentIdx,
          question: currentQ,
        },
        { role: "user", text: submittedAnswer },
        {
          role: "ai",
          text: data.latest_evaluation?.assessment || "Answer evaluated.",
          isEvaluation: true,
          evaluation: data.latest_evaluation,
        },
      ]);
      setQuestions((prev) => [...prev, data.current_question].filter(Boolean));
      setCurrentIdx((prev) => prev + 1);
      setAnswer("");
    } catch (err) {
      setError(
        getInterviewError(err, "Could not evaluate that answer. Please retry."),
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleComplete = async () => {
    if (!session?.session_id || isSubmitting) return;
    setIsSubmitting(true);
    setError("");
    try {
      const data = await completeInterviewSession(session.session_id);
      setSession(data);
      setQuestions(data.final_report?.questions_asked || questions);
      setPhase("done");
      window.localStorage.removeItem("careerverse_interview_session_id");
    } catch (err) {
      setError(
        getInterviewError(err, "Could not complete the interview. Please retry."),
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmitAnswer();
    }
  };

  const handleReset = () => {
    recognitionRef.current?.stop?.();
    window.speechSynthesis?.cancel?.();
    setPhase("setup");
    setQuestions([]);
    setSession(null);
    setTranscript([]);
    setCurrentIdx(0);
    setAnswer("");
    setError("");
    setPreparationSummary("");
    setTargetRole("");
    setDetectedMode("");
    setVoiceMode(false);
    setListening(false);
    setVoiceStatus("idle");
    setVoiceNotice("");
    setProctorChecks(null); setProctorEvents([]); setProctored(false); setProctorConsent(false);
    spokenQuestionRef.current = "";
    window.localStorage.removeItem("careerverse_interview_session_id");
  };

  return (
    <div className="cv-ai-page">
      {/* ── SETUP ── */}
      {phase === "setup" && (
        <>
          <div className="cv-ai-hero">
            <div className="cv-ai-hero-icon" aria-hidden="true">
              <Mic size={28} />
            </div>
            <div>
              <p className="eyebrow">Virtual AI Interviewer</p>
              <h2 className="cv-ai-hero-title">Practice Interview</h2>
              <p className="cv-ai-hero-desc">
                Practice a realistic interview for your target career and receive
                evidence-based feedback grounded in your available profile.
              </p>
            </div>
          </div>

          <form className="cv-ai-form panel-card" onSubmit={handleStart}>
            {/* Interview type */}
            <label className="cv-field-label">
              <span className="cv-field-icon" aria-hidden="true">
                📋
              </span>
              Interview type
            </label>
            <div
              className="cv-mode-selector"
              role="group"
              aria-label="Interview type"
            >
              {INTERVIEW_MODES.map((m) => (
                <button
                  key={m.value}
                  type="button"
                  className={`cv-mode-btn ${interviewMode === m.value ? "cv-mode-btn-active" : ""}`}
                  onClick={() => setInterviewMode(m.value)}
                  aria-pressed={interviewMode === m.value}
                >
                  {m.label}
                </button>
              ))}
            </div>

            <div className="proctor-mode-panel">
              <div>
                <strong>Proctored Interview</strong>
                <p>Optional local browser checks for microphone, camera, speech, fullscreen, and focus events. No raw audio or video is stored by this UI.</p>
              </div>
              <label className="proctor-toggle"><input type="checkbox" checked={proctored} onChange={(event) => { setProctored(event.target.checked); setProctorConsent(false); }} /> Enable proctored mode</label>
              {proctored ? <label className="proctor-consent"><input type="checkbox" checked={proctorConsent} onChange={(event) => setProctorConsent(event.target.checked)} /> I understand the browser checks and consent to this local monitoring.</label> : null}
            </div>

            {/* Target role */}
            <label className="cv-field-label" htmlFor="int-role">
              <span className="cv-field-icon" aria-hidden="true">
                🎯
              </span>
              Interviewing for{" "}
              {interviewMode === "target_role" ||
              interviewMode === "skill_gap" ? (
                <span className="cv-required">required</span>
              ) : (
                <span className="cv-optional">optional</span>
              )}
            </label>
            <input
              id="int-role"
              className="cv-ai-input"
              type="text"
              list="int-role-list"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="e.g. Backend Developer"
              disabled={false}
            />
            <datalist id="int-role-list">
              {KNOWN_ROLES.map((r) => (
                <option key={r} value={r} />
              ))}
            </datalist>

            <div className="cv-ai-form-footer">
              <LanguageSelector
                value={language}
                onChange={setLanguage}
                disabled={false}
              />
              {validErr && (
                <p className="cv-field-error" role="alert">
                  {validErr}
                </p>
              )}
              {error && (
                <p className="cv-field-error" role="alert">
                  {error}
                </p>
              )}
              <button className="primary-button cv-ai-submit-btn" type="submit">
                Start Interview →
              </button>
            </div>
          </form>

          {/* What to expect */}
          <div className="cv-interview-info panel-card">
            <h4 className="cv-section-title">How it works</h4>
            <div className="cv-interview-steps">
              {[
                [
                  "1",
                  "AI loads your profile",
                  "Skills, projects, and experience from your connected accounts",
                ],
                [
                  "2",
                  "Questions are generated",
                  "Personalised questions grounded in your actual evidence",
                ],
                [
                  "3",
                  "Answer at your pace",
                  "Type your answers one question at a time",
                ],
                [
                  "4",
                  "Review your session",
                  "See all questions and your answers at the end",
                ],
              ].map(([n, title, desc]) => (
                <div key={n} className="cv-interview-step">
                  <span className="cv-step-num">{n}</span>
                  <div>
                    <strong>{title}</strong>
                    <p>{desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* ── LOADING ── */}
      {phase === "loading" && <AILoadingState mode="ai-interview" />}

      {/* ── ACTIVE INTERVIEW ── */}
      {phase === "active" && (
        <div className="cv-interview-session">
          {/* Session header */}
          <div className="cv-interview-header panel-card">
            <div className="cv-interview-header-left">
              <div className="cv-interview-status-dot" aria-hidden="true" />
              <div>
                <strong>Virtual AI Interviewer</strong>
                <p className="cv-interview-meta">
                  <span>Target: {targetRole || "Profile-based practice"}</span>
                  {detectedMode && <span className="tag">{detectedMode}</span>}
                  {language && language !== "en" && (
                    <span
                      className="cv-response-lang-badge"
                      style={{ marginLeft: "0.5rem" }}
                    >
                      {LANG_LABELS[language] || language}
                    </span>
                  )}
                </p>
              </div>
            </div>
            <div className="cv-interview-progress-area">
              <span className="cv-interview-progress-label">
                Question {session?.question_number || 1} · Interview in progress
              </span>
              <div className="cv-interview-progress-bar cv-progress-indeterminate" role="progressbar" aria-label="Interview in progress" />
            </div>
          </div>
          {proctored && proctorChecks && <div className="proctor-live-panel" role="status"><strong>Proctored mode active</strong><div className="proctor-check-row">{Object.entries(proctorChecks).map(([name, passed]) => <span key={name} className={passed ? "passed" : "unavailable"}>{passed ? "✓" : "—"} {name}</span>)}</div>{proctorEvents.length ? <ul>{proctorEvents.map((event, index) => <li key={`${event.at}-${index}`}>{event.at} · {event.message}</li>)}</ul> : <small>Browser state events will be reported neutrally here.</small>}</div>}

          {/* Transcript */}
          <div
            className="cv-interview-transcript"
            aria-live="polite"
            aria-label="Interview transcript"
          >
            {transcript.map((msg, i) => (
              <InterviewMessage key={i} msg={msg} />
            ))}
            {/* Current question bubble (not yet answered) */}
            {currentQuestion && (
              <InterviewMessage
                msg={{
                  role: "ai",
                  text: currentQuestion.question,
                  question: currentQuestion,
                }}
                isCurrent
              />
            )}
            <div ref={transcriptEndRef} />
          </div>

          {/* Answer input */}
          <div className="cv-interview-answer-area">
            <div className="cv-interview-answer-wrap panel-card">
              <div
                className="interview-mode-switch"
                role="group"
                aria-label="Interview mode"
              >
                <button
                  type="button"
                  className={!voiceMode ? "active" : ""}
                  onClick={switchToText}
                  aria-pressed={!voiceMode}
                >
                  Text mode
                </button>
                {voiceInputSupported || speechOutputSupported ? (
                  <button
                    type="button"
                    className={voiceMode ? "active" : ""}
                    onClick={() => {
                      setVoiceMode(true);
                      setVoiceStatus("idle");
                      setVoiceNotice("");
                    }}
                    aria-pressed={voiceMode}
                  >
                    <Mic size={15} aria-hidden="true" /> Voice mode
                  </button>
                ) : null}
              </div>
              {voiceMode && (
                <div className="voice-controls" aria-label="Voice interview controls">
                  <button
                    type="button"
                    className={`voice-button ${listening ? "listening" : ""}`}
                    onClick={toggleListening}
                    aria-pressed={listening}
                    disabled={!voiceInputSupported || isSubmitting}
                  >
                    {listening ? <><MicOff size={16} aria-hidden="true" /> Stop listening</> : <><Mic size={16} aria-hidden="true" /> Start listening</>}
                  </button>
                  {speechOutputSupported && (
                    <button
                      type="button"
                      className="ghost-button"
                      onClick={speakQuestion}
                      aria-label="Replay question"
                    >
                      <Volume2 size={16} aria-hidden="true" /> Replay question
                    </button>
                  )}
                  <button type="button" className="ghost-button" onClick={switchToText}>
                    Switch to text mode
                  </button>
                </div>
              )}
              {voiceMode && (
                <div className="cv-voice-status" aria-live="polite">
                  <span className={`cv-voice-status-dot cv-voice-status-${voiceStatus}`} aria-hidden="true" />
                  {voiceStatus === "listening" && "Listening for your answer…"}
                  {voiceStatus === "processing" && "Finishing your transcript…"}
                  {voiceStatus === "ready" && "Transcript ready — edit it before submitting."}
                  {voiceStatus === "idle" && (voiceInputSupported ? "Ready when you are." : "Voice input is unavailable; use text mode to answer.")}
                </div>
              )}
              {voiceNotice && (
                <p className="voice-notice" role="status">
                  {voiceNotice}
                </p>
              )}
              <label className="cv-field-label" htmlFor="int-answer">
                Your answer
                <span className="cv-optional" style={{ marginLeft: "0.5rem" }}>
                  Ctrl/⌘ + Enter to submit
                </span>
              </label>
              <textarea
                id="int-answer"
                ref={answerRef}
                className="cv-ai-textarea cv-interview-textarea"
                rows={4}
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your answer here…"
                aria-required="true"
                aria-label="Your interview answer"
              />
              <div className="cv-interview-answer-footer">
                <button
                  className="ghost-button"
                  type="button"
                  onClick={handleReset}
                >
                  Exit interview
                </button>
                <button
                  className="primary-button"
                  type="button"
                  onClick={handleSubmitAnswer}
                  disabled={!answer.trim() || isSubmitting}
                >
                  {isSubmitting ? <><Brain size={16} aria-hidden="true" /> Evaluating…</> : <><Check size={16} aria-hidden="true" /> Submit answer</>}
                </button>
                <button
                  className="ghost-button"
                  type="button"
                  onClick={handleComplete}
                  disabled={!session?.transcript?.length || isSubmitting}
                >
                  Complete interview
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── DONE ── */}
      {phase === "done" && (
        <div className="cv-interview-done">
          <div className="cv-interview-done-header panel-card">
            <div className="cv-interview-done-icon" aria-hidden="true">
              🏁
            </div>
            <div>
              <h3>Interview Completed</h3>
              <p className="cv-ai-hero-desc">
                You answered all {questions.length} questions.{" "}
                {targetRole
                  ? `Good work preparing for ${targetRole}.`
                  : "Good work!"}
              </p>
            </div>
          </div>

          {/* Full transcript review */}
          <div className="panel-card">
            <h4 className="cv-section-title">Session Review</h4>
            <p className="muted-copy" style={{ marginBottom: "1rem" }}>
              Your answers are shown below. The AI interviewer used your real
              projects and skills. No scores are provided — this is practice
              based on profile evidence only.
            </p>
            <div className="cv-review-list">
              {questions.map((q, i) => {
                const entry = session?.transcript?.[i];
                const userMsg = entry ? { text: entry.answer } : null;
                return (
                  <div key={i} className="cv-review-item">
                    <div className="cv-review-q-header">
                      <span className="cv-question-num">Q{i + 1}</span>
                      <div>
                        <span className="tag">{q.question_type}</span>
                        <span
                          className={`cv-diff-badge cv-diff-${q.difficulty}`}
                          style={{ marginLeft: "0.4rem" }}
                        >
                          {q.difficulty}
                        </span>
                        {q.topic && (
                          <span
                            className="muted-copy"
                            style={{
                              marginLeft: "0.5rem",
                              fontSize: "0.82rem",
                            }}
                          >
                            {q.topic}
                          </span>
                        )}
                      </div>
                    </div>
                    <p className="cv-review-question">{q.question}</p>
                    {userMsg && (
                      <div className="cv-review-answer">
                        <span className="cv-review-answer-label">
                          Your answer
                        </span>
                        <p>{userMsg.text}</p>
                      </div>
                    )}
                    {q.supporting_skills?.length > 0 && (
                      <div
                        className="cv-evidence-group"
                        style={{ marginTop: "0.5rem" }}
                      >
                        <p className="cv-evidence-label">Evidence basis</p>
                        <TagGroup
                          items={q.supporting_skills}
                          variant="skill"
                          max={4}
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {session?.final_report && (
            <div className="panel-card">
              <h4 className="cv-section-title">Final AI Report</h4>
              <p className="cv-ai-hero-desc">
                {session.final_report.overall_interview_summary}
              </p>
              {session.final_report.strengths?.length > 0 && (
                <p className="muted-copy">
                  <strong>Strengths:</strong>{" "}
                  {session.final_report.strengths.join(", ")}
                </p>
              )}
              {session.final_report.improvement_areas?.length > 0 && (
                <p className="muted-copy">
                  <strong>Preparation areas:</strong>{" "}
                  {session.final_report.improvement_areas.join(", ")}
                </p>
              )}
              {session.final_report.skill_areas_demonstrated?.length > 0 && (
                <div className="cv-report-section">
                  <strong>What you demonstrated</strong>
                  <TagGroup items={session.final_report.skill_areas_demonstrated} variant="skill" />
                </div>
              )}
              {session.final_report.unanswered_or_weak_areas?.length > 0 && (
                <div className="cv-report-section">
                  <strong>Areas to strengthen</strong>
                  <TagGroup items={session.final_report.unanswered_or_weak_areas} variant="default" />
                </div>
              )}
              {session.final_report.recommended_preparation_areas?.length > 0 && (
                <div className="cv-report-section">
                  <strong>Recommended preparation areas</strong>
                  <TagGroup items={session.final_report.recommended_preparation_areas} variant="tech" />
                </div>
              )}
            </div>
          )}

          <div className="cv-interview-done-actions">
            <button
              className="ghost-button"
              type="button"
              onClick={handleReset}
            >
              Start new interview
            </button>
            <Link className="primary-button" to={`/ai/intelligence${targetRole ? `?role=${encodeURIComponent(targetRole)}` : ""}`}>View Career Intelligence</Link>
            <Link className="ghost-button" to={`/skill-gap?role=${encodeURIComponent(targetRole)}`}>Review Skill Gaps</Link>
          </div>
        </div>
      )}
    </div>
  );
}

function InterviewMessage({ msg, isCurrent }) {
  const isAI = msg.role === "ai";
  const q = msg.question;
  return (
    <div
      className={`cv-chat-msg ${isAI ? "cv-chat-msg-ai" : "cv-chat-msg-user"} ${isCurrent ? "cv-chat-msg-current" : ""}`}
    >
      {isAI && (
        <div className="cv-chat-avatar" aria-hidden="true">
          {msg.isGreeting ? "👋" : "🤖"}
        </div>
      )}
      <div className="cv-chat-bubble">
        {msg.isEvaluation && (
          <p className="cv-chat-q-meta cv-interview-feedback-label">Interview feedback</p>
        )}
        {isAI && !msg.isGreeting && q && (
          <div className="cv-chat-q-meta">
            <span className="tag">{q.question_type}</span>
            <span className={`cv-diff-badge cv-diff-${q.difficulty}`}>
              {q.difficulty}
            </span>
            {q.topic && <span className="cv-chat-topic">{q.topic}</span>}
          </div>
        )}
        <p className="cv-chat-text">{msg.text}</p>
        {msg.isEvaluation && msg.evaluation?.strengths?.length ? (
          <div className="cv-interview-feedback-group"><strong>Strengths</strong><TagGroup items={msg.evaluation.strengths} variant="skill" /></div>
        ) : null}
        {msg.isEvaluation && msg.evaluation?.improvements?.length ? (
          <div className="cv-interview-feedback-group"><strong>Areas to improve</strong><TagGroup items={msg.evaluation.improvements} variant="default" /></div>
        ) : null}
      </div>
      {!isAI && (
        <div className="cv-chat-avatar cv-chat-avatar-user" aria-hidden="true">
          You
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// CAREER INTELLIGENCE PAGE — Combined multi-agent
// ═══════════════════════════════════════════════════════════════════════════════

const QUICK_ACTIONS = [
  {
    label: "What roles suit me?",
    query: "What career roles are suitable for me based on my profile?",
    icon: "💼",
  },
  {
    label: "Backend Developer gaps",
    query: "Evaluate my skill gaps for Backend Developer.",
    icon: "📊",
  },
  {
    label: "Interview questions",
    query: "Generate personalised interview questions based on my experience.",
    icon: "🎤",
  },
  {
    label: "Full career plan",
    query:
      "Recommend career roles, evaluate my skill gaps for Backend Developer, and prepare interview questions.",
    icon: "🧠",
  },
];

function CareerIntelligencePage() {
  const [query, setQuery] = useState("");
  const [role, setRole] = useState("");
  const [language, setLanguage] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [validErr, setValidErr] = useState("");

  const handleSubmit = async (e, overrideQuery) => {
    e?.preventDefault();
    setValidErr("");
    const q = (overrideQuery ?? query).trim();
    if (!q) {
      setValidErr("Please enter a question.");
      return;
    }
    setBusy(true);
    setError("");
    setResult(null);
    try {
      setResult(await aiIntelligence(q, role.trim() || null, language || null));
    } catch (err) {
      setError(
        getApiError(
          err,
          "The career intelligence request could not be completed.",
        ),
      );
    } finally {
      setBusy(false);
    }
  };

  const handleQuickAction = (qa) => {
    setQuery(qa.query);
    handleSubmit(null, qa.query);
  };

  const hasRecs = result?.recommendations?.length > 0;
  const hasGaps = result?.skill_gaps?.length > 0;
  const hasQs = result?.interview_preparation?.length > 0;

  return (
    <div className="cv-ai-page">
      <div className="cv-ai-hero">
        <div className="cv-ai-hero-icon" aria-hidden="true">
          🧠
        </div>
        <div>
          <p className="eyebrow">AI · Career Intelligence</p>
          <h2 className="cv-ai-hero-title">Career Intelligence</h2>
          <p className="cv-ai-hero-desc">
            Your personalised AI career assistant. Ask anything in English,
            Tamil (தமிழ்) or Hindi (हिन्दी). The AI automatically routes your
            query through the right agents.
          </p>
        </div>
      </div>

      {/* ── Main form ── */}
      <form className="cv-ai-form panel-card" onSubmit={handleSubmit}>
        <label className="cv-field-label" htmlFor="intel-query">
          <span className="cv-field-icon" aria-hidden="true">
            ✏️
          </span>
          Ask your career assistant
        </label>
        <textarea
          id="intel-query"
          className="cv-ai-textarea"
          rows={3}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Recommend roles, evaluate my skill gaps for Backend Developer, and prepare interview questions."
          disabled={busy}
          aria-required="true"
        />
        <div className="cv-ai-form-row-2col" style={{ marginTop: "0.75rem" }}>
          <div>
            <label className="cv-field-label" htmlFor="intel-role">
              <span className="cv-field-icon" aria-hidden="true">
                🎯
              </span>
              Target role override <span className="cv-optional">optional</span>
            </label>
            <input
              id="intel-role"
              className="cv-ai-input"
              type="text"
              list="intel-role-list"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="e.g. Backend Developer"
              disabled={busy}
            />
            <datalist id="intel-role-list">
              {KNOWN_ROLES.map((r) => (
                <option key={r} value={r} />
              ))}
            </datalist>
          </div>
          <LanguageSelector
            value={language}
            onChange={setLanguage}
            disabled={busy}
          />
        </div>
        {validErr && (
          <p className="cv-field-error" role="alert">
            {validErr}
          </p>
        )}
        <div className="cv-ai-form-footer">
          <button
            className="primary-button cv-ai-submit-btn"
            type="submit"
            disabled={busy}
            aria-busy={busy}
          >
            {busy ? (
              <>
                <span className="spinner" aria-hidden="true" /> Running
                intelligence…
              </>
            ) : (
              "Run Intelligence →"
            )}
          </button>
        </div>
      </form>

      {/* ── Quick actions ── */}
      {!busy && !result && !error && (
        <div className="cv-quick-actions">
          <p className="cv-evidence-label">Quick actions</p>
          <div className="cv-quick-action-grid">
            {QUICK_ACTIONS.map((qa) => (
              <button
                key={qa.label}
                type="button"
                className="cv-quick-action-btn panel-card"
                onClick={() => handleQuickAction(qa)}
              >
                <span className="cv-quick-action-icon" aria-hidden="true">
                  {qa.icon}
                </span>
                <span>{qa.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {busy && <AILoadingState mode="ai-intelligence" />}
      {!busy && error && (
        <ErrorState
          message={error}
          onRetry={() => {
            setError("");
            setResult(null);
          }}
        />
      )}

      {!busy && !error && result && (
        <div className="cv-ai-result">
          {/* ── Response header ── */}
          <div className="cv-intel-response-header panel-card">
            <div className="cv-intel-agents">
              <p className="cv-evidence-label">Agents executed</p>
              <div className="cv-agents-row">
                {(result.agents_used || []).map((a) => (
                  <span key={a} className={`cv-agent-badge cv-agent-${a}`}>
                    {a}
                  </span>
                ))}
              </div>
            </div>
            {result.language && result.language !== "en" && (
              <div className="cv-response-lang-bar">
                <span className="cv-response-lang-badge">
                  {LANG_LABELS[result.language] || result.language}
                </span>
              </div>
            )}
          </div>

          {/* ── Summary ── */}
          {result.summary && (
            <div className="cv-ai-narrative panel-card cv-intel-summary">
              <p className="cv-evidence-label">Summary</p>
              <p>{result.summary}</p>
              {result.final_guidance && (
                <>
                  <p
                    className="cv-evidence-label"
                    style={{ marginTop: "1rem" }}
                  >
                    Guidance
                  </p>
                  <p>{result.final_guidance}</p>
                </>
              )}
            </div>
          )}

          {/* ── Recommendations ── */}
          {hasRecs && (
            <section className="cv-intel-section">
              <h3 className="cv-intel-section-title">
                <span aria-hidden="true">💼</span> Career Recommendations
              </h3>
              <div className="cv-rec-grid">
                {result.recommendations.map((rec, i) => (
                  <RecommendCard key={rec.title + i} rec={rec} />
                ))}
              </div>
            </section>
          )}

          {/* ── Skill gaps ── */}
          {hasGaps && (
            <section className="cv-intel-section">
              <h3 className="cv-intel-section-title">
                <span aria-hidden="true">📊</span> Skill Gap Analysis
                {result.evaluation_details?.target_role &&
                  ` · ${result.evaluation_details.target_role}`}
              </h3>
              {result.evaluation_details?.summary && (
                <p
                  className="cv-ai-hero-desc"
                  style={{ marginBottom: "0.75rem" }}
                >
                  {result.evaluation_details.summary}
                </p>
              )}
              <div className="cv-gap-columns">
                <div className="panel-card cv-gap-column cv-gap-column-ok">
                  <h4 className="cv-gap-col-title">
                    <span aria-hidden="true">✓</span> Strengths
                  </h4>
                  {result.evaluation_details?.strengths?.length > 0 ? (
                    <ul className="cv-strength-list">
                      {result.evaluation_details.strengths.map((s) => (
                        <li key={s} className="cv-strength-item">
                          <span
                            className="cv-strength-check"
                            aria-hidden="true"
                          >
                            ✓
                          </span>
                          {s}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="muted-copy">No strengths data available.</p>
                  )}
                </div>
                <div className="panel-card cv-gap-column cv-gap-column-miss">
                  <h4 className="cv-gap-col-title">
                    <span aria-hidden="true">⚡</span> Skills to Develop
                  </h4>
                  <ul className="cv-gap-pill-list">
                    {result.skill_gaps
                      .filter((g) => g.gap_level !== "none")
                      .map((g) => (
                        <li
                          key={g.skill}
                          className={`cv-gap-pill ${GAP_META[g.gap_level]?.cls || ""}`}
                        >
                          <span className="cv-gap-pill-name">{g.skill}</span>
                          <span className="cv-gap-pill-level">
                            {GAP_META[g.gap_level]?.label}
                          </span>
                        </li>
                      ))}
                  </ul>
                </div>
              </div>
            </section>
          )}

          {/* ── Interview questions ── */}
          {hasQs && (
            <section className="cv-intel-section">
              <h3 className="cv-intel-section-title">
                <span aria-hidden="true">🎤</span> Interview Preparation
                {result.interview_details?.target_role &&
                  ` · ${result.interview_details.target_role}`}
              </h3>
              {result.interview_details?.preparation_summary && (
                <p
                  className="cv-ai-hero-desc"
                  style={{ marginBottom: "0.75rem" }}
                >
                  {result.interview_details.preparation_summary}
                </p>
              )}
              <div className="cv-question-list">
                {result.interview_preparation.map((q, i) => (
                  <IntelQuestionCard key={i} q={q} num={i + 1} />
                ))}
              </div>
            </section>
          )}

          {!result.summary && !hasRecs && !hasGaps && !hasQs && (
            <EmptyState title="No intelligence results returned">
              Try a more specific query, e.g. "Recommend roles and evaluate my
              skill gaps for Backend Developer."
            </EmptyState>
          )}

          {/* Pipeline warnings (non-fatal) */}
          {result.errors?.filter(Boolean).length > 0 && (
            <div className="cv-pipeline-warnings">
              <p className="cv-evidence-label">Pipeline notes</p>
              {result.errors.filter(Boolean).map((err, i) => (
                <p key={i} className="cv-pipeline-warning-item">
                  {err.split(":")[0]}
                </p>
              ))}
            </div>
          )}
        </div>
      )}

      {!busy && !error && !result && (
        <EmptyState title="Ready when you are">
          Enter your question above or choose a quick action.
        </EmptyState>
      )}
    </div>
  );
}

function IntelQuestionCard({ q, num }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="cv-question-card panel-card">
      <div className="cv-question-header">
        <span className="cv-question-num" aria-hidden="true">
          Q{num}
        </span>
        <div className="cv-question-meta-row">
          <span className="tag">{q.question_type}</span>
          <span className={`cv-diff-badge cv-diff-${q.difficulty}`}>
            {q.difficulty}
          </span>
        </div>
      </div>
      <p className="cv-question-text">{q.question}</p>
      {(q.topic || q.rationale || q.supporting_skills?.length > 0) && (
        <button
          type="button"
          className="cv-expand-btn"
          onClick={() => setExpanded((v) => !v)}
          aria-expanded={expanded}
        >
          {expanded ? "Hide context" : "Show context"}
        </button>
      )}
      {expanded && (
        <div className="cv-question-detail">
          {q.topic && (
            <p className="cv-evidence-label">
              Topic: <strong>{q.topic}</strong>
            </p>
          )}
          {q.rationale && <p className="cv-rationale">{q.rationale}</p>}
          {q.supporting_skills?.length > 0 && (
            <div className="cv-evidence-group">
              <p className="cv-evidence-label">Evidence basis</p>
              <TagGroup items={q.supporting_skills} variant="skill" max={4} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// PAGE ROUTER
// ═══════════════════════════════════════════════════════════════════════════════

const PAGE_COMPONENTS = {
  "ai-recommend": RecommendPage,
  "ai-skill-gap": SkillGapPage,
  "ai-interview": InterviewPage,
  "ai-intelligence": CareerIntelligencePage,
};

export default function AIPage({ mode }) {
  const PageComponent = PAGE_COMPONENTS[mode];
  if (!PageComponent) {
    return (
      <div className="cv-ai-page">
        <ErrorState message={`Unknown AI mode: "${mode}"`} />
      </div>
    );
  }
  return <PageComponent />;
}
