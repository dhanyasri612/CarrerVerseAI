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
          background: "var(--cv-surface)",
          width: "100%",
          maxWidth: "1120px",
          height: "92vh",
          maxHeight: "880px",
          borderRadius: "20px",
          boxShadow: "0 25px 60px -15px rgba(0,0,0,0.4)",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          border: "1px solid var(--cv-border)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          style={{
            padding: "1.25rem 2rem",
            background: "var(--cv-surface-raised)",
            color: "var(--cv-text)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            borderBottom: "1px solid var(--cv-border)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: "12px",
                background: "linear-gradient(135deg, var(--cv-warning) 0%, var(--cv-accent-hover) 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "var(--cv-text-inverse)",
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
                    color: "var(--cv-warning)",
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
                      color: "var(--cv-success)",
                      padding: "2px 8px",
                      borderRadius: "6px",
                      fontWeight: 600,
                    }}
                  >
                    LeetCode Connected
                  </span>
                )}
              </div>
              <h2 style={{ margin: "2px 0 0 0", fontSize: "1.35rem", fontWeight: 700, color: "var(--cv-text)" }}>
                DSA Mastery, Topic Separation & Performance Roadmap
              </h2>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div style={{ display: "flex", background: "var(--cv-surface-raised)", borderRadius: "10px", padding: "4px", gap: "4px" }}>
              <button
                type="button"
                onClick={() => setActiveTab("topics")}
                style={{
                  padding: "7px 14px",
                  borderRadius: "7px",
                  border: "none",
                  background: activeTab === "topics" ? "var(--cv-warning)" : "transparent",
                  color: activeTab === "topics" ? "var(--cv-text-inverse)" : "var(--cv-text-muted)",
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
                  background: activeTab === "roadmap" ? "var(--cv-warning)" : "transparent",
                  color: activeTab === "roadmap" ? "var(--cv-text-inverse)" : "var(--cv-text-muted)",
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
                  background: activeTab === "problems" ? "var(--cv-warning)" : "transparent",
                  color: activeTab === "problems" ? "var(--cv-text-inverse)" : "var(--cv-text-muted)",
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
                background: "var(--cv-surface)",
                color: "var(--cv-text)",
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
            background: "var(--cv-surface-raised)",
            padding: "0.85rem 2rem",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            borderBottom: "1px solid var(--cv-border)",
            color: "var(--cv-text)",
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
              <Award size={15} color="var(--cv-warning)" />
              <span style={{ color: "var(--cv-warning)", fontWeight: 700 }}>
                Readiness: {data?.overall_readiness_score || 65}%
              </span>
            </div>

            <span>
              <strong>Total Solved:</strong>{" "}
              <span style={{ color: "var(--cv-warning)", fontWeight: 700 }}>{lcStats.total_solved || 0}</span>
            </span>
            <span>
              <strong>Easy:</strong> <span style={{ color: "var(--cv-success)" }}>{lcStats.easy_solved || 0}</span>
            </span>
            <span>
              <strong>Medium:</strong> <span style={{ color: "var(--cv-warning)" }}>{lcStats.medium_solved || 0}</span>
            </span>
            <span>
              <strong>Hard:</strong> <span style={{ color: "var(--cv-danger)" }}>{lcStats.hard_solved || 0}</span>
            </span>
            <span>
              <strong>Daily Solved in App:</strong>{" "}
              <span style={{ color: "var(--cv-info)", fontWeight: 700 }}>{solvedProblems.length}</span>
            </span>
          </div>

          <div
            style={{
              color: "var(--cv-text-muted)",
              fontSize: "0.8rem",
              background: "var(--cv-surface)",
              padding: "4px 12px",
              borderRadius: "6px",
              border: "1px solid var(--cv-border)",
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
        <div style={{ flex: 1, overflow: "hidden", display: "flex", background: "var(--cv-bg-subtle)" }}>
          {loading ? (
            <div style={{ margin: "auto", textAlign: "center", color: "var(--cv-text-muted)" }}>
              <Sparkles
                size={32}
                color="var(--cv-warning)"
                style={{ animation: "spin 2s linear infinite", marginBottom: "10px" }}
              />
              <div style={{ fontWeight: 600, fontSize: "1rem", color: "var(--cv-text)" }}>
                Analyzing Daily Practice & Evaluating Algorithmic Mastery...
              </div>
              <div style={{ fontSize: "0.85rem", color: "var(--cv-text-muted)", marginTop: "4px" }}>
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
                    background: "linear-gradient(135deg, var(--cv-surface) 0%, var(--cv-surface-raised) 100%)",
                    padding: "1.25rem 1.5rem",
                    borderRadius: "14px",
                    color: "var(--cv-text)",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    border: "1px solid var(--cv-border)",
                  }}
                >
                  <div>
                    <h3 style={{ margin: "0 0 6px 0", fontSize: "1.1rem", color: "var(--cv-text)", fontWeight: 700 }}>
                      Algorithmic Practice Diagnostic • {targetRole}
                    </h3>
                    <p style={{ margin: 0, fontSize: "0.86rem", color: "var(--cv-text-muted)", lineHeight: 1.5 }}>
                      We categorize your algorithmic skills into <strong>Already Practiced Topics</strong> (with a verified
                      check if you are &ldquo;Good Enough&rdquo; for technical phone screens) and <strong>Priority Topics Needing Practice</strong>.
                    </p>
                  </div>
                  <div style={{ textAlign: "right", minWidth: "160px" }}>
                    <div style={{ fontSize: "0.75rem", color: "var(--cv-text-muted)" }}>CURRENT BENCHMARK</div>
                    <div style={{ fontSize: "1.3rem", fontWeight: 800, color: "var(--cv-warning)" }}>
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
                        background: "var(--cv-success-soft)",
                        color: "var(--cv-success)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "0.85rem",
                        fontWeight: 800,
                      }}
                    >
                      ✓
                    </div>
                    <h3 style={{ margin: 0, fontSize: "1.05rem", color: "var(--cv-surface-raised)", fontWeight: 700 }}>
                      Already Practiced Topics ({practicedTopics.length})
                    </h3>
                    <span style={{ fontSize: "0.78rem", color: "var(--cv-text-muted)" }}>
                      • Evaluated for technical interview readiness
                    </span>
                  </div>

                  {practicedTopics.length === 0 ? (
                    <div
                      style={{
                        padding: "1.5rem",
                        background: "var(--cv-surface)",
                        borderRadius: "12px",
                        border: "1px dashed var(--cv-border)",
                        textAlign: "center",
                        color: "var(--cv-text-muted)",
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
                            background: "var(--cv-surface)",
                            borderRadius: "14px",
                            border: topic.is_good_enough ? "1.5px solid var(--cv-success-soft)" : "1px solid var(--cv-border)",
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
                              <div style={{ fontSize: "1rem", fontWeight: 700, color: "var(--cv-surface-raised)" }}>
                                {topic.topic}
                              </div>
                              <div style={{ fontSize: "0.78rem", color: "var(--cv-text-muted)" }}>
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
                                background: topic.is_good_enough ? "var(--cv-success-soft)" : "var(--cv-warning)",
                                color: topic.is_good_enough ? "var(--cv-success)" : "var(--cv-warning)",
                                border: topic.is_good_enough ? "1px solid var(--cv-success-soft)" : "1px solid var(--cv-warning)",
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
                            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.74rem", color: "var(--cv-text-muted)", marginBottom: "4px" }}>
                              <span>Topic Mastery</span>
                              <span style={{ fontWeight: 700, color: topic.is_good_enough ? "var(--cv-success)" : "var(--cv-warning)" }}>
                                {topic.score_percent}%
                              </span>
                            </div>
                            <div style={{ height: "6px", background: "var(--cv-bg-subtle)", borderRadius: "3px", overflow: "hidden" }}>
                              <div
                                style={{
                                  height: "100%",
                                  width: `${topic.score_percent}%`,
                                  background: topic.is_good_enough ? "var(--cv-success)" : "var(--cv-warning)",
                                  borderRadius: "3px",
                                }}
                              />
                            </div>
                          </div>

                          {/* Assessment Verdict */}
                          <div
                            style={{
                              background: "var(--cv-surface)",
                              padding: "8px 12px",
                              borderRadius: "8px",
                              fontSize: "0.82rem",
                              color: "var(--cv-text-muted)",
                              lineHeight: 1.45,
                              borderLeft: topic.is_good_enough ? "3px solid var(--cv-success)" : "3px solid var(--cv-warning)",
                            }}
                          >
                            <strong>Verdict:</strong> {topic.assessment_verdict}
                          </div>

                          {/* Curated Resources */}
                          {topic.resources && topic.resources.length > 0 && (
                            <div style={{ marginTop: "4px" }}>
                              <div style={{ fontSize: "0.74rem", fontWeight: 700, color: "var(--cv-text-muted)", textTransform: "uppercase", marginBottom: "6px", display: "flex", alignItems: "center", gap: "4px" }}>
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
                                      color: "var(--cv-info)",
                                      textDecoration: "none",
                                      background: "var(--cv-bg-subtle)",
                                      padding: "5px 10px",
                                      borderRadius: "6px",
                                    }}
                                  >
                                    <span style={{ fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                                      {res.title}
                                    </span>
                                    <span style={{ display: "inline-flex", alignItems: "center", gap: "2px", fontSize: "0.72rem", color: "var(--cv-text-muted)", flexShrink: 0 }}>
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
                        background: "var(--cv-danger-soft)",
                        color: "var(--cv-danger)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "0.85rem",
                        fontWeight: 800,
                      }}
                    >
                      !
                    </div>
                    <h3 style={{ margin: 0, fontSize: "1.05rem", color: "var(--cv-surface-raised)", fontWeight: 700 }}>
                      Topics Needing Practice ({toPracticeTopics.length})
                    </h3>
                    <span style={{ fontSize: "0.78rem", color: "var(--cv-text-muted)" }}>
                      • High frequency in {targetRole} interviews
                    </span>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(490px, 1fr))", gap: "1rem" }}>
                    {toPracticeTopics.map((topic, i) => (
                      <div
                        key={i}
                        style={{
                          background: "var(--cv-surface)",
                          borderRadius: "14px",
                          border: "1px solid var(--cv-border)",
                          padding: "1.25rem 1.4rem",
                          boxShadow: "0 2px 6px rgba(0,0,0,0.03)",
                          display: "flex",
                          flexDirection: "column",
                          gap: "10px",
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
                          <div>
                            <div style={{ fontSize: "1rem", fontWeight: 700, color: "var(--cv-surface-raised)" }}>
                              {topic.topic}
                            </div>
                            <div style={{ fontSize: "0.78rem", color: "var(--cv-warning)", fontWeight: 500 }}>
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
                              background: "var(--cv-danger-soft)",
                              color: "var(--cv-danger)",
                            }}
                          >
                            <AlertTriangle size={12} /> Priority Need
                          </span>
                        </div>

                        {/* Recommendation */}
                        <div
                          style={{
                            background: "var(--cv-warning)",
                            padding: "8px 12px",
                            borderRadius: "8px",
                            fontSize: "0.82rem",
                            color: "var(--cv-warning)",
                            lineHeight: 1.45,
                            borderLeft: "3px solid var(--cv-warning)",
                          }}
                        >
                          <strong>Action Plan:</strong> {topic.recommended_action}
                        </div>

                        {/* Verified Resources for This Priority Topic */}
                        {topic.resources && topic.resources.length > 0 && (
                          <div>
                            <div style={{ fontSize: "0.74rem", fontWeight: 700, color: "var(--cv-text-muted)", textTransform: "uppercase", marginBottom: "6px", display: "flex", alignItems: "center", gap: "4px" }}>
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
                                    color: "var(--cv-info)",
                                    textDecoration: "none",
                                    background: "var(--cv-surface)",
                                    border: "1px solid var(--cv-border)",
                                    padding: "6px 10px",
                                    borderRadius: "6px",
                                  }}
                                >
                                  <div>
                                    <div style={{ fontWeight: 600, color: "var(--cv-surface-raised)" }}>{res.title}</div>
                                    <div style={{ fontSize: "0.72rem", color: "var(--cv-text-muted)" }}>{res.summary}</div>
                                  </div>
                                  <ExternalLink size={13} color="var(--cv-info)" style={{ flexShrink: 0, marginLeft: "8px" }} />
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
                <div style={{ background: "var(--cv-surface)", padding: "1.25rem 1.5rem", borderRadius: "14px", border: "1px solid var(--cv-border)" }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "6px" }}>
                    <h3 style={{ margin: 0, fontSize: "1.1rem", color: "var(--cv-surface-raised)" }}>
                      Adaptive DSA Roadmap • {targetRole}
                    </h3>
                    <span style={{ fontSize: "0.8rem", background: "var(--cv-warning-soft)", color: "var(--cv-warning)", padding: "3px 10px", borderRadius: "14px", fontWeight: 700 }}>
                      Adjusted to Practice Score ({data?.overall_readiness_score}%)
                    </span>
                  </div>
                  <p style={{ margin: 0, fontSize: "0.88rem", color: "var(--cv-text-muted)", lineHeight: 1.55 }}>
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
                        background: "var(--cv-surface)",
                        borderRadius: "14px",
                        border: isCompleted ? "1.5px solid var(--cv-success-soft)" : isInProgress ? "1.5px solid var(--cv-warning)" : "1px solid var(--cv-border)",
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
                          background: isCompleted ? "var(--cv-success-soft)" : isInProgress ? "var(--cv-warning)" : "var(--cv-bg-subtle)",
                          color: isCompleted ? "var(--cv-success)" : isInProgress ? "var(--cv-warning)" : "var(--cv-text-muted)",
                          fontWeight: 800,
                          fontSize: "1.15rem",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          flexShrink: 0,
                          border: isCompleted ? "1px solid var(--cv-success-soft)" : isInProgress ? "1px solid var(--cv-warning)" : "1px solid var(--cv-border)",
                        }}
                      >
                        {isCompleted ? "✓" : stage.stage}
                      </div>

                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "4px" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                            <h4 style={{ margin: 0, fontSize: "1.05rem", color: "var(--cv-surface-raised)", fontWeight: 700 }}>
                              {stage.title}
                            </h4>
                            <span
                              style={{
                                fontSize: "0.72rem",
                                fontWeight: 700,
                                padding: "2px 8px",
                                borderRadius: "10px",
                                background: isCompleted ? "var(--cv-success-soft)" : isInProgress ? "var(--cv-warning)" : "var(--cv-bg-subtle)",
                                color: isCompleted ? "var(--cv-success)" : isInProgress ? "var(--cv-warning)" : "var(--cv-text-muted)",
                                textTransform: "uppercase",
                              }}
                            >
                              {isCompleted ? "Completed" : isInProgress ? "In Progress" : "Upcoming"}
                            </span>
                          </div>
                          <span style={{ fontSize: "0.78rem", background: "var(--cv-bg-subtle)", color: "var(--cv-text-muted)", padding: "2px 8px", borderRadius: "12px", fontWeight: 600 }}>
                            {stage.duration}
                          </span>
                        </div>

                        <div style={{ fontSize: "0.85rem", color: "var(--cv-text-muted)", marginBottom: "6px", fontWeight: 600 }}>
                          <strong>Pattern Focus:</strong> {stage.pattern}
                        </div>

                        <p style={{ margin: "0 0 10px 0", fontSize: "0.86rem", color: "var(--cv-text-muted)", lineHeight: 1.5 }}>
                          {stage.learning_goal}
                        </p>

                        {/* Stage Assessment Tag */}
                        {stage.stage_assessment && (
                          <div
                            style={{
                              background: isCompleted ? "rgba(34, 197, 94, 0.08)" : "var(--cv-surface)",
                              padding: "6px 12px",
                              borderRadius: "6px",
                              fontSize: "0.8rem",
                              color: isCompleted ? "var(--cv-success)" : "var(--cv-text-muted)",
                              marginBottom: "10px",
                              borderLeft: isCompleted ? "3px solid var(--cv-success)" : "3px solid var(--cv-text-muted)",
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
                                  background: "var(--cv-bg-subtle)",
                                  color: "var(--cv-text-muted)",
                                  padding: "2px 8px",
                                  borderRadius: "4px",
                                  border: "1px solid var(--cv-border)",
                                }}
                              >
                                {t}
                              </span>
                            ))}
                          </div>
                          <span style={{ fontSize: "0.8rem", color: "var(--cv-text-muted)" }}>
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
                  borderRight: "1px solid var(--cv-border)",
                  background: "var(--cv-surface)",
                  overflowY: "auto",
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                <div style={{ padding: "1rem 1.25rem", borderBottom: "1px solid var(--cv-bg-subtle)", fontSize: "0.8rem", fontWeight: 700, color: "var(--cv-text-muted)" }}>
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
                        borderBottom: "1px solid var(--cv-bg-subtle)",
                        cursor: "pointer",
                        background: isSel ? "var(--cv-surface)" : "var(--cv-bg-subtle)",
                        borderLeft: isSel ? "4px solid var(--cv-warning)" : "4px solid transparent",
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
                            background: prob.difficulty === "Easy" ? "var(--cv-success-soft)" : prob.difficulty === "Hard" ? "var(--cv-danger-soft)" : "var(--cv-warning-soft)",
                            color: prob.difficulty === "Easy" ? "var(--cv-success)" : prob.difficulty === "Hard" ? "var(--cv-danger)" : "var(--cv-warning)",
                          }}
                        >
                          {prob.difficulty}
                        </span>
                        {isDone && (
                          <span style={{ display: "inline-flex", alignItems: "center", gap: "3px", color: "var(--cv-success)", fontSize: "0.75rem", fontWeight: 700 }}>
                            <CheckCircle2 size={13} /> Solved
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: "0.88rem", fontWeight: 600, color: "var(--cv-surface-raised)", marginBottom: "4px" }}>
                        {prob.title}
                      </div>
                      <div style={{ fontSize: "0.76rem", color: "var(--cv-text-muted)" }}>
                        {prob.topic} • {prob.similar_to?.slice(0, 24)}...
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Problem Details Workspace */}
              {selectedProblem && (
                <div style={{ flex: 1, overflowY: "auto", padding: "1.75rem 2rem", background: "var(--cv-surface)" }}>
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
                              background: selectedProblem.difficulty === "Easy" ? "var(--cv-success-soft)" : selectedProblem.difficulty === "Hard" ? "var(--cv-danger-soft)" : "var(--cv-warning-soft)",
                              color: selectedProblem.difficulty === "Easy" ? "var(--cv-success)" : selectedProblem.difficulty === "Hard" ? "var(--cv-danger)" : "var(--cv-warning)",
                            }}
                          >
                            {selectedProblem.difficulty}
                          </span>
                          <span style={{ fontSize: "0.8rem", color: "var(--cv-text-muted)", fontWeight: 600 }}>
                            {selectedProblem.topic}
                          </span>
                        </div>
                        <h2 style={{ margin: 0, fontSize: "1.35rem", fontWeight: 700, color: "var(--cv-surface-raised)" }}>
                          {selectedProblem.title}
                        </h2>
                        {selectedProblem.similar_to && (
                          <div style={{ fontSize: "0.82rem", color: "var(--cv-warning)", marginTop: "4px", fontStyle: "italic" }}>
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
                          background: solvedProblems.includes(selectedProblem.id) ? "var(--cv-success)" : "var(--cv-surface-raised)",
                          color: "var(--cv-text)",
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
                    <div style={{ background: "var(--cv-surface)", padding: "1.25rem 1.5rem", borderRadius: "12px", border: "1px solid var(--cv-border)" }}>
                      <h4 style={{ margin: "0 0 8px 0", fontSize: "0.9rem", color: "var(--cv-surface-raised)" }}>Problem Statement</h4>
                      <p style={{ margin: 0, fontSize: "0.92rem", color: "var(--cv-text-muted)", lineHeight: 1.6 }}>
                        {selectedProblem.description}
                      </p>
                    </div>

                    {/* Attached Resources */}
                    {selectedProblem.resources && selectedProblem.resources.length > 0 && (
                      <div style={{ background: "var(--cv-surface)", padding: "1rem 1.25rem", borderRadius: "12px", border: "1px solid var(--cv-border)" }}>
                        <div style={{ fontSize: "0.78rem", fontWeight: 700, color: "var(--cv-text-muted)", marginBottom: "8px", display: "flex", alignItems: "center", gap: "6px" }}>
                          <BookOpen size={14} color="var(--cv-warning)" /> PATTERN RESOURCES & CHEAT SHEETS
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
                                background: "var(--cv-surface)",
                                border: "1px solid var(--cv-bg-subtle)",
                                textDecoration: "none",
                                fontSize: "0.82rem",
                                color: "var(--cv-info)",
                              }}
                            >
                              <span style={{ fontWeight: 600 }}>{res.title}</span>
                              <span style={{ display: "inline-flex", alignItems: "center", gap: "4px", fontSize: "0.74rem", color: "var(--cv-text-muted)" }}>
                                {res.resource_type} <ExternalLink size={12} />
                              </span>
                            </a>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Examples */}
                    {selectedProblem.examples?.map((ex, i) => (
                      <div key={i} style={{ background: "var(--cv-surface)", padding: "1rem 1.25rem", borderRadius: "10px", border: "1px solid var(--cv-border)" }}>
                        <div style={{ fontSize: "0.78rem", fontWeight: 700, color: "var(--cv-text-muted)", marginBottom: "4px" }}>
                          EXAMPLE {i + 1}
                        </div>
                        <div style={{ fontFamily: "monospace", fontSize: "0.84rem", background: "var(--cv-surface)", padding: "8px 12px", borderRadius: "6px", marginBottom: "4px" }}>
                          <strong>Input:</strong> {ex.input}
                          <br />
                          <strong>Output:</strong> {ex.output}
                        </div>
                        {ex.explanation && (
                          <div style={{ fontSize: "0.82rem", color: "var(--cv-text-muted)" }}>
                            <strong>Explanation:</strong> {ex.explanation}
                          </div>
                        )}
                      </div>
                    ))}

                    {/* Hints (Collapsible) */}
                    <div>
                      <h4 style={{ margin: "0 0 8px 0", fontSize: "0.9rem", color: "var(--cv-surface-raised)", display: "flex", alignItems: "center", gap: "6px" }}>
                        <HelpCircle size={15} color="var(--cv-info)" /> Problem Hints
                      </h4>
                      <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                        {selectedProblem.hints?.map((hint, i) => (
                          <div key={i} style={{ border: "1px solid var(--cv-border)", borderRadius: "8px", overflow: "hidden", background: "var(--surface, var(--cv-surface))" }}>
                            <button
                              type="button"
                              onClick={() => toggleHint(i)}
                              style={{
                                width: "100%",
                                padding: "8px 12px",
                                border: "none",
                                background: "var(--cv-surface)",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                                fontSize: "0.84rem",
                                fontWeight: 600,
                                color: "var(--cv-text-muted)",
                                cursor: "pointer",
                              }}
                            >
                              <span>Hint {i + 1}</span>
                              {revealedHints[i] ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                            </button>
                            {revealedHints[i] && (
                              <div style={{ padding: "8px 12px", background: "var(--cv-surface)", fontSize: "0.84rem", color: "var(--cv-text-muted)", borderTop: "1px solid var(--cv-bg-subtle)" }}>
                                {hint}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Algorithmic Approach & Complexity */}
                    <div style={{ background: "var(--cv-warning-soft)", padding: "1rem 1.25rem", borderRadius: "10px", border: "1px solid var(--cv-warning)" }}>
                      <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "var(--cv-warning)", marginBottom: "4px" }}>
                        OPTIMAL ALGORITHMIC APPROACH
                      </div>
                      <p style={{ margin: "0 0 6px 0", fontSize: "0.88rem", color: "var(--cv-warning)" }}>
                        {selectedProblem.approach}
                      </p>
                      <div style={{ display: "flex", gap: "16px", fontSize: "0.8rem", color: "var(--cv-warning)", fontWeight: 600 }}>
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
