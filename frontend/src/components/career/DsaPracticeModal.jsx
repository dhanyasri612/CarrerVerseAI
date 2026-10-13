import React, { useState, useEffect } from "react";
import {
  X,
  Code2,
  GitBranch,
  Flame,
  Award,
  ChevronRight,
  ChevronDown,
  CheckCircle2,
  Sparkles,
  ExternalLink,
  BookOpen,
  HelpCircle,
  Copy,
  Check,
  Zap,
  Layers,
  Compass,
  AlertTriangle,
} from "lucide-react";
import { getDsaRecommendations } from "../../services/careerService";
import { recordActivity } from "../../services/activityTracker";

export default function DsaPracticeModal({ onClose, targetRole = "Software Developer" }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("topics"); // "topics" | "roadmap" | "problems"
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [revealedHints, setRevealedHints] = useState({});
  const [solvedProblems, setSolvedProblems] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("cv_solved_dsa_problems") || "[]");
    } catch {
      return [];
    }
  });

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getDsaRecommendations(targetRole)
      .then((res) => {
        if (!cancelled) {
          setData(res);
          if (res.recommended_problems && res.recommended_problems.length > 0) {
            setSelectedProblem(res.recommended_problems[0]);
          }
        }
      })
      .catch((err) => {
        if (!cancelled) setError("Could not load DSA recommendations.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [targetRole]);

  const toggleSolved = (prob) => {
    const isSolved = solvedProblems.includes(prob.id);
    let updated;
    if (isSolved) {
      updated = solvedProblems.filter((id) => id !== prob.id);
    } else {
      updated = [...solvedProblems, prob.id];
      recordActivity({
        type: "dsa",
        title: `Practiced DSA: ${prob.title}`,
        detail: `${prob.difficulty} (${prob.topic}) — Solved pattern similar to ${prob.similar_to || "LeetCode"}`,
        score: prob.difficulty === "Hard" ? 3 : prob.difficulty === "Medium" ? 2 : 1,
      });
    }
    setSolvedProblems(updated);
    localStorage.setItem("cv_solved_dsa_problems", JSON.stringify(updated));
  };

  const toggleHint = (index) => {
    setRevealedHints((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  const lcStats = data?.current_stats?.leetcode || {};
  const isLcConnected = data?.connected_platforms?.leetcode;
  const practicedTopics = data?.practiced_topics || [];
  const toPracticeTopics = data?.to_practice_topics || [];

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        background: "rgba(15, 23, 42, 0.82)",
        backdropFilter: "blur(8px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "1.5rem",
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: "#ffffff",
          width: "100%",
          maxWidth: "1120px",
          height: "92vh",
          maxHeight: "880px",
          borderRadius: "20px",
          boxShadow: "0 25px 60px -15px rgba(0,0,0,0.4)",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          border: "1px solid #334155",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          style={{
            padding: "1.25rem 2rem",
            background: "#0f172a",
            color: "#ffffff",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            borderBottom: "1px solid #1e293b",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: "12px",
                background: "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#0f172a",
                boxShadow: "0 4px 12px rgba(245, 158, 11, 0.3)",
              }}
            >
              <Code2 size={24} />
            </div>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span
                  style={{
                    fontSize: "0.75rem",
                    fontWeight: 700,
                    letterSpacing: "0.08em",
                    color: "#fbbf24",
                    textTransform: "uppercase",
                  }}
                >
                  Daily Problem Solving • Adaptive DSA Engine
                </span>
                {isLcConnected && (
                  <span
                    style={{
                      fontSize: "0.7rem",
                      background: "rgba(34, 197, 94, 0.2)",
                      color: "#4ade80",
                      padding: "2px 8px",
                      borderRadius: "6px",
                      fontWeight: 600,
                    }}
                  >
                    LeetCode Connected
                  </span>
                )}
              </div>
              <h2 style={{ margin: "2px 0 0 0", fontSize: "1.35rem", fontWeight: 700, color: "#f8fafc" }}>
                DSA Mastery, Topic Separation & Performance Roadmap
              </h2>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div style={{ display: "flex", background: "#1e293b", borderRadius: "10px", padding: "4px", gap: "4px" }}>
              <button
                type="button"
                onClick={() => setActiveTab("topics")}
                style={{
                  padding: "7px 14px",
                  borderRadius: "7px",
                  border: "none",
                  background: activeTab === "topics" ? "#fbbf24" : "transparent",
                  color: activeTab === "topics" ? "#0f172a" : "#94a3b8",
                  fontWeight: 600,
                  fontSize: "0.82rem",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                <Layers size={14} /> Topic Separation ({practicedTopics.length} Practiced)
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("roadmap")}
                style={{
                  padding: "7px 14px",
                  borderRadius: "7px",
                  border: "none",
                  background: activeTab === "roadmap" ? "#fbbf24" : "transparent",
                  color: activeTab === "roadmap" ? "#0f172a" : "#94a3b8",
                  fontWeight: 600,
                  fontSize: "0.82rem",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                <Compass size={14} /> Performance Roadmap
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("problems")}
                style={{
                  padding: "7px 14px",
                  borderRadius: "7px",
                  border: "none",
                  background: activeTab === "problems" ? "#fbbf24" : "transparent",
                  color: activeTab === "problems" ? "#0f172a" : "#94a3b8",
                  fontWeight: 600,
                  fontSize: "0.82rem",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                <Zap size={14} /> Practice Problems ({data?.recommended_problems?.length || 4})
              </button>
            </div>

            <button
              type="button"
              onClick={onClose}
              style={{
                width: 34,
                height: 34,
                borderRadius: "8px",
                border: "none",
                background: "#334155",
                color: "#e2e8f0",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
              }}
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Diagnostic Assessment Banner */}
        <div
          style={{
            background: "#1e293b",
            padding: "0.85rem 2rem",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            borderBottom: "1px solid #334155",
            color: "#e2e8f0",
            fontSize: "0.84rem",
            flexWrap: "wrap",
            gap: "1rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "16px", flexWrap: "wrap" }}>
            <div
              style={{
                background: "rgba(245, 158, 11, 0.15)",
                border: "1px solid rgba(245, 158, 11, 0.35)",
                borderRadius: "8px",
                padding: "3px 10px",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <Award size={15} color="#fbbf24" />
              <span style={{ color: "#fbbf24", fontWeight: 700 }}>
                Readiness: {data?.overall_readiness_score || 65}%
              </span>
            </div>

            <span>
              <strong>Total Solved:</strong>{" "}
              <span style={{ color: "#fbbf24", fontWeight: 700 }}>{lcStats.total_solved || 0}</span>
            </span>
            <span>
              <strong>Easy:</strong> <span style={{ color: "#4ade80" }}>{lcStats.easy_solved || 0}</span>
            </span>
            <span>
              <strong>Medium:</strong> <span style={{ color: "#facc15" }}>{lcStats.medium_solved || 0}</span>
            </span>
            <span>
              <strong>Hard:</strong> <span style={{ color: "#f87171" }}>{lcStats.hard_solved || 0}</span>
            </span>
            <span>
              <strong>Daily Solved in App:</strong>{" "}
              <span style={{ color: "#38bdf8", fontWeight: 700 }}>{solvedProblems.length}</span>
            </span>
          </div>

          <div
            style={{
              color: "#94a3b8",
              fontSize: "0.8rem",
              background: "#0f172a",
              padding: "4px 12px",
              borderRadius: "6px",
              border: "1px solid #334155",
              maxWidth: "480px",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            <strong>Assessment:</strong> {data?.readiness_verdict || data?.standing_summary}
          </div>
        </div>

        {/* Content Area */}
        <div style={{ flex: 1, overflow: "hidden", display: "flex", background: "#f8fafc" }}>
          {loading ? (
            <div style={{ margin: "auto", textAlign: "center", color: "#64748b" }}>
              <Sparkles
                size={32}
                color="#f59e0b"
                style={{ animation: "spin 2s linear infinite", marginBottom: "10px" }}
              />
              <div style={{ fontWeight: 600, fontSize: "1rem", color: "#0f172a" }}>
                Analyzing Daily Practice & Evaluating Algorithmic Mastery...
              </div>
              <div style={{ fontSize: "0.85rem", color: "#64748b", marginTop: "4px" }}>
                Loading verified resources, topic breakdown, and adaptive milestones
              </div>
            </div>
          ) : activeTab === "topics" ? (
            /* TAB 1: TOPIC SEPARATION & MASTERY ASSESSMENT */
            <div style={{ flex: 1, overflowY: "auto", padding: "1.75rem 2rem" }}>
              <div style={{ maxWidth: 1040, margin: "0 auto", display: "flex", flexDirection: "column", gap: "1.75rem" }}>
                
                {/* Introduction Banner */}
                <div
                  style={{
                    background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
                    padding: "1.25rem 1.5rem",
                    borderRadius: "14px",
                    color: "#ffffff",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    border: "1px solid #334155",
                  }}
                >
                  <div>
                    <h3 style={{ margin: "0 0 6px 0", fontSize: "1.1rem", color: "#f8fafc", fontWeight: 700 }}>
                      Algorithmic Practice Diagnostic • {targetRole}
                    </h3>
                    <p style={{ margin: 0, fontSize: "0.86rem", color: "#94a3b8", lineHeight: 1.5 }}>
                      We categorize your algorithmic skills into <strong>Already Practiced Topics</strong> (with a verified
                      check if you are &ldquo;Good Enough&rdquo; for technical phone screens) and <strong>Priority Topics Needing Practice</strong>.
                    </p>
                  </div>
                  <div style={{ textAlign: "right", minWidth: "160px" }}>
                    <div style={{ fontSize: "0.75rem", color: "#94a3b8" }}>CURRENT BENCHMARK</div>
                    <div style={{ fontSize: "1.3rem", fontWeight: 800, color: "#fbbf24" }}>
                      {practicedTopics.filter((t) => t.is_good_enough).length} / {practicedTopics.length + toPracticeTopics.length} Good Enough
                    </div>
                  </div>
                </div>

                {/* Section 1: ALREADY PRACTICED TOPICS */}
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
                    <div
                      style={{
                        width: 24,
                        height: 24,
                        borderRadius: "50%",
                        background: "#dcfce7",
                        color: "#16a34a",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "0.85rem",
                        fontWeight: 800,
                      }}
                    >
                      ✓
                    </div>
                    <h3 style={{ margin: 0, fontSize: "1.05rem", color: "#0f172a", fontWeight: 700 }}>
                      Already Practiced Topics ({practicedTopics.length})
                    </h3>
                    <span style={{ fontSize: "0.78rem", color: "#64748b" }}>
                      • Evaluated for technical interview readiness
                    </span>
                  </div>

                  {practicedTopics.length === 0 ? (
                    <div
                      style={{
                        padding: "1.5rem",
                        background: "#ffffff",
                        borderRadius: "12px",
                        border: "1px dashed #cbd5e1",
                        textAlign: "center",
                        color: "#64748b",
                        fontSize: "0.88rem",
                      }}
                    >
                      No practiced topics recorded yet. Connect LeetCode or solve daily problems in the &ldquo;Practice Problems&rdquo; tab to establish your baseline!
                    </div>
                  ) : (
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(490px, 1fr))", gap: "1rem" }}>
                      {practicedTopics.map((topic, i) => (
                        <div
                          key={i}
                          style={{
                            background: "#ffffff",
                            borderRadius: "14px",
                            border: topic.is_good_enough ? "1.5px solid #86efac" : "1px solid #e2e8f0",
                            padding: "1.25rem 1.4rem",
                            boxShadow: "0 2px 6px rgba(0,0,0,0.04)",
                            display: "flex",
                            flexDirection: "column",
                            gap: "10px",
                          }}
                        >
                          {/* Card Top */}
                          <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
                            <div>
                              <div style={{ fontSize: "1rem", fontWeight: 700, color: "#0f172a" }}>
                                {topic.topic}
                              </div>
                              <div style={{ fontSize: "0.78rem", color: "#64748b" }}>
                                {topic.solved_count} / {topic.target_count} target problems solved
                              </div>
                            </div>

                            {/* "Good Enough" Badge */}
                            <span
                              style={{
                                display: "inline-flex",
                                alignItems: "center",
                                gap: "4px",
                                fontSize: "0.75rem",
                                fontWeight: 700,
                                padding: "4px 10px",
                                borderRadius: "20px",
                                background: topic.is_good_enough ? "#dcfce7" : "#fef3c7",
                                color: topic.is_good_enough ? "#15803d" : "#b45309",
                                border: topic.is_good_enough ? "1px solid #bbf7d0" : "1px solid #fde68a",
                              }}
                            >
                              {topic.is_good_enough ? (
                                <>
                                  <CheckCircle2 size={13} /> Good Enough
                                </>
                              ) : (
                                <>
                                  <Flame size={13} /> Developing ({topic.mastery_level})
                                </>
                              )}
                            </span>
                          </div>

                          {/* Progress Bar */}
                          <div>
                            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.74rem", color: "#64748b", marginBottom: "4px" }}>
                              <span>Topic Mastery</span>
                              <span style={{ fontWeight: 700, color: topic.is_good_enough ? "#16a34a" : "#d97706" }}>
                                {topic.score_percent}%
                              </span>
                            </div>
                            <div style={{ height: "6px", background: "#f1f5f9", borderRadius: "3px", overflow: "hidden" }}>
                              <div
                                style={{
                                  height: "100%",
                                  width: `${topic.score_percent}%`,
                                  background: topic.is_good_enough ? "#22c55e" : "#f59e0b",
                                  borderRadius: "3px",
                                }}
                              />
                            </div>
                          </div>

                          {/* Assessment Verdict */}
                          <div
                            style={{
                              background: "#f8fafc",
                              padding: "8px 12px",
                              borderRadius: "8px",
                              fontSize: "0.82rem",
                              color: "#334155",
                              lineHeight: 1.45,
                              borderLeft: topic.is_good_enough ? "3px solid #22c55e" : "3px solid #f59e0b",
                            }}
                          >
                            <strong>Verdict:</strong> {topic.assessment_verdict}
                          </div>

                          {/* Curated Resources */}
                          {topic.resources && topic.resources.length > 0 && (
                            <div style={{ marginTop: "4px" }}>
                              <div style={{ fontSize: "0.74rem", fontWeight: 700, color: "#64748b", textTransform: "uppercase", marginBottom: "6px", display: "flex", alignItems: "center", gap: "4px" }}>
                                <BookOpen size={12} /> Curated Resources & Guides
                              </div>
                              <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                                {topic.resources.slice(0, 2).map((res, ri) => (
                                  <a
                                    key={ri}
                                    href={res.url}
                                    target="_blank"
                                    rel="noreferrer"
                                    style={{
                                      display: "flex",
                                      alignItems: "center",
                                      justifyContent: "space-between",
                                      fontSize: "0.78rem",
                                      color: "#2563eb",
                                      textDecoration: "none",
                                      background: "#f1f5f9",
                                      padding: "5px 10px",
                                      borderRadius: "6px",
                                    }}
                                  >
                                    <span style={{ fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                                      {res.title}
                                    </span>
                                    <span style={{ display: "inline-flex", alignItems: "center", gap: "2px", fontSize: "0.72rem", color: "#64748b", flexShrink: 0 }}>
                                      {res.resource_type} <ExternalLink size={11} />
                                    </span>
                                  </a>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Section 2: TOPICS NEEDING PRACTICE */}
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
                    <div
                      style={{
                        width: 24,
                        height: 24,
                        borderRadius: "50%",
                        background: "#fee2e2",
                        color: "#ef4444",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "0.85rem",
                        fontWeight: 800,
                      }}
                    >
                      !
                    </div>
                    <h3 style={{ margin: 0, fontSize: "1.05rem", color: "#0f172a", fontWeight: 700 }}>
                      Topics Needing Practice ({toPracticeTopics.length})
                    </h3>
                    <span style={{ fontSize: "0.78rem", color: "#64748b" }}>
                      • High frequency in {targetRole} interviews
                    </span>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(490px, 1fr))", gap: "1rem" }}>
                    {toPracticeTopics.map((topic, i) => (
                      <div
                        key={i}
                        style={{
                          background: "#ffffff",
                          borderRadius: "14px",
                          border: "1px solid #fed7aa",
                          padding: "1.25rem 1.4rem",
                          boxShadow: "0 2px 6px rgba(0,0,0,0.03)",
                          display: "flex",
                          flexDirection: "column",
                          gap: "10px",
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
                          <div>
                            <div style={{ fontSize: "1rem", fontWeight: 700, color: "#0f172a" }}>
                              {topic.topic}
                            </div>
                            <div style={{ fontSize: "0.78rem", color: "#b45309", fontWeight: 500 }}>
                              Status: {topic.mastery_level} • Target: {topic.target_count} problems
                            </div>
                          </div>

                          <span
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "4px",
                              fontSize: "0.72rem",
                              fontWeight: 700,
                              padding: "3px 9px",
                              borderRadius: "14px",
                              background: "#fee2e2",
                              color: "#dc2626",
                            }}
                          >
                            <AlertTriangle size={12} /> Priority Need
                          </span>
                        </div>

                        {/* Recommendation */}
                        <div
                          style={{
                            background: "#fffbeb",
                            padding: "8px 12px",
                            borderRadius: "8px",
                            fontSize: "0.82rem",
                            color: "#92400e",
                            lineHeight: 1.45,
                            borderLeft: "3px solid #f59e0b",
                          }}
                        >
                          <strong>Action Plan:</strong> {topic.recommended_action}
                        </div>

                        {/* Verified Resources for This Priority Topic */}
                        {topic.resources && topic.resources.length > 0 && (
                          <div>
                            <div style={{ fontSize: "0.74rem", fontWeight: 700, color: "#64748b", textTransform: "uppercase", marginBottom: "6px", display: "flex", alignItems: "center", gap: "4px" }}>
                              <BookOpen size={12} /> Master This Pattern:
                            </div>
                            <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                              {topic.resources.map((res, ri) => (
                                <a
                                  key={ri}
                                  href={res.url}
                                  target="_blank"
                                  rel="noreferrer"
                                  style={{
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "space-between",
                                    fontSize: "0.78rem",
                                    color: "#2563eb",
                                    textDecoration: "none",
                                    background: "#f8fafc",
                                    border: "1px solid #e2e8f0",
                                    padding: "6px 10px",
                                    borderRadius: "6px",
                                  }}
                                >
                                  <div>
                                    <div style={{ fontWeight: 600, color: "#1e293b" }}>{res.title}</div>
                                    <div style={{ fontSize: "0.72rem", color: "#64748b" }}>{res.summary}</div>
                                  </div>
                                  <ExternalLink size={13} color="#2563eb" style={{ flexShrink: 0, marginLeft: "8px" }} />
                                </a>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : activeTab === "roadmap" ? (
            /* TAB 2: PERFORMANCE-ADAPTIVE ROADMAP */
            <div style={{ flex: 1, overflowY: "auto", padding: "2rem" }}>
              <div style={{ maxWidth: 880, margin: "0 auto", display: "flex", flexDirection: "column", gap: "1.25rem" }}>
                <div style={{ background: "#ffffff", padding: "1.25rem 1.5rem", borderRadius: "14px", border: "1px solid #e2e8f0" }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "6px" }}>
                    <h3 style={{ margin: 0, fontSize: "1.1rem", color: "#0f172a" }}>
                      Adaptive DSA Roadmap • {targetRole}
                    </h3>
                    <span style={{ fontSize: "0.8rem", background: "#fef3c7", color: "#92400e", padding: "3px 10px", borderRadius: "14px", fontWeight: 700 }}>
                      Adjusted to Practice Score ({data?.overall_readiness_score}%)
                    </span>
                  </div>
                  <p style={{ margin: 0, fontSize: "0.88rem", color: "#64748b", lineHeight: 1.55 }}>
                    {data?.standing_summary}
                  </p>
                </div>

                {data?.dsa_roadmap?.map((stage) => {
                  const isCompleted = stage.status === "completed";
                  const isInProgress = stage.status === "in_progress";

                  return (
                    <div
                      key={stage.stage}
                      style={{
                        background: "#ffffff",
                        borderRadius: "14px",
                        border: isCompleted ? "1.5px solid #86efac" : isInProgress ? "1.5px solid #fde047" : "1px solid #e2e8f0",
                        padding: "1.4rem 1.6rem",
                        display: "flex",
                        gap: "1.25rem",
                        boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
                        position: "relative",
                      }}
                    >
                      <div
                        style={{
                          width: 48,
                          height: 48,
                          borderRadius: "12px",
                          background: isCompleted ? "#dcfce7" : isInProgress ? "#fef3c7" : "#f1f5f9",
                          color: isCompleted ? "#15803d" : isInProgress ? "#b45309" : "#64748b",
                          fontWeight: 800,
                          fontSize: "1.15rem",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          flexShrink: 0,
                          border: isCompleted ? "1px solid #bbf7d0" : isInProgress ? "1px solid #fde68a" : "1px solid #cbd5e1",
                        }}
                      >
                        {isCompleted ? "✓" : stage.stage}
                      </div>

                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "4px" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                            <h4 style={{ margin: 0, fontSize: "1.05rem", color: "#0f172a", fontWeight: 700 }}>
                              {stage.title}
                            </h4>
                            <span
                              style={{
                                fontSize: "0.72rem",
                                fontWeight: 700,
                                padding: "2px 8px",
                                borderRadius: "10px",
                                background: isCompleted ? "#dcfce7" : isInProgress ? "#fef3c7" : "#f1f5f9",
                                color: isCompleted ? "#15803d" : isInProgress ? "#b45309" : "#64748b",
                                textTransform: "uppercase",
                              }}
                            >
                              {isCompleted ? "Completed" : isInProgress ? "In Progress" : "Upcoming"}
                            </span>
                          </div>
                          <span style={{ fontSize: "0.78rem", background: "#f1f5f9", color: "#475569", padding: "2px 8px", borderRadius: "12px", fontWeight: 600 }}>
                            {stage.duration}
                          </span>
                        </div>

                        <div style={{ fontSize: "0.85rem", color: "#475569", marginBottom: "6px", fontWeight: 600 }}>
                          <strong>Pattern Focus:</strong> {stage.pattern}
                        </div>

                        <p style={{ margin: "0 0 10px 0", fontSize: "0.86rem", color: "#64748b", lineHeight: 1.5 }}>
                          {stage.learning_goal}
                        </p>

                        {/* Stage Assessment Tag */}
                        {stage.stage_assessment && (
                          <div
                            style={{
                              background: isCompleted ? "rgba(34, 197, 94, 0.08)" : "#f8fafc",
                              padding: "6px 12px",
                              borderRadius: "6px",
                              fontSize: "0.8rem",
                              color: isCompleted ? "#15803d" : "#334155",
                              marginBottom: "10px",
                              borderLeft: isCompleted ? "3px solid #22c55e" : "3px solid #94a3b8",
                            }}
                          >
                            <strong>Performance Check:</strong> {stage.stage_assessment}
                          </div>
                        )}

                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "8px" }}>
                          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                            {stage.topics.map((t, ti) => (
                              <span
                                key={ti}
                                style={{
                                  fontSize: "0.75rem",
                                  background: "#f1f5f9",
                                  color: "#334155",
                                  padding: "2px 8px",
                                  borderRadius: "4px",
                                  border: "1px solid #e2e8f0",
                                }}
                              >
                                {t}
                              </span>
                            ))}
                          </div>
                          <span style={{ fontSize: "0.8rem", color: "#64748b" }}>
                            Target: <strong>{stage.target_problems_count} problems</strong> • Mastery: <strong>{stage.mastery_score}%</strong>
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            /* TAB 3: SIMILAR PRACTICE PROBLEMS SPLIT VIEW */
            <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
              {/* Problem List Sidebar */}
              <div
                style={{
                  width: "350px",
                  borderRight: "1px solid #e2e8f0",
                  background: "#ffffff",
                  overflowY: "auto",
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                <div style={{ padding: "1rem 1.25rem", borderBottom: "1px solid #f1f5f9", fontSize: "0.8rem", fontWeight: 700, color: "#64748b" }}>
                  AI-CURATED PROBLEMS ({data?.recommended_problems?.length || 0})
                </div>
                {data?.recommended_problems?.map((prob) => {
                  const isSel = selectedProblem?.id === prob.id;
                  const isDone = solvedProblems.includes(prob.id);
                  return (
                    <div
                      key={prob.id}
                      onClick={() => setSelectedProblem(prob)}
                      style={{
                        padding: "1rem 1.25rem",
                        borderBottom: "1px solid #f1f5f9",
                        cursor: "pointer",
                        background: isSel ? "#f8fafc" : "#ffffff",
                        borderLeft: isSel ? "4px solid #f59e0b" : "4px solid transparent",
                        transition: "all 0.15s ease",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "4px" }}>
                        <span
                          style={{
                            fontSize: "0.72rem",
                            fontWeight: 700,
                            padding: "2px 6px",
                            borderRadius: "4px",
                            background: prob.difficulty === "Easy" ? "#dcfce7" : prob.difficulty === "Hard" ? "#fee2e2" : "#fef3c7",
                            color: prob.difficulty === "Easy" ? "#15803d" : prob.difficulty === "Hard" ? "#b91c1c" : "#b45309",
                          }}
                        >
                          {prob.difficulty}
                        </span>
                        {isDone && (
                          <span style={{ display: "inline-flex", alignItems: "center", gap: "3px", color: "#16a34a", fontSize: "0.75rem", fontWeight: 700 }}>
                            <CheckCircle2 size={13} /> Solved
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: "0.88rem", fontWeight: 600, color: "#0f172a", marginBottom: "4px" }}>
                        {prob.title}
                      </div>
                      <div style={{ fontSize: "0.76rem", color: "#64748b" }}>
                        {prob.topic} • {prob.similar_to?.slice(0, 24)}...
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Problem Details Workspace */}
              {selectedProblem && (
                <div style={{ flex: 1, overflowY: "auto", padding: "1.75rem 2rem", background: "#f8fafc" }}>
                  <div style={{ maxWidth: 780, margin: "0 auto", display: "flex", flexDirection: "column", gap: "1.25rem" }}>
                    <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
                      <div>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                          <span
                            style={{
                              fontSize: "0.75rem",
                              fontWeight: 700,
                              padding: "2px 8px",
                              borderRadius: "4px",
                              background: selectedProblem.difficulty === "Easy" ? "#dcfce7" : selectedProblem.difficulty === "Hard" ? "#fee2e2" : "#fef3c7",
                              color: selectedProblem.difficulty === "Easy" ? "#15803d" : selectedProblem.difficulty === "Hard" ? "#b91c1c" : "#b45309",
                            }}
                          >
                            {selectedProblem.difficulty}
                          </span>
                          <span style={{ fontSize: "0.8rem", color: "#64748b", fontWeight: 600 }}>
                            {selectedProblem.topic}
                          </span>
                        </div>
                        <h2 style={{ margin: 0, fontSize: "1.35rem", fontWeight: 700, color: "#0f172a" }}>
                          {selectedProblem.title}
                        </h2>
                        {selectedProblem.similar_to && (
                          <div style={{ fontSize: "0.82rem", color: "#b45309", marginTop: "4px", fontStyle: "italic" }}>
                            Similar pattern to: {selectedProblem.similar_to}
                          </div>
                        )}
                      </div>

                      <button
                        type="button"
                        onClick={() => toggleSolved(selectedProblem)}
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "6px",
                          padding: "8px 16px",
                          borderRadius: "8px",
                          border: "none",
                          background: solvedProblems.includes(selectedProblem.id) ? "#16a34a" : "#0f172a",
                          color: "#ffffff",
                          fontSize: "0.85rem",
                          fontWeight: 600,
                          cursor: "pointer",
                          boxShadow: "0 2px 6px rgba(0,0,0,0.15)",
                        }}
                      >
                        <CheckCircle2 size={16} />
                        {solvedProblems.includes(selectedProblem.id) ? "Completed ✓" : "Mark as Solved"}
                      </button>
                    </div>

                    {/* Problem Statement */}
                    <div style={{ background: "#ffffff", padding: "1.25rem 1.5rem", borderRadius: "12px", border: "1px solid #e2e8f0" }}>
                      <h4 style={{ margin: "0 0 8px 0", fontSize: "0.9rem", color: "#0f172a" }}>Problem Statement</h4>
                      <p style={{ margin: 0, fontSize: "0.92rem", color: "#334155", lineHeight: 1.6 }}>
                        {selectedProblem.description}
                      </p>
                    </div>

                    {/* Attached Resources */}
                    {selectedProblem.resources && selectedProblem.resources.length > 0 && (
                      <div style={{ background: "#ffffff", padding: "1rem 1.25rem", borderRadius: "12px", border: "1px solid #e2e8f0" }}>
                        <div style={{ fontSize: "0.78rem", fontWeight: 700, color: "#64748b", marginBottom: "8px", display: "flex", alignItems: "center", gap: "6px" }}>
                          <BookOpen size={14} color="#f59e0b" /> PATTERN RESOURCES & CHEAT SHEETS
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                          {selectedProblem.resources.map((res, ri) => (
                            <a
                              key={ri}
                              href={res.url}
                              target="_blank"
                              rel="noreferrer"
                              style={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                                padding: "6px 12px",
                                borderRadius: "6px",
                                background: "#f8fafc",
                                border: "1px solid #f1f5f9",
                                textDecoration: "none",
                                fontSize: "0.82rem",
                                color: "#2563eb",
                              }}
                            >
                              <span style={{ fontWeight: 600 }}>{res.title}</span>
                              <span style={{ display: "inline-flex", alignItems: "center", gap: "4px", fontSize: "0.74rem", color: "#64748b" }}>
                                {res.resource_type} <ExternalLink size={12} />
                              </span>
                            </a>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Examples */}
                    {selectedProblem.examples?.map((ex, i) => (
                      <div key={i} style={{ background: "#ffffff", padding: "1rem 1.25rem", borderRadius: "10px", border: "1px solid #e2e8f0" }}>
                        <div style={{ fontSize: "0.78rem", fontWeight: 700, color: "#64748b", marginBottom: "4px" }}>
                          EXAMPLE {i + 1}
                        </div>
                        <div style={{ fontFamily: "monospace", fontSize: "0.84rem", background: "#f8fafc", padding: "8px 12px", borderRadius: "6px", marginBottom: "4px" }}>
                          <strong>Input:</strong> {ex.input}
                          <br />
                          <strong>Output:</strong> {ex.output}
                        </div>
                        {ex.explanation && (
                          <div style={{ fontSize: "0.82rem", color: "#64748b" }}>
                            <strong>Explanation:</strong> {ex.explanation}
                          </div>
                        )}
                      </div>
                    ))}

                    {/* Hints (Collapsible) */}
                    <div>
                      <h4 style={{ margin: "0 0 8px 0", fontSize: "0.9rem", color: "#0f172a", display: "flex", alignItems: "center", gap: "6px" }}>
                        <HelpCircle size={15} color="#2563eb" /> Problem Hints
                      </h4>
                      <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                        {selectedProblem.hints?.map((hint, i) => (
                          <div key={i} style={{ border: "1px solid #e2e8f0", borderRadius: "8px", overflow: "hidden", background: "#ffffff" }}>
                            <button
                              type="button"
                              onClick={() => toggleHint(i)}
                              style={{
                                width: "100%",
                                padding: "8px 12px",
                                border: "none",
                                background: "#ffffff",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                                fontSize: "0.84rem",
                                fontWeight: 600,
                                color: "#475569",
                                cursor: "pointer",
                              }}
                            >
                              <span>Hint {i + 1}</span>
                              {revealedHints[i] ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                            </button>
                            {revealedHints[i] && (
                              <div style={{ padding: "8px 12px", background: "#f8fafc", fontSize: "0.84rem", color: "#334155", borderTop: "1px solid #f1f5f9" }}>
                                {hint}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Algorithmic Approach & Complexity */}
                    <div style={{ background: "#fef3c7", padding: "1rem 1.25rem", borderRadius: "10px", border: "1px solid #fde68a" }}>
                      <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#92400e", marginBottom: "4px" }}>
                        OPTIMAL ALGORITHMIC APPROACH
                      </div>
                      <p style={{ margin: "0 0 6px 0", fontSize: "0.88rem", color: "#78350f" }}>
                        {selectedProblem.approach}
                      </p>
                      <div style={{ display: "flex", gap: "16px", fontSize: "0.8rem", color: "#92400e", fontWeight: 600 }}>
                        <span>Time Complexity: {selectedProblem.time_complexity || "O(N)"}</span>
                        <span>Space Complexity: {selectedProblem.space_complexity || "O(1)"}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
