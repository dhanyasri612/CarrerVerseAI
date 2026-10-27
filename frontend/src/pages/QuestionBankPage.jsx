import React, { useState, useEffect, useMemo } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import {
  BookOpen,
  Search,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  RotateCcw,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Clock,
  Award,
  Layers,
  Code2,
  Bookmark,
  RefreshCw,
  ExternalLink,
  ChevronRight,
  Filter,
  Check,
  X,
  Target,
  FileText,
  GitBranch,
} from "lucide-react";
import {
  getInterviewQuestionHistory,
  getInterviewSessionsList,
} from "../services/careerService";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import "./QuestionBankPage.css";

export default function QuestionBankPage() {
  const { user } = useAuth();
  const { theme } = useTheme();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // State
  const [questions, setQuestions] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Active Tab & Filters
  const [activeTab, setActiveTab] = useState(() => searchParams.get("tab") || "all");
  const [searchQuery, setSearchQuery] = useState(() => searchParams.get("q") || "");
  const [difficultyFilter, setDifficultyFilter] = useState("all");
  const [roleFilter, setRoleFilter] = useState("all");
  const [topicFilter, setTopicFilter] = useState("all");
  const [selectedQuestionIdx, setSelectedQuestionIdx] = useState(0);

  // Fetch persisted question history & sessions
  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [histData, sessData] = await Promise.all([
        getInterviewQuestionHistory(),
        getInterviewSessionsList().catch(() => []),
      ]);
      const hist = Array.isArray(histData) ? histData : [];
      const sess = Array.isArray(sessData) ? sessData : [];
      setQuestions(hist);
      setSessions(sess);
    } catch (err) {
      console.error("Failed to load question bank data:", err);
      setError("Unable to load question bank data. Please check connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Update URL search query params
  useEffect(() => {
    const params = new URLSearchParams();
    if (activeTab !== "all") params.set("tab", activeTab);
    if (searchQuery.trim()) params.set("q", searchQuery.trim());
    setSearchParams(params, { replace: true });
  }, [activeTab, searchQuery, setSearchParams]);

  // Metric collections
  const masteredItems = useMemo(
    () => questions.filter((q) => q.mastery_status === "mastered" || (q.score || 0) >= 8),
    [questions]
  );
  const revisionItems = useMemo(
    () =>
      questions.filter(
        (q) =>
          q.mastery_status === "needs_revision" ||
          q.ready_for_retest ||
          ((q.score || 0) > 0 && (q.score || 0) < 7)
      ),
    [questions]
  );
  const easyItems = useMemo(
    () => questions.filter((q) => (q.difficulty || "").toLowerCase() === "easy"),
    [questions]
  );
  const mediumItems = useMemo(
    () => questions.filter((q) => (q.difficulty || "medium").toLowerCase() === "medium"),
    [questions]
  );
  const hardItems = useMemo(
    () => questions.filter((q) => (q.difficulty || "").toLowerCase() === "hard"),
    [questions]
  );

  const progressPct =
    questions.length > 0
      ? Math.round((masteredItems.length / Math.max(questions.length, 1)) * 100)
      : 0;

  // Filtered Questions
  const filteredQuestions = useMemo(() => {
    return questions.filter((item) => {
      // Tab filter
      if (activeTab === "revision" && !revisionItems.includes(item)) return false;
      if (activeTab === "mastered" && !masteredItems.includes(item)) return false;

      // Search Query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const questionText = (item.question || "").toLowerCase();
        const topic = (item.topic || "").toLowerCase();
        const role = (item.target_role || "").toLowerCase();
        const ans = (item.candidate_answer || item.answer_snippet || "").toLowerCase();
        if (!questionText.includes(q) && !topic.includes(q) && !role.includes(q) && !ans.includes(q)) {
          return false;
        }
      }

      // Difficulty Filter
      if (difficultyFilter !== "all") {
        if ((item.difficulty || "medium").toLowerCase() !== difficultyFilter.toLowerCase()) {
          return false;
        }
      }

      // Role Filter
      if (roleFilter !== "all") {
        if (!(item.target_role || "").toLowerCase().includes(roleFilter.toLowerCase())) {
          return false;
        }
      }

      // Topic Filter
      if (topicFilter !== "all") {
        if ((item.topic || "").toLowerCase() !== topicFilter.toLowerCase()) {
          return false;
        }
      }

      return true;
    });
  }, [
    questions,
    activeTab,
    revisionItems,
    masteredItems,
    searchQuery,
    difficultyFilter,
    roleFilter,
    topicFilter,
  ]);

  // Currently active selected question for detail view
  const activeQuestion = filteredQuestions[selectedQuestionIdx] || filteredQuestions[0] || null;

  // Unique topics for topic dropdown
  const uniqueTopics = useMemo(() => {
    const s = new Set();
    questions.forEach((q) => {
      if (q.topic) s.add(q.topic);
    });
    return Array.from(s);
  }, [questions]);

  return (
    <div className="qb-page" data-theme={theme}>
      <div className="qb-container">
        {/* Header & Breadcrumb */}
        <div className="qb-header">
          <div className="qb-breadcrumb">
            <Link to="/dashboard">Dashboard</Link>
            <ChevronRight size={14} />
            <Link to="/ai/interview">Interview</Link>
            <ChevronRight size={14} />
            <span>Question Bank</span>
          </div>

          <div className="qb-title-row">
            <div>
              <h1 className="qb-title">Question Bank &amp; Revision Studio</h1>
              <p className="qb-subtitle">
                Explore real scenario-based questions from your technical interview sessions.
                Review exact submitted answers, multi-dimensional rubric feedback, and spaced
                repetition cooldowns.
              </p>
            </div>

            <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
              <button
                type="button"
                onClick={loadData}
                className="qb-cta-btn"
                style={{ background: "rgba(255, 255, 255, 0.08)", color: "#f8fafc" }}
                title="Refresh Question Bank"
              >
                <RefreshCw size={15} className={loading ? "spin" : ""} />
                <span>Refresh</span>
              </button>
              <Link to="/ai/interview" className="qb-cta-btn">
                <Target size={16} />
                <span>Practice Live Interview</span>
              </Link>
            </div>
          </div>
        </div>

        {/* 4 Stat Cards */}
        <div className="qb-stats-grid">
          <div className="qb-stat-card">
            <div className="qb-stat-header">
              <span className="qb-stat-label">Total Mastery Progress</span>
              <Award size={18} color="#818cf8" />
            </div>
            <div className="qb-stat-value">
              {progressPct}% <span className="qb-stat-total">({masteredItems.length}/{Math.max(questions.length, 1)})</span>
            </div>
            <div className="qb-progress-track">
              <div
                className="qb-progress-bar"
                style={{ width: `${progressPct}%`, background: "#6366f1" }}
              />
            </div>
          </div>

          <div className="qb-stat-card">
            <div className="qb-stat-header">
              <span className="qb-stat-label">Easy Problems</span>
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#22c55e" }} />
            </div>
            <div className="qb-stat-value">
              {easyItems.length} <span className="qb-stat-total">questions</span>
            </div>
            <div className="qb-progress-track">
              <div
                className="qb-progress-bar"
                style={{
                  width: `${questions.length ? (easyItems.length / questions.length) * 100 : 0}%`,
                  background: "#22c55e",
                }}
              />
            </div>
          </div>

          <div className="qb-stat-card">
            <div className="qb-stat-header">
              <span className="qb-stat-label">Medium Problems</span>
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#f59e0b" }} />
            </div>
            <div className="qb-stat-value">
              {mediumItems.length} <span className="qb-stat-total">questions</span>
            </div>
            <div className="qb-progress-track">
              <div
                className="qb-progress-bar"
                style={{
                  width: `${questions.length ? (mediumItems.length / questions.length) * 100 : 0}%`,
                  background: "#f59e0b",
                }}
              />
            </div>
          </div>

          <div className="qb-stat-card">
            <div className="qb-stat-header">
              <span className="qb-stat-label">Hard Problems</span>
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#ef4444" }} />
            </div>
            <div className="qb-stat-value">
              {hardItems.length} <span className="qb-stat-total">questions</span>
            </div>
            <div className="qb-progress-track">
              <div
                className="qb-progress-bar"
                style={{
                  width: `${questions.length ? (hardItems.length / questions.length) * 100 : 0}%`,
                  background: "#ef4444",
                }}
              />
            </div>
          </div>
        </div>

        {/* Filter & Search Bar */}
        <div className="qb-controls-section">
          <div className="qb-tabs-row">
            {[
              { id: "all", label: `All Questions (${questions.length})` },
              { id: "sessions", label: `Past Sessions (${sessions.length})` },
              { id: "revision", label: `Revision Needed (${revisionItems.length})` },
              { id: "mastered", label: `Mastered (${masteredItems.length})` },
            ].map((tab) => (
              <button
                key={tab.id}
                type="button"
                className={`qb-tab-btn ${activeTab === tab.id ? "active" : ""}`}
                onClick={() => {
                  setActiveTab(tab.id);
                  setSelectedQuestionIdx(0);
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="qb-filters-grid">
            <div className="qb-search-box">
              <Search size={16} color="#94a3b8" />
              <input
                type="text"
                className="qb-search-input"
                placeholder="Search by question title, concept, or answer..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  style={{ background: "none", border: "none", color: "#94a3b8", cursor: "pointer" }}
                >
                  <X size={14} />
                </button>
              )}
            </div>

            <select
              className="qb-select"
              value={difficultyFilter}
              onChange={(e) => setDifficultyFilter(e.target.value)}
            >
              <option value="all">All Difficulties</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>

            <select
              className="qb-select"
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
            >
              <option value="all">All Roles</option>
              <option value="Backend">Backend Systems</option>
              <option value="Frontend">Frontend / React</option>
              <option value="Full Stack">Full Stack</option>
              <option value="Machine Learning">AI / Machine Learning</option>
              <option value="Cloud">Cloud &amp; DevOps</option>
            </select>

            <select
              className="qb-select"
              value={topicFilter}
              onChange={(e) => setTopicFilter(e.target.value)}
            >
              <option value="all">All Topics</option>
              {uniqueTopics.map((topic) => (
                <option key={topic} value={topic.toLowerCase()}>
                  {topic}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Content Body: Sessions Tab OR Questions Main Layout */}
        {loading ? (
          <div className="qb-empty-state">
            <RefreshCw size={28} className="spin" style={{ marginBottom: "1rem" }} />
            <div className="qb-empty-title">Loading Question Bank...</div>
            <div className="qb-empty-desc">Fetching verified interview questions and attempt history.</div>
          </div>
        ) : error ? (
          <div className="qb-empty-state" style={{ borderColor: "#ef4444" }}>
            <AlertCircle size={32} color="#ef4444" style={{ marginBottom: "0.75rem" }} />
            <div className="qb-empty-title" style={{ color: "#f87171" }}>
              Unable to Load Questions
            </div>
            <div className="qb-empty-desc">{error}</div>
            <button type="button" onClick={loadData} className="qb-cta-btn">
              Try Again
            </button>
          </div>
        ) : activeTab === "sessions" ? (
          /* Past Sessions Tab */
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {sessions.length === 0 ? (
              <div className="qb-empty-state">
                <div className="qb-empty-icon">🎙️</div>
                <div className="qb-empty-title">No Past Interview Sessions Found</div>
                <div className="qb-empty-desc">
                  Start an interview session to generate and persist interview dossiers.
                </div>
                <Link to="/ai/interview" className="qb-cta-btn">
                  Start an Interview
                </Link>
              </div>
            ) : (
              sessions.map((sess) => {
                const isDone = sess.status === "completed";
                const dateStr = sess.created_at
                  ? new Date(sess.created_at).toLocaleDateString(undefined, {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })
                  : "Recent";

                return (
                  <div
                    key={sess.session_id}
                    className="qb-card"
                    style={{ cursor: "default" }}
                  >
                    <div className="qb-card-top">
                      <div className="qb-badge-group">
                        <span
                          className="qb-badge"
                          style={{
                            background: isDone ? "rgba(34, 197, 94, 0.18)" : "rgba(99, 102, 241, 0.18)",
                            color: isDone ? "#4ade80" : "#a5b4fc",
                            border: `1px solid ${isDone ? "rgba(34, 197, 94, 0.3)" : "rgba(99, 102, 241, 0.3)"}`,
                          }}
                        >
                          {isDone ? "✓ Completed" : "● In Progress"}
                        </span>
                        <span className="qb-badge qb-badge-role">
                          Mode: {sess.interview_mode || "General"}
                        </span>
                      </div>
                      {sess.overall_score && (
                        <span className="qb-card-score">Score: {sess.overall_score}/10</span>
                      )}
                    </div>

                    <h3 className="qb-card-title">{sess.target_role || "Software Engineer"}</h3>
                    {sess.answers_summary && (
                      <p className="qb-card-snippet">"{sess.answers_summary}"</p>
                    )}

                    <div className="qb-card-meta">
                      <span>{dateStr}</span>
                      <span>{sess.question_count || 1} Turn{(sess.question_count || 1) > 1 ? "s" : ""}</span>
                      <Link
                        to={`/ai/interview?session_id=${sess.session_id}`}
                        style={{
                          color: "#818cf8",
                          fontWeight: 700,
                          textDecoration: "none",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "0.25rem",
                        }}
                      >
                        Inspect Dossier <ArrowRight size={14} />
                      </Link>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        ) : filteredQuestions.length === 0 ? (
          /* Empty Questions State */
          <div className="qb-empty-state">
            <div className="qb-empty-icon">🎯</div>
            <div className="qb-empty-title">No Questions Matched Your Filters</div>
            <div className="qb-empty-desc">
              Try adjusting your search query, difficulty, or role filters.
            </div>
            <button
              type="button"
              onClick={() => {
                setSearchQuery("");
                setDifficultyFilter("all");
                setRoleFilter("all");
                setTopicFilter("all");
              }}
              className="qb-cta-btn"
              style={{ background: "rgba(255, 255, 255, 0.08)" }}
            >
              Reset Filters
            </button>
          </div>
        ) : (
          /* Main 2-Column Layout: Questions List + Detail Panel */
          <div className="qb-main-layout">
            {/* Left Column: Questions List */}
            <div className="qb-list-col">
              {filteredQuestions.map((item, idx) => {
                const isSelected = activeQuestion === item;
                const diff = (item.difficulty || "medium").toLowerCase();
                const isMastered = item.mastery_status === "mastered" || (item.score || 0) >= 8;
                const isRevision = item.mastery_status === "needs_revision" || item.ready_for_retest;

                return (
                  <div
                    key={idx}
                    className={`qb-card ${isSelected ? "selected" : ""}`}
                    onClick={() => setSelectedQuestionIdx(idx)}
                  >
                    <div className="qb-card-top">
                      <div className="qb-badge-group">
                        <span
                          className={`qb-badge ${
                            diff === "easy"
                              ? "qb-badge-easy"
                              : diff === "hard"
                              ? "qb-badge-hard"
                              : "qb-badge-medium"
                          }`}
                        >
                          {diff.charAt(0).toUpperCase() + diff.slice(1)}
                        </span>
                        <span className="qb-badge qb-badge-role">
                          {item.topic || "Technical Assessment"}
                        </span>
                        {isMastered && (
                          <span className="qb-badge qb-badge-mastered">
                            <CheckCircle2 size={12} /> Mastered
                          </span>
                        )}
                        {isRevision && (
                          <span className="qb-badge qb-badge-revision">
                            <Bookmark size={12} /> Needs Revision
                          </span>
                        )}
                      </div>

                      {item.score !== undefined && item.score !== null && (
                        <span className="qb-card-score">{item.score}/10</span>
                      )}
                    </div>

                    <h3 className="qb-card-title">
                      {item.question ? item.question.split(/[\n.?]/)[0] : "Scenario Assessment"}
                    </h3>

                    <p className="qb-card-snippet">{item.question}</p>

                    <div className="qb-card-meta">
                      <span>Role: {item.target_role || "Engineering"}</span>
                      <span>
                        {item.ready_for_retest
                          ? "🎯 Ready for re-test"
                          : `⏳ ${item.days_until_retest || 30}d cooldown`}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Right Column: 8-Section Structured Question Detail View */}
            {activeQuestion && (
              <div className="qb-detail-panel">
                <div className="qb-detail-header">
                  <div className="qb-badge-group">
                    <span
                      className={`qb-badge ${
                        (activeQuestion.difficulty || "medium").toLowerCase() === "easy"
                          ? "qb-badge-easy"
                          : (activeQuestion.difficulty || "medium").toLowerCase() === "hard"
                          ? "qb-badge-hard"
                          : "qb-badge-medium"
                      }`}
                    >
                      {(activeQuestion.difficulty || "medium").toUpperCase()}
                    </span>
                    <span className="qb-badge qb-badge-role">
                      {activeQuestion.target_role || "General"}
                    </span>
                    <span className="qb-badge qb-badge-role">
                      Topic: {activeQuestion.topic || "Architecture"}
                    </span>
                  </div>

                  <h2 className="qb-detail-title">
                    {activeQuestion.question.split(/[\n.?]/)[0] || "Question Breakdown"}
                  </h2>
                </div>

                {/* 1. Original Question */}
                <div className="qb-section">
                  <div className="qb-section-header">
                    <BookOpen size={16} />
                    <span>1. Original Question</span>
                  </div>
                  <div className="qb-section-content">
                    <p style={{ margin: "0 0 0.5rem" }}>{activeQuestion.question}</p>
                    {activeQuestion.constraints && activeQuestion.constraints.length > 0 && (
                      <div style={{ marginTop: "0.5rem", fontSize: "0.82rem", color: "#94a3b8" }}>
                        <strong style={{ color: "#e2e8f0" }}>Constraints:</strong>
                        <ul style={{ margin: "0.25rem 0 0", paddingLeft: "1.2rem" }}>
                          {activeQuestion.constraints.map((c, i) => (
                            <li key={i}>{c}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {activeQuestion.repository_citations &&
                      activeQuestion.repository_citations.length > 0 && (
                        <div style={{ marginTop: "0.5rem", fontSize: "0.82rem", color: "#818cf8" }}>
                          <strong>Verified Citations:</strong>{" "}
                          {activeQuestion.repository_citations.join(", ")}
                        </div>
                      )}
                  </div>
                </div>

                {/* 2. Candidate Answer */}
                <div className="qb-section">
                  <div className="qb-section-header">
                    <FileText size={16} />
                    <span>2. Candidate's Exact Submitted Answer</span>
                  </div>
                  <div className="qb-section-content">
                    {activeQuestion.candidate_answer || activeQuestion.answer_snippet ? (
                      <blockquote
                        style={{
                          margin: 0,
                          padding: "0.75rem 1rem",
                          borderLeft: "3px solid #6366f1",
                          background: "rgba(15, 23, 42, 0.6)",
                          borderRadius: "0 8px 8px 0",
                          fontStyle: "italic",
                        }}
                      >
                        "{activeQuestion.candidate_answer || activeQuestion.answer_snippet}"
                      </blockquote>
                    ) : (
                      <span style={{ color: "#64748b" }}>No candidate answer recorded for this turn.</span>
                    )}
                  </div>
                </div>

                {/* 3. AI Evaluation & Rubric Scores */}
                <div className="qb-section">
                  <div className="qb-section-header">
                    <Award size={16} />
                    <span>3. AI Evaluation &amp; Calibrated Rubric</span>
                  </div>
                  <div className="qb-section-content">
                    <p style={{ margin: "0 0 0.5rem" }}>
                      {activeQuestion.evaluation_summary ||
                        "Candidate's response was evaluated against the active technical constraints."}
                    </p>

                    {activeQuestion.rubric_scores &&
                      typeof activeQuestion.rubric_scores === "object" && (
                        <div className="qb-rubric-grid">
                          {Object.entries(activeQuestion.rubric_scores).map(([dim, score]) => (
                            <div key={dim} className="qb-rubric-box">
                              <div className="qb-rubric-label">{dim.replace(/_/g, " ")}</div>
                              <div className="qb-rubric-score">{score}/10</div>
                            </div>
                          ))}
                        </div>
                      )}
                  </div>
                </div>

                {/* 4. What Was Correct (Strengths) */}
                <div className="qb-section">
                  <div className="qb-section-header" style={{ color: "#4ade80" }}>
                    <CheckCircle2 size={16} />
                    <span>4. What Was Correct (Strengths)</span>
                  </div>
                  <div className="qb-section-content">
                    {activeQuestion.strengths && activeQuestion.strengths.length > 0 ? (
                      <ul className="qb-item-list">
                        {activeQuestion.strengths.map((str, i) => (
                          <li key={i}>{str}</li>
                        ))}
                      </ul>
                    ) : (
                      <span style={{ color: "#64748b" }}>Demonstrated initial context.</span>
                    )}
                  </div>
                </div>

                {/* 5. What Was Missing or Incorrect */}
                <div className="qb-section">
                  <div className="qb-section-header" style={{ color: "#f87171" }}>
                    <AlertCircle size={16} />
                    <span>5. Missing Elements &amp; Growth Areas</span>
                  </div>
                  <div className="qb-section-content">
                    {activeQuestion.missing_elements && activeQuestion.missing_elements.length > 0 ? (
                      <ul className="qb-item-list">
                        {activeQuestion.missing_elements.map((m, i) => (
                          <li key={i} style={{ color: "#fca5a5" }}>
                            {m}
                          </li>
                        ))}
                      </ul>
                    ) : activeQuestion.improvements && activeQuestion.improvements.length > 0 ? (
                      <ul className="qb-item-list">
                        {activeQuestion.improvements.map((imp, i) => (
                          <li key={i}>{imp}</li>
                        ))}
                      </ul>
                    ) : (
                      <span style={{ color: "#64748b" }}>No critical technical omissions noted.</span>
                    )}
                  </div>
                </div>

                {/* 6. Suggested Improved Answer */}
                <div className="qb-section">
                  <div className="qb-section-header" style={{ color: "#fbbf24" }}>
                    <Sparkles size={16} />
                    <span>6. Suggested Model Pitch / Architecture Script</span>
                  </div>
                  <div className="qb-section-content">
                    {activeQuestion.ideal_pitch_script ? (
                      <div
                        style={{
                          background: "rgba(15, 23, 42, 0.7)",
                          padding: "0.85rem 1.1rem",
                          borderRadius: "8px",
                          border: "1px solid rgba(251, 191, 36, 0.2)",
                          color: "#fef3c7",
                          lineHeight: 1.6,
                        }}
                      >
                        {activeQuestion.ideal_pitch_script}
                      </div>
                    ) : activeQuestion.how_to_explain ? (
                      <div style={{ color: "#cbd5e1" }}>{activeQuestion.how_to_explain}</div>
                    ) : (
                      <span style={{ color: "#64748b" }}>
                        Structure your response by defining constraints first, proposing your core
                        architecture, and stating computational trade-offs.
                      </span>
                    )}
                  </div>
                </div>

                {/* 7. Follow-Up Discussion */}
                <div className="qb-section">
                  <div className="qb-section-header">
                    <Layers size={16} />
                    <span>7. Follow-Up Probing &amp; Discussion</span>
                  </div>
                  <div className="qb-section-content">
                    {activeQuestion.follow_ups && activeQuestion.follow_ups.length > 0 ? (
                      <ul className="qb-item-list">
                        {activeQuestion.follow_ups.map((fu, i) => (
                          <li key={i}>
                            <strong>Follow-up {i + 1}:</strong> {typeof fu === "string" ? fu : fu.question}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <span style={{ color: "#64748b" }}>
                        Probe deeper into distributed scalability, failure modes, and edge cases.
                      </span>
                    )}
                  </div>
                </div>

                {/* 8. Previous Attempts & Revision Actions */}
                <div className="qb-section" style={{ border: "1px solid rgba(99, 102, 241, 0.3)" }}>
                  <div className="qb-section-header">
                    <RotateCcw size={16} />
                    <span>8. Attempt History &amp; Revision Actions</span>
                  </div>
                  <div className="qb-section-content">
                    <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "0.75rem", alignItems: "center" }}>
                      <div>
                        <div style={{ fontSize: "0.85rem", color: "#f8fafc", fontWeight: 700 }}>
                          {activeQuestion.ready_for_retest
                            ? "✅ 30-Day Cooldown Elapsed: Ready for Retest"
                            : `⏳ 30-Day Anti-Repetition Active (${activeQuestion.days_until_retest || 30} days left)`}
                        </div>
                        <div style={{ fontSize: "0.76rem", color: "#94a3b8", marginTop: "0.2rem" }}>
                          Last attempted: {activeQuestion.days_ago || 0} day(s) ago
                        </div>
                      </div>

                      <Link
                        to={`/ai/interview?mode=targeted_revision&topic=${encodeURIComponent(
                          activeQuestion.topic || ""
                        )}`}
                        className="qb-cta-btn"
                        style={{ padding: "0.55rem 1rem", fontSize: "0.82rem" }}
                      >
                        <Target size={14} />
                        <span>Practice This Question</span>
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
