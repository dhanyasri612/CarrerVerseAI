import React, { useEffect, useState } from "react";
import { Link, useLocation, useSearchParams } from "react-router-dom";
import { ArrowRight, ArrowLeft, Activity, CheckCircle2, Circle, Sparkles, Network, ListOrdered, GitBranch } from "lucide-react";
import { getApiError } from "../services/api";
import { getLearningRoadmap } from "../services/careerService";
import { LoadingState, ErrorState } from "../components/AsyncState";
import RoadmapTechTree from "../components/roadmap/RoadmapTechTree";
import RoadmapVisualFlow from "../components/roadmap/RoadmapVisualFlow";

const DEFAULT_ROLES = [
  "Full Stack Developer",
  "Software Developer",
  "Data Scientist",
  "Machine Learning Engineer",
  "Frontend Developer",
  "Backend Developer",
  "UI/UX Designer",
  "AI & NLP Engineer",
];

export default function LearningRoadmapPage() {
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();

  const queryRole = searchParams.get("role");
  const stateRole = location.state?.targetRole;
  const storedRole = typeof window !== "undefined" ? sessionStorage.getItem("careerverse_target_role") : null;
  const activeRole = queryRole || stateRole || storedRole || "Full Stack Developer";

  const [data,        setData]        = useState(null);
  const [loading,     setLoading]     = useState(true);
  const [error,       setError]       = useState("");
  const [viewMode,    setViewMode]    = useState("techtree"); // "techtree" | "highway" | "editorial"

  const discoveredRoles = React.useMemo(() => {
    try {
      const stored = sessionStorage.getItem("careerverse_discovered_roles");
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }, []);

  const availableRoles = React.useMemo(() => {
    const list = [...discoveredRoles, activeRole, ...DEFAULT_ROLES].filter(Boolean);
    return Array.from(new Set(list));
  }, [discoveredRoles, activeRole]);

  const load = async (roleToLoad) => {
    const target = roleToLoad || activeRole;
    setLoading(true);
    setError("");
    try {
      const res = await getLearningRoadmap(target);
      setData(res);
    } catch (err) {
      setError(getApiError(err, `Unable to load roadmap for ${target}.`));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(activeRole);
  }, [activeRole]);

  const handleRoleSelect = (roleName) => {
    if (roleName === activeRole && !error && !loading) return;
    sessionStorage.setItem("careerverse_target_role", roleName);
    setSearchParams({ role: roleName });
  };

  const rawMissions = Array.isArray(data?.roadmap)
    ? data.roadmap
    : Array.isArray(data?.learning_roadmap)
    ? data.learning_roadmap
    : Array.isArray(data?.phases)
    ? data.phases
    : Array.isArray(data?.missions)
    ? data.missions
    : Array.isArray(data?.stages)
    ? data.stages
    : Array.isArray(data)
    ? data
    : (data?.roadmap?.missions || data?.roadmap?.phases || data?.roadmap?.steps || data?.roadmap?.stages || []);

  const missions = rawMissions.map((m, idx) => {
    const title = m.title || m.name || m.phase || `Stage ${m.stage || idx + 1}`;
    const desc  = m.description || m.goal || m.objective || "";

    let tasks = m.tasks || [];
    if (!tasks.length) {
      const list = [];
      if (m.practical_task) {
        list.push({ title: m.practical_task, type: "Practical Project", status: "Hands-on" });
      }
      if (Array.isArray(m.learning_objectives)) {
        m.learning_objectives.forEach(obj => list.push({ title: obj, type: "Learning Objective", status: "Concept" }));
      }
      if (Array.isArray(m.skills)) {
        m.skills.forEach(s => list.push({ title: s, type: "Target Skill", status: "Core" }));
      }
      tasks = list;
    }

    return {
      ...m,
      title,
      description: desc,
      reason: m.reason || (m.estimated_effort ? `Estimated effort: ${m.estimated_effort}` : null),
      tasks,
    };
  });

  const targetRole = data?.target_role || data?.goal || activeRole;
  const timeline   = data?.estimated_timeline || data?.timeline || data?.duration || (missions.length > 0 ? `${missions.length} Progressive Stages` : null);

  if (loading && !data) return <LoadingState label={`Generating learning journey for ${activeRole}…`} />;
  if (error && !data)   return <ErrorState message={error} onRetry={() => load(activeRole)} />;

  return (
    <div>
      {/* ─── CHAPTER INTRO ───────────────────────────────────────────────── */}
      <header className="cv-chapter-intro">
        <span className="cv-chapter-number">04 / 06</span>
        <div>
          <div className="cv-chapter-kicker">04 &nbsp; / &nbsp; Your Journey</div>
          <h1 className="cv-chapter-title">Not a timeline.<br /><span className="serif">A series of meaningful moves.</span></h1>
          <p className="cv-chapter-deck">
            Your journey can be a set of missions shaped around a real goal: why it matters,
            what you already know, what to learn, and what to make or practice next.
          </p>
        </div>
        <p className="cv-intro-aside">
          {activeRole ? `Current goal: ${activeRole}` : "Set a direction in Career Navigator to ground your journey."}
          {timeline && <><br /><br />Estimated timeline: {timeline}</>}
        </p>
      </header>

      {/* ─── DIRECTION SELECTOR ─────────────────────────────────────────── */}
      <section className="cv-editorial-section" style={{ borderBottom: "1px solid var(--cv-rule, rgba(0,0,0,0.08))", paddingBottom: "1.25rem" }}>
        <div className="cv-section-index">TARGET DIRECTION</div>
        <div className="cv-section-content">
          <p style={{ margin: "0 0 0.75rem", fontSize: "var(--cv-text-body-sm)", color: "var(--cv-muted)" }}>
            Select a target direction to build a customized mission sequence for:
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", alignItems: "center" }}>
            {availableRoles.map((roleName) => {
              const isActive = roleName.toLowerCase() === activeRole.toLowerCase();
              return (
                <button
                  key={roleName}
                  onClick={() => handleRoleSelect(roleName)}
                  disabled={loading}
                  style={{
                    cursor: loading ? "wait" : "pointer",
                    padding: "7px 16px",
                    borderRadius: "20px",
                    border: isActive ? "1.5px solid var(--cv-ink, #1f1d1a)" : "1px solid var(--cv-rule, #dcd7ce)",
                    background: isActive ? "var(--cv-ink, #1f1d1a)" : "transparent",
                    color: isActive ? "#faf7f2" : "var(--cv-ink, #1f1d1a)",
                    fontSize: "0.85rem",
                    fontWeight: isActive ? 600 : 400,
                    transition: "all 0.15s ease",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  {isActive && <Sparkles size={13} />}
                  {roleName}
                </button>
              );
            })}
          </div>
          {loading && (
            <p style={{ color: "var(--cv-muted)", fontSize: "0.82rem", marginTop: "0.5rem" }}>
              Synthesizing learning missions for {activeRole}…
            </p>
          )}
        </div>
      </section>

      {/* ─── ROADMAP VIEW MODE TOGGLE ─────────────────────────────────── */}
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        margin: "1.25rem 0 0.5rem",
        padding: "0.5rem 0",
        borderBottom: "1px solid var(--cv-rule, rgba(0,0,0,0.06))",
        flexWrap: "wrap",
        gap: "1rem"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ fontSize: "0.75rem", fontWeight: 700, letterSpacing: "0.06em", color: "var(--cv-muted)" }}>
            ROADMAP STYLE:
          </span>
          <div style={{
            display: "inline-flex",
            background: "rgba(0, 0, 0, 0.04)",
            padding: "3px",
            borderRadius: "10px",
            border: "1px solid var(--cv-rule, rgba(0,0,0,0.08))"
          }}>
            <button
              type="button"
              onClick={() => setViewMode("techtree")}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                padding: "6px 14px",
                borderRadius: "8px",
                border: "none",
                background: viewMode === "techtree" ? "#0f172a" : "transparent",
                color: viewMode === "techtree" ? "#fbbf24" : "var(--cv-muted, #787570)",
                fontWeight: viewMode === "techtree" ? 600 : 400,
                fontSize: "0.82rem",
                cursor: "pointer",
                boxShadow: viewMode === "techtree" ? "0 2px 6px rgba(0,0,0,0.2)" : "none",
                transition: "all 0.15s ease",
              }}
            >
              <Network size={14} style={{ color: viewMode === "techtree" ? "#fbbf24" : "inherit" }} />
              roadmap.sh Tech Tree
            </button>
            <button
              type="button"
              onClick={() => setViewMode("pipeline")}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                padding: "6px 14px",
                borderRadius: "8px",
                border: "none",
                background: viewMode === "pipeline" ? "#0284c7" : "transparent",
                color: viewMode === "pipeline" ? "#ffffff" : "var(--cv-muted, #787570)",
                fontWeight: viewMode === "pipeline" ? 600 : 400,
                fontSize: "0.82rem",
                cursor: "pointer",
                boxShadow: viewMode === "pipeline" ? "0 2px 6px rgba(2, 132, 199, 0.3)" : "none",
                transition: "all 0.15s ease",
              }}
            >
              <GitBranch size={14} style={{ color: viewMode === "pipeline" ? "#ffffff" : "inherit" }} />
              Pipeline Flowchart
            </button>
            <button
              type="button"
              onClick={() => setViewMode("editorial")}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                padding: "6px 14px",
                borderRadius: "8px",
                border: "none",
                background: viewMode === "editorial" ? "var(--cv-surface, #ffffff)" : "transparent",
                color: viewMode === "editorial" ? "var(--cv-ink, #1f1d1a)" : "var(--cv-muted, #787570)",
                fontWeight: viewMode === "editorial" ? 600 : 400,
                fontSize: "0.82rem",
                cursor: "pointer",
                boxShadow: viewMode === "editorial" ? "0 1px 4px rgba(0,0,0,0.08)" : "none",
                transition: "all 0.15s ease",
              }}
            >
              <ListOrdered size={14} />
              Curriculum Guide
            </button>
          </div>
        </div>
        <div style={{ fontSize: "0.8rem", color: "var(--cv-muted)" }}>
          {missions.length} Progressive Milestones • 3 Visual Representations
        </div>
      </div>

      <div style={{ opacity: loading ? 0.45 : 1, pointerEvents: loading ? "none" : "auto", transition: "opacity 0.25s ease" }}>
        {missions.length > 0 ? (
          viewMode === "techtree" ? (
            <RoadmapTechTree
              missions={missions}
              targetRole={targetRole || activeRole}
              timeline={timeline}
            />
          ) : viewMode === "pipeline" ? (
            <RoadmapVisualFlow
              missions={missions}
              targetRole={targetRole || activeRole}
              timeline={timeline}
            />
          ) : (
            <>
              {/* ─── ROADMAP META ────────────────────────────────────────────────── */}
              {(targetRole || timeline) && (
                <section className="cv-editorial-section">
                  <div className="cv-section-index">FIELD GUIDE</div>
                  <div className="cv-section-content">
                    <h2>Your career field guide.</h2>
                    <p>A roadmap links a real intention to a concrete action. Each mission below builds on the last.</p>
                    <div className="cv-evidence-lines">
                      {targetRole && <div className="cv-evidence-line"><strong>Target direction</strong><span>{targetRole}</span></div>}
                      {timeline   && <div className="cv-evidence-line"><strong>Estimated timeline</strong><span>{timeline}</span></div>}
                      {missions.length > 0 && <div className="cv-evidence-line"><strong>Total missions</strong><span>{missions.length}</span></div>}
                    </div>
                  </div>
                </section>
              )}

              {/* ─── EDITORIAL MISSIONS ────────────────────────────────────────── */}
              {missions.map((mission, idx) => {
                const title      = mission.title || mission.name || mission.phase || `Mission ${idx + 1}`;
                const desc       = mission.description || mission.objective || "";
                const tasks      = mission.tasks || mission.resources || mission.steps || [];
                const completed  = mission.completed || mission.status === "completed";
                const isCurrent  = mission.status === "current" || mission.status === "in_progress";
                return (
                  <section className="cv-editorial-section" key={idx}>
                    <div className="cv-section-index" style={{ display: "flex", alignItems: "flex-start", gap: "0.5rem" }}>
                      {completed
                        ? <CheckCircle2 size={14} style={{ color: "var(--cv-success)", marginTop: 1 }} />
                        : <Circle size={14} style={{ marginTop: 1, opacity: isCurrent ? 1 : 0.4 }} />
                      }
                      MISSION {String(idx + 1).padStart(2, "0")}
                    </div>
                    <div className="cv-section-content">
                      <h2>{title}</h2>
                      {desc && <p>{desc}</p>}
                      {mission.reason && (
                        <div className="cv-note-block"><Activity size={16} /><div><strong>Why this.</strong>{mission.reason}</div></div>
                      )}
                      {tasks.length > 0 && (
                        <div className="cv-evidence-lines">
                          {tasks.map((t, i) => (
                            <div className="cv-evidence-line" key={i}>
                              <strong>{typeof t === "string" ? t : (t.title || t.task || t.name)}</strong>
                              <span>{t.type || t.resource_type || t.status || ""}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </section>
                );
              })}
            </>
          )
        ) : (
          <section className="cv-editorial-section">
            <div className="cv-section-index">A FIELD GUIDE</div>
            <div className="cv-section-content">
              <h2>Not a timeline. A series of meaningful moves.</h2>
              <p>Your journey can be a set of missions shaped around a real goal—but personal missions are unavailable until profile and career data are connected.</p>
              <div className="cv-note-block">
                <Activity size={16} />
                <div><strong>Not yet grounded.</strong> Select a target direction above, or explore directions in Career Navigator.</div>
              </div>
              <div className="cv-action-row">
                <Link to="/career-discovery" className="cv-opening-cta">
                  Open Career Navigator <ArrowRight size={14} />
                </Link>
              </div>
            </div>
          </section>
        )}
      </div>

      <footer className="cv-chapter-footer">
        <Link to={`/skill-gap?role=${encodeURIComponent(targetRole || activeRole)}`}><ArrowLeft size={12} /> Your Gaps</Link>
        <span>04 / 06</span>
        <Link to={`/ai/interview?role=${encodeURIComponent(targetRole || activeRole)}`}>Cyra Vance &nbsp; 05 <ArrowRight size={12} /></Link>
      </footer>
    </div>
  );
}
