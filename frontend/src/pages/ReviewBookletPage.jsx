import React, { useState, useEffect } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  Sparkles,
  Bot,
  Award,
  BookOpen,
  Loader2,
  ChevronLeft,
  ChevronRight,
  FileText,
  Search,
  Check,
  Target,
  Lightbulb,
  Printer,
  History,
  Plus,
} from "lucide-react";
import { getInterviewBooklet, getInterviewSessionsList } from "../services/careerService";
import { getApiError } from "../services/api";

export default function ReviewBookletPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [booklet, setBooklet] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeSpread, setActiveSpread] = useState(0);

  // Past sessions archive
  const [sessionList, setSessionList] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [personalReflection, setPersonalReflection] = useState("");

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError("");

      try {
        // Fetch session list for the archive sidebar
        const listRes = await getInterviewSessionsList(50, 0).catch(() => []);
        const rawSessions = Array.isArray(listRes) ? listRes : listRes?.sessions || [];
        if (!cancelled) {
          setSessionList(rawSessions);
        }

        const effectiveId = sessionId || rawSessions[0]?.session_id || rawSessions[0]?.id;
        if (!effectiveId) {
          if (!cancelled) {
            setError("No session specified.");
            setLoading(false);
          }
          return;
        }

        const data = await getInterviewBooklet(effectiveId);
        if (!cancelled) {
          setBooklet(data);
          setActiveSpread(0);
          setPersonalReflection(data.overall_interview_summary || "");
        }
      } catch (err) {
        if (!cancelled) setError(getApiError(err, "Could not load review booklet."));
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  const filteredSessions = sessionList.filter((s) => {
    const q = searchQuery.toLowerCase();
    const role = (s.target_role || s.role || "").toLowerCase();
    const mode = (s.interview_mode || s.mode || "").toLowerCase();
    const id = (s.session_id || s.id || "").toLowerCase();
    return role.includes(q) || mode.includes(q) || id.includes(q);
  });

  if (loading) {
    return (
      <div className="practice-scope">
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "60vh", color: "var(--pr-muted-ink)" }}>
          <Loader2 size={32} style={{ animation: "spin 1s linear infinite", marginBottom: "12px", color: "var(--pr-green)" }} />
          <div style={{ fontSize: "1rem", fontWeight: 600, fontFamily: "var(--pr-font-sans)" }}>Loading review booklet…</div>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      </div>
    );
  }

  if (error && !booklet) {
    return (
      <div className="practice-scope">
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "60vh", color: "var(--pr-ink)", textAlign: "center", padding: "24px" }}>
          <AlertCircle size={36} color="var(--pr-peach)" style={{ marginBottom: "12px" }} />
          <div style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "14px", color: "var(--pr-ink)" }}>{error}</div>
          <button
            type="button"
            onClick={() => navigate("/ai/interview")}
            className="pr-button pr-button-primary"
          >
            <ArrowLeft size={16} /> Back to Interview
          </button>
        </div>
      </div>
    );
  }

  if (!booklet) {
    return (
      <div className="practice-scope">
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "60vh", color: "var(--pr-muted-ink)" }}>
          <BookOpen size={36} style={{ marginBottom: "12px", color: "var(--pr-green)" }} />
          <div style={{ fontSize: "1rem", fontWeight: 600 }}>No booklet available for this session.</div>
          <button
            type="button"
            onClick={() => navigate("/ai/interview")}
            className="pr-button pr-button-primary"
            style={{ marginTop: "16px" }}
          >
            <ArrowLeft size={16} /> Go to Interview Room
          </button>
        </div>
      </div>
    );
  }

  const spreads = booklet.spreads || [];
  const spread = spreads[activeSpread] || null;
  const total = spreads.length;

  return (
    <div className="practice-scope">
      <div className="work-page">
        {/* Page Head */}
        <div className="page-head">
          <div>
            <div className="eyebrow">
              <span className="eyebrow-rule" />
              PAST INTERVIEW QUESTIONS
            </div>
            <h1>Review booklet</h1>
            <p className="page-deck">
              Revisit questions from your interview sessions, along with your recorded answers and personal reflections.
            </p>
          </div>
          <div className="head-action" style={{ display: "flex", gap: "10px", alignItems: "center" }}>
            <button
              type="button"
              className="pr-button pr-button-secondary"
              onClick={() => navigate("/ai/interview")}
            >
              <ArrowLeft size={16} /> Back to Interview
            </button>
            <Link
              to="/ai/interview"
              className="pr-button pr-button-primary"
              data-testid="link-archive-practice"
            >
              <Plus size={16} /> New practice session
            </Link>
          </div>
        </div>

        {/* 2-Column Archive Layout */}
        <div className="archive-layout">
          {/* Left Panel: Past Sessions List */}
          <aside className="session-list-panel">
            <div className="session-list-head">
              <div>
                <span className="eyebrow" style={{ fontSize: "9px" }}>PAST SESSIONS</span>
                <b>{sessionList.length > 0 ? sessionList.length : 1} booklet{sessionList.length === 1 ? "" : "s"}</b>
              </div>
              <History size={16} />
            </div>

            <div className="session-search">
              <Search size={15} />
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Find a session..."
                aria-label="Search interview sessions"
                data-testid="input-search-sessions"
              />
            </div>

            <div className="session-list">
              {filteredSessions.length > 0 ? (
                filteredSessions.map((s) => {
                  const sId = s.session_id || s.id;
                  const isActive = (booklet?.session_id === sId) || (sessionId === sId);
                  const dateStr = s.created_at ? new Date(s.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) : "Recent";
                  return (
                    <button
                      key={sId}
                      type="button"
                      className={`session-option ${isActive ? "session-option-active" : ""}`}
                      onClick={() => navigate(`/ai/interview/booklet/${sId}`)}
                      data-testid={`button-session-${sId}`}
                    >
                      <span className="session-date">{dateStr}</span>
                      <b>{s.target_role || s.role || "Software Engineer"}</b>
                      <span className="session-option-bottom">
                        {s.interview_mode || "Technical"} <i /> {s.question_count || total} prompts
                      </span>
                    </button>
                  );
                })
              ) : (
                <div style={{ padding: "16px", textAlign: "center", fontSize: "11px", color: "var(--pr-muted-ink)" }}>
                  Current Session: {booklet.session_id}
                </div>
              )}
            </div>

            <div className="archive-sidebar-foot">
              <span className="local-dot" /> Private to your session workspace
            </div>
          </aside>

          {/* Right Panel: Booklet View */}
          <section className="booklet-area">
            {/* Booklet Topline */}
            <div className="booklet-topline">
              <div>
                <span className="booklet-session-code">
                  REVIEW BOOKLET / {String(booklet.session_id).slice(-6).toUpperCase()}
                </span>
                <h2>{booklet.target_role || "Technical Evaluation"}</h2>
                <p>
                  <span>Session {booklet.session_id}</span>
                  <i />
                  <span>{booklet.interview_mode || "General"}</span>
                  <i />
                  <span>{booklet.language ? booklet.language.toUpperCase() : "EN"}</span>
                  <i />
                  <span>{total} question spread{total !== 1 ? "s" : ""}</span>
                </p>
              </div>
              <span className={`status-tag ${booklet.status === "completed" ? "tag-done" : "tag-progress"}`}>
                {booklet.status === "completed" ? "Completed" : (booklet.status || "In Progress")}
              </span>
            </div>

            {/* Personal Session Reflection Card */}
            <div className="reflection-card">
              <div className="reflection-title">
                <span className="reflection-icon">
                  <FileText size={17} />
                </span>
                <div>
                  <b>Your session reflection & key takeaways</b>
                  <small>Personal notes saved locally · captures your trade-offs and growth areas</small>
                </div>
                <span className="saved-label">
                  <Check size={13} /> Saved locally
                </span>
              </div>
              <textarea
                value={personalReflection}
                onChange={(e) => setPersonalReflection(e.target.value)}
                placeholder="What felt strong? What architecture trade-off or complexity bounds would you state differently next time?"
                aria-label="Session reflection"
                data-testid="textarea-session-reflection"
              />
            </div>

            {/* Overall Strengths & Improvement Areas Summary */}
            {(booklet.strengths?.length > 0 || booklet.improvement_areas?.length > 0 || booklet.skill_areas_demonstrated?.length > 0) && (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                  gap: "12px",
                  marginBottom: "16px",
                  background: "var(--pr-white-paper)",
                  padding: "14px 16px",
                  borderRadius: "6px",
                  border: "1px solid var(--pr-line)",
                }}
              >
                {booklet.strengths?.length > 0 && (
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "var(--pr-green)", fontWeight: 700, fontSize: "11px", marginBottom: "6px" }}>
                      <CheckCircle2 size={13} /> Strengths
                    </div>
                    <ul style={{ margin: 0, paddingLeft: "16px", fontSize: "11px", color: "var(--pr-ink)", lineHeight: 1.5 }}>
                      {booklet.strengths.map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {booklet.improvement_areas?.length > 0 && (
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "var(--pr-peach)", fontWeight: 700, fontSize: "11px", marginBottom: "6px" }}>
                      <AlertTriangle size={13} /> Areas to Improve
                    </div>
                    <ul style={{ margin: 0, paddingLeft: "16px", fontSize: "11px", color: "var(--pr-ink)", lineHeight: 1.5 }}>
                      {booklet.improvement_areas.map((a, i) => (
                        <li key={i}>{a}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {booklet.skill_areas_demonstrated?.length > 0 && (
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#3b82f6", fontWeight: 700, fontSize: "11px", marginBottom: "6px" }}>
                      <Award size={13} /> Skills Demonstrated
                    </div>
                    <ul style={{ margin: 0, paddingLeft: "16px", fontSize: "11px", color: "var(--pr-ink)", lineHeight: 1.5 }}>
                      {booklet.skill_areas_demonstrated.map((sk, i) => (
                        <li key={i}>{sk}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Spread Navigation Controls */}
            {total > 1 && (
              <div className="spread-controls">
                <div className="spread-progress">
                  {spreads.map((_, i) => (
                    <button
                      key={i}
                      type="button"
                      className={`spread-dot ${i === activeSpread ? "spread-dot-active" : ""}`}
                      onClick={() => setActiveSpread(i)}
                      aria-label={`Open question ${i + 1}`}
                      data-testid={`button-spread-${i + 1}`}
                    />
                  ))}
                </div>
                <span className="spread-count">
                  Spread {activeSpread + 1} of {total}
                </span>
                <div className="spread-arrows">
                  <button
                    type="button"
                    className="pr-button pr-button-secondary"
                    style={{ minHeight: "32px", padding: "0 12px", fontSize: "11px" }}
                    onClick={() => setActiveSpread((p) => Math.max(0, p - 1))}
                    disabled={activeSpread === 0}
                    aria-label="Previous"
                    data-testid="button-previous-spread"
                  >
                    <ChevronLeft size={14} /> Previous
                  </button>
                  <button
                    type="button"
                    className="pr-button pr-button-secondary"
                    style={{ minHeight: "32px", padding: "0 12px", fontSize: "11px" }}
                    onClick={() => setActiveSpread((p) => Math.min(total - 1, p + 1))}
                    disabled={activeSpread >= total - 1}
                    aria-label="Next"
                    data-testid="button-next-spread"
                  >
                    Next <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            )}

            {/* 2-Column Open Book Spread */}
            {spread && (
              <div className="booklet-spread" data-testid={`spread-content-${activeSpread + 1}`}>
                {/* Left Page: Question */}
                <article className="spread-question">
                  <div className="spread-label">
                    <span>THE PROMPT</span>
                    <span>QUESTION {String(spread.sequence_number || activeSpread + 1).padStart(2, "0")}</span>
                  </div>
                  {spread.question?.topic && (
                    <div className="topic-pill" style={{ marginBottom: "14px" }}>
                      <Target size={12} /> {spread.question.topic}
                    </div>
                  )}
                  <h3>
                    {spread.question?.question_text || spread.question?.question || spread.question || "Question prompt"}
                  </h3>
                  <div className="spread-quote-mark">“</div>
                </article>

                {/* Right Page: Candidate's Response & Feedback */}
                <article className="spread-answer">
                  <div className="spread-label">
                    <span>YOUR RESPONSE</span>
                    <span>
                      {spread.skipped
                        ? "SKIPPED"
                        : spread.unanswered || !spread.answer
                        ? "NOT ANSWERED"
                        : "AS RECORDED"}
                    </span>
                  </div>

                  <div className={`answer-record ${spread.skipped || spread.unanswered || !spread.answer ? "answer-skipped" : ""}`}>
                    {spread.skipped
                      ? "Answer unavailable (question was skipped). Use this prompt as a starting point next time."
                      : spread.unanswered || !spread.answer
                      ? "Not answered yet. Use this question to rehearse your solution approach."
                      : spread.answer}
                  </div>

                  {/* Socratic Feedback & Session Notes */}
                  {spread.evaluation && (
                    <div className="feedback-block">
                      <span className="feedback-label">
                        <Lightbulb size={14} /> SESSION NOTE & EVALUATION
                      </span>
                      {spread.evaluation.assessment && (
                        <p>{spread.evaluation.assessment}</p>
                      )}
                      {spread.evaluation.ideal_pitch_script && (
                        <div style={{ marginTop: "8px", background: "var(--pr-paper)", padding: "10px", borderRadius: "5px", fontSize: "11px", color: "var(--pr-ink)" }}>
                          <strong>Ideal Pitch Model:</strong> {spread.evaluation.ideal_pitch_script}
                        </div>
                      )}
                      {spread.evaluation.improvements && spread.evaluation.improvements.length > 0 && (
                        <p style={{ marginTop: "6px", color: "var(--pr-peach)" }}>
                          <strong>Suggested Refinement:</strong> {spread.evaluation.improvements.join("; ")}
                        </p>
                      )}
                      <small style={{ display: "block", marginTop: "8px", color: "var(--pr-muted-ink)" }}>
                        Feedback is grounded in production system design and SDE hiring benchmarks.
                      </small>
                    </div>
                  )}
                </article>
              </div>
            )}

            {/* Booklet Footnote */}
            <div className="booklet-footnote">
              <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <BookOpen size={15} color="var(--pr-green)" />
                Keep what you learned. Return to your review booklet whenever you prepare for interviews.
              </span>
              <button
                type="button"
                className="pr-text-button"
                onClick={() => window.print()}
                data-testid="button-print-booklet"
              >
                <Printer size={14} /> Print booklet <ArrowLeft size={12} style={{ transform: "rotate(180deg)" }} />
              </button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
