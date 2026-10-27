import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  ArrowLeft,
  Compass,
  CheckCircle2,
  Circle,
  Sparkles,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import {
  createCareerQuizSession,
  getCareerQuizSession,
  submitCareerQuizAnswer,
  completeCareerQuiz,
} from "../services/careerService";
import { getApiError } from "../services/api";

export default function CareerQuizPage() {
  const [phase, setPhase] = useState("start"); // "start" | "active" | "complete"
  const [session, setSession] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState("");
  const [customText, setCustomText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const startQuiz = async () => {
    setLoading(true);
    setError("");
    try {
      const sess = await createCareerQuizSession("en");
      setSession(sess);
      const q = sess.current_question || sess.questions?.[sess.current_question_index || 0];
      setCurrentQuestion(q);
      setSelectedAnswer("");
      setCustomText("");
      setPhase("active");
    } catch (err) {
      setError(getApiError(err, "Could not start career compass quiz."));
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAnswer = async (ans) => {
    const finalAnswer = (ans || customText || "").trim();
    if (!finalAnswer) return;
    setSelectedAnswer(finalAnswer);
    setLoading(true);
    setError("");
    try {
      const sessionId = session?.session_id || session?.id;
      const resp = await submitCareerQuizAnswer(sessionId, finalAnswer);
      setSession(resp);

      // Detect completion: explicit completed status OR no more questions
      const isComplete =
        resp.status === "completed" ||
        resp.is_complete === true ||
        resp.is_complete === "true" ||
        (!resp.current_question &&
          (!resp.questions || resp.question_number >= (resp.total_questions || 5)));

      if (isComplete) {
        // Fetch final result then show complete screen
        try {
          const finalResult = await completeCareerQuiz(sessionId);
          setResult(finalResult?.result || finalResult);
        } catch {
          // completeCareerQuiz may 409 if already completed — use session result
          setResult(resp.result || resp);
        }
        setPhase("complete");
      } else if (resp.current_question) {
        setCurrentQuestion(resp.current_question);
        setSelectedAnswer("");
        setCustomText("");
      } else {
        try {
          const finalResult = await completeCareerQuiz(sessionId);
          setResult(finalResult?.result || finalResult);
        } catch {
          setResult(resp.result || resp);
        }
        setPhase("complete");
      }
    } catch (err) {
      setError(getApiError(err, "Failed to record answer."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--cv-space-8)" }}>
      {/* ─── CHAPTER INTRO ───────────────────────────────────────────────── */}
      <header className="cv-chapter-intro">
        <span className="cv-chapter-number">CHAPTER 03</span>
        <div>
          <div className="cv-chapter-kicker">03 &nbsp; / &nbsp; Career Compass</div>
          <h1 className="cv-chapter-title">
            A compass is useful<br /><span className="serif">when it listens.</span>
          </h1>
          <p className="cv-chapter-deck">
            Take a reflective career assessment to map your working preferences, technical inclinations,
            and leadership style to uncover where you excel most naturally.
          </p>
          {error && (
            <div className="cv-note-block" style={{ borderColor: "var(--cv-danger)", color: "var(--cv-danger)", marginTop: "16px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <AlertCircle size={16} />
                <div><strong>AI Service Notice:</strong> {error}</div>
              </div>
              <button
                type="button"
                className="cv-text-button"
                onClick={startQuiz}
                style={{ cursor: "pointer", color: "var(--cv-accent)", fontWeight: 600 }}
              >
                Retry
              </button>
            </div>
          )}
        </div>
        <p className="cv-intro-aside">
          All responses are evaluated against verified industry roles to suggest natural career trajectories.
        </p>
      </header>

      {/* ─── PHASE: START QUIZ ───────────────────────────────────────────── */}
      {phase === "start" && (
        <section className="cv-editorial-section">
          <div className="cv-section-index">01 / DISCOVERY ASSESSMENT</div>
          <div className="cv-section-content">
            <h2 style={{ color: "var(--text, var(--cv-text))", fontSize: "1.45rem", marginTop: "8px", marginBottom: "16px" }}>
              Find Your Direction Through Reflection
            </h2>
            <p style={{ color: "var(--text-muted, var(--cv-text-muted))" }}>
              Answer 5 situational questions designed to test your instincts regarding systems design,
              product trade-offs, team leadership, and autonomy.
            </p>

            <div className="cv-note-block" style={{ margin: "20px 0" }}>
              <Compass size={18} color="var(--cv-accent)" />
              <div>
                <strong>Takes under 2 minutes.</strong>
                Results are saved directly to your candidate dossier and inform your personalized learning roadmap.
              </div>
            </div>

            <div style={{ marginTop: "24px" }}>
              <button
                type="button"
                className="cv-auth-btn"
                style={{ width: "auto", padding: "0 28px", height: "46px" }}
                onClick={startQuiz}
                disabled={loading}
              >
                {loading ? "Initializing Compass…" : "Begin Career Assessment →"}
              </button>
            </div>
          </div>
        </section>
      )}

      {/* ─── PHASE: ACTIVE QUESTION ──────────────────────────────────────── */}
      {phase === "active" && currentQuestion && (
        <section className="cv-editorial-section">
          <div className="cv-section-index">
            {session?.current_question_index !== undefined ? `0${session.current_question_index + 1} / 05` : "QUESTION"}
          </div>
          <div className="cv-section-content">
            <span style={{ fontSize: "0.75rem", fontFamily: "var(--cv-font-mono)", color: "var(--accent, var(--cv-accent))", textTransform: "uppercase", fontWeight: 700 }}>
              {currentQuestion.category || "Career Preference"}
            </span>
            <h2 style={{ fontSize: "1.45rem", marginTop: "8px", marginBottom: "20px", color: "var(--text, var(--cv-text))" }}>
              {currentQuestion.question_text || currentQuestion.text || currentQuestion.question}
            </h2>
            
            {/* Progress dots */}
            <div style={{ display: "flex", gap: "6px", alignItems: "center", marginBottom: "20px" }}>
              {Array.from({ length: session?.total_questions || 5 }, (_, i) => (
                <span
                  key={i}
                  style={{
                    width: 8, height: 8, borderRadius: "50%",
                    background: i < (session?.question_number || session?.answers?.length || 0)
                      ? "var(--accent, var(--cv-accent))"
                      : i === (session?.question_number || session?.answers?.length || 0)
                      ? "var(--accent, var(--cv-accent))"
                      : "var(--border, var(--cv-rule))",
                    border: i === (session?.question_number || session?.answers?.length || 0) ? "2px solid var(--accent, var(--cv-accent))" : "none",
                    transition: "all 0.2s",
                  }}
                />
              ))}
              <span style={{ fontSize: "0.72rem", color: "var(--text-muted, var(--cv-muted))", marginLeft: "4px" }}>
                {(session?.question_number || (session?.answers?.length || 0) + 1)} of {session?.total_questions || 5}
              </span>
            </div>

            {/* Options List (if provided) */}
            {Array.isArray(currentQuestion.options || currentQuestion.choices) && (currentQuestion.options || currentQuestion.choices).length > 0 && (
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "16px" }}>
                {(currentQuestion.options || currentQuestion.choices).map((opt, i) => {
                  const optText = typeof opt === "object" ? opt.text || opt.label || JSON.stringify(opt) : opt;
                  const isSelected = selectedAnswer === optText;
                  return (
                    <button
                      key={i}
                      type="button"
                      onClick={() => handleSelectAnswer(optText)}
                      disabled={loading}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "12px",
                        padding: "16px 20px",
                        border: isSelected ? "1px solid var(--accent-border, var(--cv-accent-border, var(--accent)))" : "1px solid var(--border, var(--cv-rule))",
                        borderRadius: "6px",
                        background: isSelected ? "var(--accent-soft, var(--cv-accent-soft))" : "var(--surface, var(--cv-paper))",
                        color: "var(--text, var(--cv-text))",
                        textAlign: "left",
                        fontSize: "0.9rem",
                        cursor: "pointer",
                        transition: "all 0.15s ease",
                      }}
                    >
                      <Circle size={16} color="var(--accent, var(--cv-accent))" />
                      <span>{optText}</span>
                    </button>
                  );
                })}
              </div>
            )}

            {/* Open-Ended Textarea & Custom Input Support */}
            {(currentQuestion.question_type === "text" || !currentQuestion.options || currentQuestion.options.length === 0 || (currentQuestion.options || []).length <= 4) && (
              <div style={{ marginTop: "20px", paddingTop: (currentQuestion.options && currentQuestion.options.length > 0) ? "16px" : "0", borderTop: (currentQuestion.options && currentQuestion.options.length > 0) ? "1px dashed var(--border, var(--cv-rule))" : "none" }}>
                <label style={{ display: "block", fontSize: "0.82rem", fontWeight: 600, color: "var(--text-muted, var(--cv-muted))", marginBottom: "8px" }}>
                  {currentQuestion.question_type === "text" || !currentQuestion.options || currentQuestion.options.length === 0
                    ? "Write your personal reflection or project highlight:"
                    : "Or elaborate in your own words:"}
                </label>
                <textarea
                  value={customText}
                  onChange={(e) => setCustomText(e.target.value)}
                  placeholder="e.g., In my recent system, I built an end-to-end asynchronous pipeline with real-time feedback and state caching, which taught me how to handle concurrent user interactions..."
                  rows={4}
                  style={{
                    width: "100%",
                    padding: "12px 14px",
                    borderRadius: "6px",
                    border: "1px solid var(--border, var(--cv-rule))",
                    background: "var(--surface, var(--cv-paper))",
                    color: "var(--text, var(--cv-text))",
                    fontSize: "0.9rem",
                    fontFamily: "inherit",
                    lineHeight: 1.5,
                    resize: "vertical",
                    boxSizing: "border-box",
                  }}
                />

                {/* Quick Starters for open-ended prompt */}
                {(!currentQuestion.options || currentQuestion.options.length === 0) && (
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "10px" }}>
                    {[
                      "Full-Stack Web App with real-time state and responsive UI",
                      "Scalable Backend API with async job processing",
                      "AI-assisted system with vector search and agent workflows",
                      "Algorithmic optimization reducing latency and memory usage",
                    ].map((starter, sIdx) => (
                      <button
                        key={sIdx}
                        type="button"
                        onClick={() => setCustomText(starter)}
                        style={{
                          fontSize: "0.78rem",
                          padding: "4px 10px",
                          borderRadius: "14px",
                          border: "1px solid var(--border, var(--cv-rule))",
                          background: "var(--surface-2, var(--cv-card-bg, #f8fafc))",
                          color: "var(--text-muted, var(--cv-muted))",
                          cursor: "pointer",
                        }}
                      >
                        + {starter}
                      </button>
                    ))}
                  </div>
                )}

                <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "14px" }}>
                  <button
                    type="button"
                    className="cv-auth-btn"
                    style={{ width: "auto", padding: "0 24px", height: "42px" }}
                    onClick={() => handleSelectAnswer(customText)}
                    disabled={loading || !customText.trim()}
                  >
                    {loading ? "Recording..." : "Submit Response & Continue →"}
                  </button>
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* ─── PHASE: COMPLETE / RESULTS ───────────────────────────────────── */}
      {phase === "complete" && (
        <section className="cv-editorial-section">
          <div className="cv-section-index">RESULTS</div>
          <div className="cv-section-content">
            <h2 style={{ color: "var(--text, var(--cv-text))", fontSize: "1.45rem", marginTop: "8px", marginBottom: "16px" }}>
              Your Natural Trajectory Profile
            </h2>
            <p style={{ color: "var(--text-muted, var(--cv-text-muted))" }}>Based on your choices, CareerVerse has synthesized your core strengths and alignment:</p>

            <div
              style={{
                border: "1px solid var(--border, var(--cv-rule))",
                borderRadius: "8px",
                padding: "24px",
                background: "var(--surface, var(--cv-paper))",
                marginTop: "20px",
                display: "flex",
                flexDirection: "column",
                gap: "16px",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <Sparkles size={24} color="var(--accent, var(--cv-accent))" />
                <h3 style={{ margin: 0, fontSize: "1.2rem", color: "var(--text, var(--cv-text))" }}>
                  {result?.top_archetype || result?.primary_direction || "System Architect & Problem Solver"}
                </h3>
              </div>
              <p style={{ color: "var(--text-muted, var(--cv-muted))", fontSize: "0.9rem", lineHeight: 1.6, margin: 0 }}>
                {result?.summary || result?.analysis || "You thrive when balancing technical depth with end-to-end architectural autonomy. Consider exploring backend engineering, systems design, and technical leadership roles."}
              </p>
            </div>

            <div style={{ display: "flex", gap: "14px", marginTop: "24px", flexWrap: "wrap" }}>
              <Link to="/career-discovery" className="cv-auth-btn" style={{ width: "auto", padding: "0 20px", height: "44px", textDecoration: "none" }}>
                Explore Options (Chapter 04) <ArrowRight size={14} />
              </Link>
              <button
                type="button"
                onClick={() => { setPhase("start"); setResult(null); }}
                style={{
                  padding: "0 18px",
                  height: "44px",
                  background: "var(--surface, transparent)",
                  border: "1px solid var(--border, var(--cv-rule))",
                  color: "var(--text, var(--cv-text))",
                  borderRadius: "4px",
                  fontSize: "0.82rem",
                  cursor: "pointer",
                }}
              >
                Retake Assessment
              </button>
            </div>
          </div>
        </section>
      )}

      {/* ─── CHAPTER FOOTER ──────────────────────────────────────────────── */}
      <footer className="cv-chapter-footer">
        <Link to="/resume"><ArrowLeft size={12} /> Chapter 02 · Work &amp; Sources</Link>
        <span>03 / 08 · CAREER COMPASS</span>
        <Link to="/career-discovery">Chapter 04 · Your Options <ArrowRight size={12} /></Link>
      </footer>
    </div>
  );
}
