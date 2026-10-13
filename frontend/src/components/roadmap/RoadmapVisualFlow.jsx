import React, { useState, useEffect } from "react";
import {
  Code,
  Server,
  Database,
  Layers,
  GitBranch,
  Cpu,
  Terminal,
  Flag,
  Sparkles,
  CheckCircle2,
  Circle,
  Clock,
  BookOpen,
  Hammer,
  ChevronRight,
  TrendingUp,
  MapPin,
  Check,
  Zap,
} from "lucide-react";

const STAGE_ICONS = [Code, Server, GitBranch, Database, Layers, Cpu, Terminal];

export default function RoadmapVisualFlow({ missions = [], targetRole = "Software Developer", timeline }) {
  const [selectedStageIndex, setSelectedStageIndex] = useState(0);
  const [progressState, setProgressState] = useState(() => {
    try {
      const saved = localStorage.getItem(`cv_roadmap_progress_${targetRole}`);
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });

  useEffect(() => {
    try {
      const saved = localStorage.getItem(`cv_roadmap_progress_${targetRole}`);
      setProgressState(saved ? JSON.parse(saved) : {});
    } catch {
      setProgressState({});
    }
  }, [targetRole]);

  const toggleStageStatus = (idx) => {
    setProgressState((prev) => {
      const current = prev[idx] || (idx === 0 ? "in_progress" : "pending");
      const next = current === "completed" ? "pending" : "completed";
      const updated = { ...prev, [idx]: next };
      try {
        localStorage.setItem(`cv_roadmap_progress_${targetRole}`, JSON.stringify(updated));
      } catch (e) {}
      return updated;
    });
  };

  const completedCount = missions.filter((_, i) => progressState[i] === "completed").length;
  const progressPercent = missions.length > 0 ? Math.round((completedCount / missions.length) * 100) : 0;

  const activeMission = missions[selectedStageIndex] || missions[0] || null;

  return (
    <div className="cv-roadmap-flow-wrapper">
      {/* ─── WAYPOINT PROGRESS BAR (INSPIRED BY ROADMAP WAYPOINTS) ─────────── */}
      <div className="cv-roadmap-flow-waypoint-bar">
        <div className="cv-roadmap-waypoint-header">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <MapPin size={16} style={{ color: "var(--cv-accent, #c9933b)" }} />
            <span style={{ fontWeight: 600, fontSize: "0.9rem", letterSpacing: "0.02em" }}>
              Trajectory to {targetRole}
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "12px", fontSize: "0.85rem" }}>
            <span style={{ color: "var(--cv-muted)" }}>
              {completedCount} of {missions.length} milestones completed
            </span>
            <span className="cv-roadmap-progress-badge">
              <Zap size={12} style={{ color: "#eab308" }} />
              {progressPercent}% Complete
            </span>
          </div>
        </div>

        <div className="cv-roadmap-waypoint-track">
          <div className="cv-roadmap-waypoint-line">
            <div
              className="cv-roadmap-waypoint-fill"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <div className="cv-roadmap-waypoint-pins">
            {missions.map((m, idx) => {
              const isDone = progressState[idx] === "completed";
              const isSelected = selectedStageIndex === idx;
              return (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setSelectedStageIndex(idx)}
                  className={`cv-roadmap-waypoint-pin ${isDone ? "completed" : ""} ${isSelected ? "selected" : ""}`}
                  title={m.title}
                >
                  <span className="cv-pin-dot">
                    {isDone ? <Check size={11} strokeWidth={3} /> : idx + 1}
                  </span>
                  <span className="cv-pin-label">{`Stage 0${idx + 1}`}</span>
                </button>
              );
            })}
            <div className="cv-roadmap-waypoint-pin finish-pin">
              <span className="cv-pin-dot finish-dot">
                <Flag size={12} />
              </span>
              <span className="cv-pin-label">Goal</span>
            </div>
          </div>
        </div>
      </div>

      {/* ─── MAIN ROADMAP.SH TREE FLOW CANVAS & DETAIL INSPECTOR ───────────── */}
      <div className="cv-roadmap-flow-layout">
        {/* LEFT / CENTER: VISUAL CONNECTED TREE */}
        <div className="cv-roadmap-flow-tree">
          {/* ROOT ENTRY NODE */}
          <div className="cv-roadmap-root-node">
            <div className="cv-roadmap-node-hex root-hex">
              <Code size={18} />
            </div>
            <div className="cv-roadmap-root-label">
              <span className="cv-root-badge">START</span>
              <strong>{targetRole} Learning Highway</strong>
            </div>
          </div>

          {/* CONNECTING STEM */}
          <div className="cv-roadmap-spine-stem top-stem" />

          {/* STAGE MILESTONES WITH SATELLITE BRANCHES */}
          {missions.map((mission, idx) => {
            const isDone = progressState[idx] === "completed";
            const isSelected = selectedStageIndex === idx;
            const IconComponent = STAGE_ICONS[idx % STAGE_ICONS.length] || Code;
            const isEven = idx % 2 === 0;

            return (
              <React.Fragment key={idx}>
                {/* VERTICAL STEM BETWEEN HUBS */}
                {idx > 0 && <div className="cv-roadmap-spine-stem" />}

                <div
                  className={`cv-roadmap-stage-container ${isEven ? "branch-right" : "branch-left"} ${
                    isSelected ? "stage-selected" : ""
                  } ${isDone ? "stage-done" : ""}`}
                >
                  {/* CENTRAL HUB CONNECTOR ON SPINE */}
                  <div
                    className="cv-roadmap-hub"
                    onClick={() => setSelectedStageIndex(idx)}
                  >
                    <div className={`cv-roadmap-hub-circle ${isDone ? "done" : isSelected ? "active" : ""}`}>
                      <IconComponent size={18} />
                      {isDone && (
                        <span className="cv-hub-check">
                          <Check size={10} strokeWidth={3} />
                        </span>
                      )}
                    </div>
                    <span className="cv-roadmap-hub-number">
                      {String(idx + 1).padStart(2, "0")}
                    </span>
                  </div>

                  {/* HORIZONTAL CONNECTOR BEAM */}
                  <div className="cv-roadmap-branch-beam" />

                {/* MILESTONE CARD ON BRANCH */}
                <div
                  className={`cv-roadmap-node-card ${isSelected ? "active-card" : ""} ${isDone ? "done-card" : ""}`}
                  onClick={() => setSelectedStageIndex(idx)}
                >
                  <div className="cv-roadmap-card-header">
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <span className="cv-roadmap-card-badge">STAGE {String(idx + 1).padStart(2, "0")}</span>
                      {mission.estimated_effort && (
                        <span className="cv-roadmap-card-time">
                          <Clock size={11} /> {mission.estimated_effort}
                        </span>
                      )}
                    </div>
                    <button
                      type="button"
                      className={`cv-stage-toggle-btn ${isDone ? "is-complete" : ""}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleStageStatus(idx);
                      }}
                      title={isDone ? "Mark as in-progress" : "Mark as completed"}
                    >
                      {isDone ? (
                        <>
                          <CheckCircle2 size={13} style={{ color: "#16a34a" }} />
                          Completed
                        </>
                      ) : (
                        <>
                          <Circle size={13} />
                          Mark Done
                        </>
                      )}
                    </button>
                  </div>

                  <h3 className="cv-roadmap-card-title">{mission.title}</h3>
                  {mission.description && (
                    <p className="cv-roadmap-card-desc">{mission.description}</p>
                  )}

                  {/* BRANCHING SATELLITE SKILL PILLS */}
                  {Array.isArray(mission.skills) && mission.skills.length > 0 && (
                    <div className="cv-roadmap-card-skills">
                      {mission.skills.slice(0, 4).map((sk, sIdx) => (
                        <span key={sIdx} className="cv-roadmap-skill-pill">
                          <Sparkles size={10} /> {sk}
                        </span>
                      ))}
                      {mission.skills.length > 4 && (
                        <span className="cv-roadmap-skill-pill more-pill">
                          +{mission.skills.length - 4} more
                        </span>
                      )}
                    </div>
                  )}

                  {/* PRACTICAL CAPSTONE CALLOUT */}
                  {mission.practical_task && (
                    <div className="cv-roadmap-card-capstone">
                      <Hammer size={13} className="capstone-icon" />
                      <div>
                        <strong>Hands-On Milestone:</strong>
                        <span>{mission.practical_task}</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </React.Fragment>
          );
        })}

          {/* STEM TO FINISH */}
          <div className="cv-roadmap-spine-stem bottom-stem" />

          {/* FINAL DESTINATION FLAG (LIKE ROADMAP.SH FINAL PLATEAU) */}
          <div className="cv-roadmap-finish-node">
            <div className="cv-roadmap-finish-pedestal">
              <div className="cv-roadmap-flag-icon">
                <Flag size={20} />
              </div>
            </div>
            <div className="cv-roadmap-finish-label">
              <span className="cv-finish-badge">DESTINATION</span>
              <strong>{targetRole} Production Readiness</strong>
              <p>All core milestones verified with portfolio artifacts</p>
            </div>
          </div>
        </div>

        {/* RIGHT: INTERACTIVE MILESTONE INSPECTOR PANEL */}
        {activeMission && (
          <aside className="cv-roadmap-inspector-panel">
            <div className="cv-inspector-header">
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span className="cv-inspector-kicker">MILESTONE DOSSIER</span>
                <span className="cv-inspector-index">STAGE {String(selectedStageIndex + 1).padStart(2, "0")}</span>
              </div>
              <h2 className="cv-inspector-title">{activeMission.title}</h2>
              {activeMission.description && (
                <p className="cv-inspector-desc">{activeMission.description}</p>
              )}
            </div>

            <div className="cv-inspector-meta-row">
              <div className="cv-inspector-meta-item">
                <Clock size={14} style={{ color: "var(--cv-accent)" }} />
                <div>
                  <small>Effort Estimate</small>
                  <strong>{activeMission.estimated_effort || "2–3 weeks"}</strong>
                </div>
              </div>
              <div className="cv-inspector-meta-item">
                <TrendingUp size={14} style={{ color: "var(--cv-accent)" }} />
                <div>
                  <small>Status</small>
                  <strong>{progressState[selectedStageIndex] === "completed" ? "Completed" : "In Progress"}</strong>
                </div>
              </div>
            </div>

            {/* ACTION TOGGLE */}
            <button
              type="button"
              className={`cv-inspector-action-btn ${progressState[selectedStageIndex] === "completed" ? "completed" : ""}`}
              onClick={() => toggleStageStatus(selectedStageIndex)}
            >
              {progressState[selectedStageIndex] === "completed" ? (
                <>
                  <CheckCircle2 size={16} /> Milestone Completed
                </>
              ) : (
                <>
                  <Check size={16} /> Mark Milestone as Complete
                </>
              )}
            </button>

            {/* LEARNING OBJECTIVES */}
            {Array.isArray(activeMission.learning_objectives) && activeMission.learning_objectives.length > 0 && (
              <div className="cv-inspector-section">
                <h4 className="cv-inspector-section-title">
                  <BookOpen size={13} /> Learning Objectives
                </h4>
                <ul className="cv-inspector-objectives-list">
                  {activeMission.learning_objectives.map((obj, i) => (
                    <li key={i}>{obj}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* REQUIRED SKILLS TAXONOMY */}
            {Array.isArray(activeMission.skills) && activeMission.skills.length > 0 && (
              <div className="cv-inspector-section">
                <h4 className="cv-inspector-section-title">
                  <Sparkles size={13} /> Target Competencies
                </h4>
                <div className="cv-inspector-skills-grid">
                  {activeMission.skills.map((skill, i) => (
                    <span key={i} className="cv-inspector-skill-tag">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* PRACTICAL CAPSTONE PROJECT */}
            {activeMission.practical_task && (
              <div className="cv-inspector-section capstone-section">
                <h4 className="cv-inspector-section-title">
                  <Hammer size={13} /> Practical Project Deliverable
                </h4>
                <div className="cv-inspector-capstone-card">
                  <p>{activeMission.practical_task}</p>
                </div>
              </div>
            )}
          </aside>
        )}
      </div>
    </div>
  );
}
