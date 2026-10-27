import React, { useEffect, useState, useMemo } from "react";
import { Link, useLocation, useSearchParams } from "react-router-dom";
import {
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Network,
  ListOrdered,
  Clock,
  CheckCircle2,
  Circle,
  AlertTriangle,
  ExternalLink,
  RefreshCw,
  X,
  BookOpen,
  Hammer,
  Zap,
  Target,
  FileText,
  ChevronDown,
  ChevronUp,
  TrendingUp,
  ShieldCheck,
  Milestone,
} from "lucide-react";

import { getApiError } from "../services/api";
import {
  getPersonalizedRoadmap,
  acceptRoadmapRecommendation,
  dismissRoadmapRecommendation,
  toggleMilestoneProgress,
} from "../services/careerService";
import { LoadingState, ErrorState } from "../components/AsyncState";
import RoadmapTechTree from "../components/roadmap/RoadmapTechTree";
import "./LearningRoadmapPage.css";

const STANDARD_ROLES = [
  "AI Engineer",
  "Full Stack Developer",
  "Backend Developer",
  "Data Scientist",
  "Frontend Developer",
  "Software Developer",
  "UI/UX Designer",
  "Machine Learning Engineer",
];

export default function LearningRoadmapPage() {
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();

  const queryRole = searchParams.get("role");
  const stateRole = location.state?.targetRole;
  const storedRole = typeof window !== "undefined" ? sessionStorage.getItem("careerverse_target_role") : null;
  const activeRole = queryRole || stateRole || storedRole || "AI Engineer";

  const [roadmapData, setRoadmapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [viewMode, setViewMode] = useState("timeline"); // "tree" | "timeline" | "curriculum"

  // Evidence modal state
  const [inspectingEvidence, setInspectingEvidence] = useState(null);

  // Milestone drawer state
  const [activeDrawerMilestone, setActiveDrawerMilestone] = useState(null);

  // Curriculum accordion state
  const [expandedCurriculumStages, setExpandedCurriculumStages] = useState({ 1: true, 2: true });

  const availableRoles = useMemo(() => {
    let discovered = [];
    try {
      const stored = sessionStorage.getItem("careerverse_discovered_roles");
      if (stored) discovered = JSON.parse(stored);
    } catch {}
    const list = [...discovered, activeRole, ...STANDARD_ROLES].filter(Boolean);
    return Array.from(new Set(list));
  }, [activeRole]);

  const fetchRoadmap = async (roleName, forceRefresh = false) => {
    if (forceRefresh) setRefreshing(true);
    else setLoading(true);
    setError("");

    try {
      const data = await getPersonalizedRoadmap(roleName, forceRefresh);
      setRoadmapData(data);
    } catch (err) {
      setError(getApiError(err, `Unable to generate career roadmap for ${roleName}.`));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchRoadmap(activeRole);
  }, [activeRole]);

  const handleRoleSelect = (roleName) => {
    if (roleName === activeRole && !error && !loading) return;
    sessionStorage.setItem("careerverse_target_role", roleName);
    setSearchParams({ role: roleName });
  };

  const handleToggleMilestone = async (milestoneId) => {
    try {
      const updated = await toggleMilestoneProgress(milestoneId);
      setRoadmapData(updated);
      if (activeDrawerMilestone && activeDrawerMilestone.id === milestoneId) {
        const matching = updated.milestones?.find((m) => m.id === milestoneId);
        if (matching) setActiveDrawerMilestone(matching);
      }
    } catch (err) {
      alert("Failed to update milestone status: " + getApiError(err));
    }
  };

  const handleAcceptRecommendation = async (changeId) => {
    try {
      setRefreshing(true);
      const updated = await acceptRoadmapRecommendation(changeId);
      setRoadmapData(updated);
    } catch (err) {
      alert("Failed to accept roadmap recommendation: " + getApiError(err));
    } finally {
      setRefreshing(false);
    }
  };

  const handleDismissRecommendation = async (changeId) => {
    try {
      await dismissRoadmapRecommendation(changeId);
      // Remove from pending_recommendations locally
      setRoadmapData((prev) => ({
        ...prev,
        pending_recommendations: (prev.pending_recommendations || []).filter((r) => r.id !== changeId),
      }));
    } catch (err) {
      alert("Failed to dismiss recommendation: " + getApiError(err));
    }
  };

  const toggleCurriculumStage = (stageNum) => {
    setExpandedCurriculumStages((prev) => ({
      ...prev,
      [stageNum]: !prev[stageNum],
    }));
  };

  const milestones = roadmapData?.milestones || roadmapData?.roadmap || [];
  const readiness = roadmapData?.readiness_score || 0;
  const verifiedSkills = roadmapData?.verified_skills || [];
  const keySkillGaps = roadmapData?.key_skill_gaps || [];
  const pendingRecs = roadmapData?.pending_recommendations || [];
  const trendSignals = roadmapData?.trend_signals || [];
  const changeHistory = roadmapData?.change_history || [];
  const nextMilestone = roadmapData?.next_milestone || milestones.find((m) => m.status !== "completed") || milestones[0];

  if (loading && !roadmapData) {
    return <LoadingState label={`Synthesizing intelligent trend-aware roadmap for ${activeRole}…`} />;
  }

  if (error && !roadmapData) {
    return <ErrorState message={error} onRetry={() => fetchRoadmap(activeRole)} />;
  }

  return (
    <div className="cv-roadmap-container">
      {/* ─── CHAPTER BREADCRUMB HEADER ───────────────────────────────────── */}
      <header className="cv-chapter-intro" style={{ marginBottom: "1.5rem" }}>
        <span className="cv-chapter-number">04 / 06</span>
        <div>
          <div className="cv-chapter-kicker">Intelligent Career Roadmap</div>
          <h1 className="cv-chapter-title">
            Personalized, Trend-Aware<br />
            <span className="serif">Engineering Journey.</span>
          </h1>
          <p className="cv-chapter-deck">
            Grounded in your verified code evidence, real-time technology signals, and role prerequisites.
          </p>
        </div>
      </header>

      {/* ─── ROLE SELECTOR TABS ─────────────────────────────────────────── */}
      <div className="cv-role-selector-bar">
        <span style={{ fontSize: "0.78rem", fontWeight: 700, color: "var(--cv-muted)", marginRight: 6 }}>
          CAREER TARGET:
        </span>
        {availableRoles.map((roleName) => {
          const isActive = roleName.toLowerCase() === activeRole.toLowerCase();
          return (
            <button
              key={roleName}
              onClick={() => handleRoleSelect(roleName)}
              className={`cv-role-tab-btn ${isActive ? "active" : ""}`}
              disabled={loading || refreshing}
            >
              {isActive && <Sparkles size={12} style={{ marginRight: 4 }} />}
              {roleName}
            </button>
          );
        })}
      </div>

      {/* ─── SECTION A: CAREER OVERVIEW ─────────────────────────────────── */}
      <section className="cv-roadmap-overview-card" data-testid="career-overview-section">
        <div className="cv-overview-left">
          <div className="cv-overview-header">
            <span className="cv-role-pill-badge">
              <Target size={14} />
              {activeRole}
            </span>
            <span style={{ fontSize: "0.8rem", color: "var(--cv-muted)" }}>
              Version {roadmapData?.current_version || 1}.0 • Reviewed{" "}
              {roadmapData?.last_reviewed_at ? new Date(roadmapData.last_reviewed_at).toLocaleDateString() : "Today"}
            </span>
            <button
              onClick={() => fetchRoadmap(activeRole, true)}
              disabled={refreshing}
              className="cv-btn-inspect"
              title="Re-evaluate roadmap against profile & industry trends"
              style={{ padding: "4px 10px" }}
            >
              <RefreshCw size={12} className={refreshing ? "spin-animation" : ""} />
              {refreshing ? "Re-evaluating…" : "Re-evaluate"}
            </button>
          </div>

          <h2 className="cv-overview-title">Career Trajectory to {activeRole}</h2>
          <p className="cv-overview-subtitle">
            {roadmapData?.version_summary ||
              "Intelligent curriculum structured across foundational and production milestones."}
          </p>

          {/* Skill Gaps & Verified Skills Chips */}
          <div className="cv-skill-chips-row">
            <span className="cv-chip-label">Verified:</span>
            {verifiedSkills.length > 0 ? (
              verifiedSkills.slice(0, 5).map((sk) => (
                <span key={sk} className="cv-skill-chip verified">
                  <ShieldCheck size={12} /> {sk}
                </span>
              ))
            ) : (
              <span style={{ fontSize: "0.8rem", color: "var(--cv-muted)" }}>Analyzing GitHub & coding activity…</span>
            )}

            <span className="cv-chip-label" style={{ marginLeft: "10px" }}>Priority Gaps:</span>
            {keySkillGaps.slice(0, 5).map((gap) => (
              <span key={gap} className="cv-skill-chip gap">
                <AlertTriangle size={11} /> {gap}
              </span>
            ))}
          </div>

          {/* Next Recommended Milestone Banner */}
          {nextMilestone && (
            <div className="cv-next-milestone-banner">
              <div className="cv-next-milestone-content">
                <span className="cv-next-milestone-badge">Next Milestone</span>
                <span className="cv-next-milestone-title">
                  Stage {nextMilestone.stage}: {nextMilestone.title}
                </span>
              </div>
              <button
                onClick={() => setActiveDrawerMilestone(nextMilestone)}
                className="cv-btn-milestone-toggle"
                style={{ padding: "6px 14px", fontSize: "0.8rem" }}
              >
                Inspect Milestone <ArrowRight size={13} />
              </button>
            </div>
          )}
        </div>

        {/* Readiness Dial Score */}
        <div className="cv-overview-right">
          <div className="cv-readiness-dial">
            <div className="cv-readiness-dial-value">{readiness}%</div>
            <div className="cv-readiness-dial-label">Target Readiness</div>
            <div style={{ fontSize: "0.72rem", color: "var(--cv-muted)", marginTop: 4 }}>
              {readiness >= 75 ? "Production Ready" : readiness >= 40 ? "Progressing Strongly" : "Foundational Focus"}
            </div>
          </div>
        </div>
      </section>

      {/* ─── SECTION B: EMERGING TECHNOLOGY & INDUSTRY SIGNALS ───────────── */}
      <section className="cv-signals-section" data-testid="trend-signals-section">
        {/* Pending Adaptive Update Recommendation Alert */}
        {pendingRecs.length > 0 && (
          <div className="cv-recommendation-alert">
            <div className="cv-alert-left">
              <Zap size={22} className="cv-alert-icon" />
              <div>
                <h3 className="cv-alert-title">{pendingRecs[0].title}</h3>
                <p className="cv-alert-desc">{pendingRecs[0].why_suggested}</p>
                <div className="cv-alert-meta">
                  <span>Source: {pendingRecs[0].evidence_source}</span>
                  <span>•</span>
                  <span>Date: {pendingRecs[0].evidence_date}</span>
                </div>
              </div>
            </div>
            <div className="cv-alert-actions">
              <button
                onClick={() => handleAcceptRecommendation(pendingRecs[0].id)}
                className="cv-btn-accept"
                disabled={refreshing}
              >
                <CheckCircle2 size={14} /> Accept Recommendation
              </button>
              <button
                onClick={() => setInspectingEvidence(pendingRecs[0])}
                className="cv-btn-dismiss"
              >
                View Evidence
              </button>
              <button
                onClick={() => handleDismissRecommendation(pendingRecs[0].id)}
                className="cv-btn-dismiss"
                title="Dismiss recommendation"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        <div className="cv-signals-section-header">
          <div>
            <h3 className="cv-section-title">
              <TrendingUp size={18} style={{ color: "var(--cv-accent)" }} />
              Emerging Technology & Industry Signals
            </h3>
            <p className="cv-section-subtitle">
              Verified 2024/2025 release evidence and job-market demand shifts monitored for {activeRole}.
            </p>
          </div>
        </div>

        {/* Signals Cards Grid */}
        <div className="cv-signals-grid">
          {trendSignals.slice(0, 3).map((sig) => (
            <div key={sig.id} className="cv-signal-card">
              <div className="cv-signal-header">
                <h4 className="cv-signal-tech">{sig.technology}</h4>
                <span className={`cv-signal-status-badge ${sig.trend_status}`}>
                  {sig.trend_status === "newly_released"
                    ? "Newly Released"
                    : sig.trend_status === "job_market_required"
                    ? "Job-Market Required"
                    : "Increased Adoption"}
                </span>
              </div>

              <p className="cv-signal-why">{sig.why_it_matters}</p>

              <div className="cv-signal-student-status">
                <ShieldCheck size={14} />
                <span>{sig.student_status}</span>
              </div>

              <div className="cv-signal-footer">
                <span>{sig.source_name} ({sig.publication_date})</span>
                <button
                  onClick={() => setInspectingEvidence(sig)}
                  className="cv-btn-inspect"
                >
                  Inspect Evidence <ExternalLink size={12} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ─── SECTION C: PERSONALIZED ROADMAP (3-WAY VIEWS) ──────────────── */}
      <section className="cv-roadmap-views-section" data-testid="roadmap-views-section">
        <div className="cv-view-toggle-bar">
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{ fontSize: "0.78rem", fontWeight: 700, color: "var(--cv-muted)" }}>
              SYNCHRONIZED VIEW:
            </span>
            <div className="cv-view-buttons-group">
              <button
                onClick={() => setViewMode("timeline")}
                className={`cv-view-tab-btn ${viewMode === "timeline" ? "active" : ""}`}
              >
                <Clock size={14} />
                Milestone Journey
              </button>
              <button
                onClick={() => setViewMode("tree")}
                className={`cv-view-tab-btn ${viewMode === "tree" ? "active" : ""}`}
              >
                <Network size={14} />
                Roadmap Tech Tree
              </button>
              <button
                onClick={() => setViewMode("curriculum")}
                className={`cv-view-tab-btn ${viewMode === "curriculum" ? "active" : ""}`}
              >
                <ListOrdered size={14} />
                Curriculum Guide
              </button>
            </div>
          </div>

          <div style={{ fontSize: "0.82rem", color: "var(--cv-muted)" }}>
            {milestones.filter((m) => m.status === "completed").length} of {milestones.length} Milestones Completed
          </div>
        </div>

        {/* 1. TIMELINE VIEW (COACHSMA INSPIRED CONNECTED JOURNEY) */}
        {viewMode === "timeline" && (
          <div className="cv-timeline-wrapper" data-testid="timeline-view">
            <div className="cv-timeline-spine" />
            {milestones.map((m) => {
              const isCompleted = m.status === "completed";
              const isInProgress = m.status === "in_progress";

              return (
                <div
                  key={m.id || m.stage}
                  className={`cv-timeline-milestone-card ${m.status}`}
                >
                  <div className="cv-milestone-node-indicator">
                    {isCompleted ? <CheckCircle2 size={24} /> : m.stage}
                  </div>

                  <div className="cv-milestone-card-body">
                    <div className="cv-milestone-card-top">
                      <span className="cv-milestone-category-badge">{m.category || "Core Milestone"}</span>
                      {m.estimated_effort && (
                        <span className="cv-milestone-effort-tag">
                          <Clock size={13} /> {m.estimated_effort}
                        </span>
                      )}
                    </div>

                    <h3 className="cv-milestone-card-title">{m.title}</h3>
                    <p className="cv-milestone-card-desc">{m.description}</p>

                    {m.why_recommended && (
                      <div className="cv-milestone-why-box">
                        <strong>Why recommended: </strong>
                        {m.why_recommended}
                      </div>
                    )}

                    {/* Practical Project Deliverable Box */}
                    {m.practical_project && (
                      <div className="cv-milestone-project-box">
                        <div className="cv-project-box-header">
                          <Hammer size={13} /> Practical Project Deliverable
                        </div>
                        <p className="cv-project-box-title">{m.practical_project}</p>
                      </div>
                    )}

                    {/* Skills pills */}
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginBottom: "1rem" }}>
                      {(m.skills || []).map((sk) => (
                        <span key={sk} className="cv-skill-chip" style={{ background: "rgba(0,0,0,0.04)" }}>
                          {isCompleted && <CheckCircle2 size={11} style={{ color: "#16a34a" }} />}
                          {sk}
                        </span>
                      ))}
                    </div>

                    {/* Action buttons */}
                    <div className="cv-milestone-actions-row">
                      <button
                        onClick={() => handleToggleMilestone(m.id)}
                        className={`cv-btn-milestone-toggle ${isCompleted ? "completed" : ""}`}
                      >
                        {isCompleted ? (
                          <>
                            <CheckCircle2 size={14} /> Milestone Completed
                          </>
                        ) : (
                          <>
                            <Circle size={14} /> Mark as Complete
                          </>
                        )}
                      </button>

                      <button
                        onClick={() => setActiveDrawerMilestone(m)}
                        className="cv-btn-inspect"
                      >
                        <BookOpen size={13} /> Inspect Syllabus & Tasks
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* 2. ROADMAP TECH TREE (INTERACTIVE DAG) */}
        {viewMode === "tree" && (
          <div data-testid="tree-view">
            <RoadmapTechTree
              missions={milestones}
              targetRole={activeRole}
              timeline={roadmapData?.estimated_timeline || `${milestones.length} Milestones`}
            />
          </div>
        )}

        {/* 3. CURRICULUM VIEW (STRUCTURED SYLLABUS LIST) */}
        {viewMode === "curriculum" && (
          <div className="cv-curriculum-list" data-testid="curriculum-view">
            {milestones.map((m) => {
              const isOpen = expandedCurriculumStages[m.stage];
              return (
                <div key={m.id || m.stage} className="cv-curriculum-card">
                  <div
                    className="cv-curriculum-header"
                    onClick={() => toggleCurriculumStage(m.stage)}
                  >
                    <div className="cv-curriculum-left">
                      <div className="cv-curriculum-stage-num">
                        {String(m.stage).padStart(2, "0")}
                      </div>
                      <div className="cv-curriculum-title-group">
                        <h3>{m.title}</h3>
                        <div style={{ fontSize: "0.8rem", color: "var(--cv-muted)" }}>
                          {m.category} • {m.estimated_effort}
                        </div>
                      </div>
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                      <span
                        className={`cv-skill-chip ${m.status === "completed" ? "verified" : ""}`}
                        style={{ textTransform: "capitalize" }}
                      >
                        {m.status.replace("_", " ")}
                      </span>
                      {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                    </div>
                  </div>

                  {isOpen && (
                    <div className="cv-curriculum-body">
                      <p style={{ fontSize: "0.9rem", color: "var(--cv-muted)", marginTop: 0 }}>
                        {m.description}
                      </p>

                      <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--cv-muted)" }}>
                        Measurable Completion Criteria:
                      </h4>
                      <ul className="cv-criteria-checklist">
                        {(m.completion_criteria || []).map((crit, idx) => (
                          <li key={idx} className="cv-criteria-item">
                            <CheckCircle2 size={16} style={{ color: m.status === "completed" ? "#16a34a" : "#94a3b8", marginTop: 2, flexShrink: 0 }} />
                            <span>{crit}</span>
                          </li>
                        ))}
                      </ul>

                      {m.practical_project && (
                        <div className="cv-milestone-project-box">
                          <div className="cv-project-box-header">
                            <Hammer size={13} /> Practical Project Deliverable
                          </div>
                          <p className="cv-project-box-title">{m.practical_project}</p>
                        </div>
                      )}

                      <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "1rem" }}>
                        <button
                          onClick={() => handleToggleMilestone(m.id)}
                          className={`cv-btn-milestone-toggle ${m.status === "completed" ? "completed" : ""}`}
                        >
                          {m.status === "completed" ? "Completed" : "Mark Complete"}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* ─── SECTION D: ROADMAP CHANGE HISTORY ──────────────────────────── */}
      <section className="cv-history-section" data-testid="change-history-section">
        <h3 className="cv-section-title">
          <Clock size={18} style={{ color: "var(--cv-accent)" }} />
          Roadmap Change History & Explanations
        </h3>
        <p className="cv-section-subtitle">
          Auditable timeline of accepted updates, completed milestones, and version promotions.
        </p>

        <div className="cv-history-timeline">
          {changeHistory.length > 0 ? (
            changeHistory.map((item) => (
              <div key={item.id} className="cv-history-entry">
                <div style={{ flex: 1, minWidth: "260px" }}>
                  <h4 className="cv-history-entry-title">{item.title}</h4>
                  <p className="cv-history-entry-why">{item.why_changed}</p>
                  {item.evidence_source && (
                    <div style={{ fontSize: "0.75rem", color: "var(--cv-muted)", marginTop: 4 }}>
                      Supported by: <strong>{item.evidence_source}</strong> ({item.evidence_date})
                    </div>
                  )}
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span className={`cv-history-status-badge ${item.status}`}>
                    {item.status}
                  </span>
                  <span style={{ fontSize: "0.75rem", color: "var(--cv-muted)" }}>
                    {item.created_at ? new Date(item.created_at).toLocaleDateString() : ""}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div style={{ fontSize: "0.85rem", color: "var(--cv-muted)", padding: "1rem 0" }}>
              Initial roadmap version active. Changes will be recorded as industry trends emerge and milestones complete.
            </div>
          )}
        </div>
      </section>

      {/* ─── MODAL: EVIDENCE INSPECTOR ──────────────────────────────────── */}
      {inspectingEvidence && (
        <div className="cv-modal-backdrop" onClick={() => setInspectingEvidence(null)}>
          <div className="cv-modal-box" onClick={(e) => e.stopPropagation()}>
            <div className="cv-modal-header">
              <h3 className="cv-modal-title">Verified Industry Evidence</h3>
              <button
                className="cv-modal-close-btn"
                onClick={() => setInspectingEvidence(null)}
              >
                <X size={18} />
              </button>
            </div>

            <div className="cv-evidence-meta-row">
              <strong>Technology:</strong>
              <span>{inspectingEvidence.technology || inspectingEvidence.title}</span>
            </div>

            <div className="cv-evidence-meta-row">
              <strong>Source:</strong>
              <span>{inspectingEvidence.source_name || inspectingEvidence.evidence_source}</span>
            </div>

            <div className="cv-evidence-meta-row">
              <strong>Observation Date:</strong>
              <span>{inspectingEvidence.publication_date || inspectingEvidence.evidence_date}</span>
            </div>

            <div className="cv-evidence-meta-row">
              <strong>Official Link:</strong>
              <a
                href={inspectingEvidence.source_url || inspectingEvidence.evidence_url}
                target="_blank"
                rel="noreferrer"
                style={{ display: "inline-flex", alignItems: "center", gap: "4px", color: "#2563eb", textDecoration: "underline" }}
              >
                Visit Source Documentation <ExternalLink size={12} />
              </a>
            </div>

            <div className="cv-evidence-meta-row">
              <strong>Reliability:</strong>
              <span>{inspectingEvidence.reliability || "Verified Official Standard"}</span>
            </div>

            <div style={{ marginTop: "1rem", background: "var(--cv-card-bg, #f8fafc)", padding: "1rem", borderRadius: "8px" }}>
              <strong style={{ fontSize: "0.8rem", color: "var(--cv-muted)", display: "block", marginBottom: "4px" }}>
                EVIDENCE SUMMARY & ANALYSIS:
              </strong>
              <p style={{ margin: 0, fontSize: "0.88rem", lineHeight: 1.5 }}>
                {inspectingEvidence.evidence_summary || inspectingEvidence.why_suggested}
              </p>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "1.5rem" }}>
              <button
                onClick={() => setInspectingEvidence(null)}
                className="cv-btn-accept"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ─── DRAWER: MILESTONE INSPECTOR ────────────────────────────────── */}
      {activeDrawerMilestone && (
        <div className="cv-drawer-backdrop" onClick={() => setActiveDrawerMilestone(null)}>
          <div className="cv-drawer-panel" onClick={(e) => e.stopPropagation()}>
            <div>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
                <span className="cv-milestone-category-badge">
                  Stage {activeDrawerMilestone.stage} • {activeDrawerMilestone.category}
                </span>
                <button
                  className="cv-modal-close-btn"
                  onClick={() => setActiveDrawerMilestone(null)}
                >
                  <X size={20} />
                </button>
              </div>

              <h2 style={{ fontSize: "1.4rem", fontWeight: 700, margin: "0 0 0.75rem", color: "var(--cv-text)" }}>
                {activeDrawerMilestone.title}
              </h2>

              <p style={{ fontSize: "0.92rem", color: "var(--cv-muted)", lineHeight: 1.5, margin: "0 0 1rem" }}>
                {activeDrawerMilestone.description}
              </p>

              {activeDrawerMilestone.why_recommended && (
                <div className="cv-milestone-why-box" style={{ marginBottom: "1.25rem" }}>
                  <strong>Why this milestone is recommended: </strong>
                  {activeDrawerMilestone.why_recommended}
                </div>
              )}

              {/* Practical Deliverable */}
              {activeDrawerMilestone.practical_project && (
                <div className="cv-milestone-project-box" style={{ marginBottom: "1.25rem" }}>
                  <div className="cv-project-box-header">
                    <Hammer size={14} /> Practical Project Deliverable
                  </div>
                  <p className="cv-project-box-title">{activeDrawerMilestone.practical_project}</p>
                </div>
              )}

              {/* Measurable Completion Criteria */}
              <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--cv-muted)", marginTop: "1.25rem" }}>
                Measurable Completion Criteria:
              </h4>
              <ul className="cv-criteria-checklist">
                {(activeDrawerMilestone.completion_criteria || []).map((crit, idx) => (
                  <li key={idx} className="cv-criteria-item">
                    <CheckCircle2
                      size={16}
                      style={{
                        color: activeDrawerMilestone.status === "completed" ? "#16a34a" : "#94a3b8",
                        marginTop: 2,
                        flexShrink: 0,
                      }}
                    />
                    <span>{crit}</span>
                  </li>
                ))}
              </ul>

              {/* Learning Resources */}
              {(activeDrawerMilestone.learning_resources || []).length > 0 && (
                <>
                  <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--cv-muted)", marginTop: "1.25rem" }}>
                    Recommended Documentation & Resources:
                  </h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                    {activeDrawerMilestone.learning_resources.map((res, i) => (
                      <a
                        key={i}
                        href={res.url}
                        target="_blank"
                        rel="noreferrer"
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "6px",
                          fontSize: "0.85rem",
                          color: "#0284c7",
                          textDecoration: "underline",
                        }}
                      >
                        <BookOpen size={14} />
                        {res.name}
                        <ExternalLink size={12} />
                      </a>
                    ))}
                  </div>
                </>
              )}
            </div>

            <div style={{ paddingTop: "1.5rem", borderTop: "1px solid var(--cv-border, #e2e8f0)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "0.82rem", color: "var(--cv-muted)" }}>
                Effort: {activeDrawerMilestone.estimated_effort}
              </span>
              <button
                onClick={() => handleToggleMilestone(activeDrawerMilestone.id)}
                className={`cv-btn-milestone-toggle ${activeDrawerMilestone.status === "completed" ? "completed" : ""}`}
              >
                {activeDrawerMilestone.status === "completed" ? "Mark as Incomplete" : "Mark as Completed"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ─── CHAPTER FOOTER NAVIGATION ───────────────────────────────────── */}
      <footer className="cv-chapter-footer" style={{ marginTop: "3rem" }}>
        <Link to={`/skill-gap?role=${encodeURIComponent(activeRole)}`}>
          <ArrowLeft size={12} /> Your Gaps
        </Link>
        <span>04 / 06</span>
        <Link to={`/ai/interview?role=${encodeURIComponent(activeRole)}`}>
          Cyra Vance &nbsp; 05 <ArrowRight size={12} />
        </Link>
      </footer>
    </div>
  );
}
