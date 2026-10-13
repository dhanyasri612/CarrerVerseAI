import React, { useState, useEffect } from "react";
import {
  MapPin,
  Flag,
  Check,
  CheckCircle2,
  Circle,
  Clock,
  Sparkles,
  Hammer,
  BookOpen,
  TrendingUp,
  Zap,
  Compass,
} from "lucide-react";

const PIN_COLORS = [
  { bg: "#ef4444", border: "#dc2626", text: "#ffffff", label: "Red" },     // Red (like image 2)
  { bg: "#10b981", border: "#059669", text: "#ffffff", label: "Green" },   // Green (like image 2)
  { bg: "#0ea5e9", border: "#0284c7", text: "#ffffff", label: "Blue" },    // Blue (like image 2)
  { bg: "#8b5cf6", border: "#7c3aed", text: "#ffffff", label: "Purple" },  // Purple
  { bg: "#f59e0b", border: "#d97706", text: "#ffffff", label: "Amber" },   // Amber
  { bg: "#ec4899", border: "#db2777", text: "#ffffff", label: "Pink" },    // Pink
];

export default function RoadmapWindingHighway({
  missions = [],
  targetRole = "Software Developer",
  timeline,
}) {
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

  // Geometry calculations for winding serpentine S-curve highway
  const width = 760;
  const startY = 80;
  const stageSpacing = 210;
  const totalStages = missions.length;
  const endY = startY + (totalStages + 1) * stageSpacing;
  const svgHeight = endY + 90;

  // Calculate coordinates for each waypoint bend
  const waypoints = missions.map((mission, idx) => {
    const isEven = idx % 2 === 0;
    // Even stages curve to the right (x = 510), odd stages curve to the left (x = 250)
    const x = isEven ? 510 : 250;
    const y = startY + (idx + 1) * stageSpacing;
    const pinColor = PIN_COLORS[idx % PIN_COLORS.length];
    return {
      mission,
      idx,
      x,
      y,
      isEven,
      pinColor,
    };
  });

  // Generate smooth cubic Bézier road path string
  let roadPathD = `M 380 ${startY} `;
  let prevX = 380;
  let prevY = startY;

  waypoints.forEach((wp) => {
    const midY = (prevY + wp.y) / 2;
    roadPathD += `C ${prevX} ${midY}, ${wp.x} ${midY}, ${wp.x} ${wp.y} `;
    prevX = wp.x;
    prevY = wp.y;
  });

  // Connect last waypoint to final destination finish flag
  const goalX = 380;
  const goalY = endY;
  const finalMidY = (prevY + goalY) / 2;
  roadPathD += `C ${prevX} ${finalMidY}, ${goalX} ${finalMidY}, ${goalX} ${goalY}`;

  return (
    <div className="cv-roadmap-highway-wrapper">
      {/* ─── WAYPOINT PROGRESS BAR ─────────────────────────────────────────── */}
      <div className="cv-roadmap-flow-waypoint-bar">
        <div className="cv-roadmap-waypoint-header">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Compass size={18} style={{ color: "var(--cv-accent, #c9933b)" }} />
            <span style={{ fontWeight: 600, fontSize: "0.92rem", letterSpacing: "0.02em" }}>
              Serpentine Highway to {targetRole}
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "12px", fontSize: "0.85rem" }}>
            <span style={{ color: "var(--cv-muted)" }}>
              {completedCount} of {missions.length} waypoints reached
            </span>
            <span className="cv-roadmap-progress-badge">
              <Zap size={12} style={{ color: "#eab308" }} />
              {progressPercent}% Journey Complete
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
                  <span className="cv-pin-label">{`Waypoint 0${idx + 1}`}</span>
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

      {/* ─── HIGHWAY CANVAS & INSPECTOR LAYOUT ─────────────────────────────── */}
      <div className="cv-roadmap-flow-layout">
        {/* LEFT / CENTER: WINDING ASPHALT ROAD */}
        <div className="cv-roadmap-highway-canvas">
          <svg
            className="cv-highway-svg"
            viewBox={`0 0 ${width} ${svgHeight}`}
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <filter id="roadShadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="6" stdDeviation="8" floodColor="rgba(0,0,0,0.18)" />
              </filter>
              <filter id="pinShadow" x="-30%" y="-30%" width="160%" height="160%">
                <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="rgba(0,0,0,0.25)" />
              </filter>
              <linearGradient id="roadAsphalt" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#334155" />
                <stop offset="50%" stopColor="#1e293b" />
                <stop offset="100%" stopColor="#0f172a" />
              </linearGradient>
            </defs>

            {/* ROAD BED (SHOULDER OUTLINE) */}
            <path
              d={roadPathD}
              stroke="#64748b"
              strokeWidth="74"
              strokeLinecap="round"
              strokeLinejoin="round"
              filter="url(#roadShadow)"
            />

            {/* ASPHALT PAVEMENT */}
            <path
              d={roadPathD}
              stroke="url(#roadAsphalt)"
              strokeWidth="64"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* WHITE DASHED CENTER DIVIDER (LIKE IMAGE 2) */}
            <path
              d={roadPathD}
              stroke="#f8fafc"
              strokeWidth="3.5"
              strokeLinecap="butt"
              strokeLinejoin="round"
              strokeDasharray="12 12"
              opacity="0.9"
            />

            {/* START BANNER AT TOP OF HIGHWAY */}
            <g transform={`translate(380, ${startY - 35})`}>
              <rect
                x="-80"
                y="-18"
                width="160"
                height="34"
                rx="17"
                fill="#1e293b"
                stroke="#475569"
                strokeWidth="2"
              />
              <text
                x="0"
                y="4"
                textAnchor="middle"
                fill="#f8fafc"
                fontSize="12"
                fontWeight="700"
                letterSpacing="0.06em"
              >
                🏁 HIGHWAY START
              </text>
            </g>

            {/* FINISH DESTINATION PLATEAU AT BOTTOM */}
            <g transform={`translate(${goalX}, ${goalY + 25})`}>
              <rect
                x="-100"
                y="-18"
                width="200"
                height="40"
                rx="20"
                fill="linear-gradient(135deg, #eab308, #ca8a04)"
                stroke="#fef08a"
                strokeWidth="2.5"
                filter="url(#pinShadow)"
              />
              <text
                x="0"
                y="6"
                textAnchor="middle"
                fill="#1f1d1a"
                fontSize="13"
                fontWeight="800"
                letterSpacing="0.04em"
              >
                🚩 GOAL: READY FOR HIRE
              </text>
            </g>

            {/* WAYPOINT PINS ON ROAD BENDS */}
            {waypoints.map((wp) => {
              const isDone = progressState[wp.idx] === "completed";
              const isSelected = selectedStageIndex === wp.idx;
              const { bg, border } = wp.pinColor;

              return (
                <g
                  key={wp.idx}
                  className="cv-svg-pin-group"
                  transform={`translate(${wp.x}, ${wp.y})`}
                  onClick={() => setSelectedStageIndex(wp.idx)}
                  style={{ cursor: "pointer" }}
                >
                  {/* PULSING SELECTION RING */}
                  {isSelected && (
                    <circle
                      r="32"
                      fill="none"
                      stroke={bg}
                      strokeWidth="2.5"
                      opacity="0.6"
                      strokeDasharray="4 4"
                    />
                  )}

                  {/* 3D TEARDROP MAP PIN (EXACTLY MATCHING IMAGE 2) */}
                  <g filter="url(#pinShadow)" transform="translate(0, -28)">
                    {/* Outer Teardrop Pin Shape */}
                    <path
                      d="M 0 0 C -16 -16, -20 -28, -20 -38 A 20 20 0 1 1 20 -38 C 20 -28, 16 -16, 0 0 Z"
                      fill={isDone ? "#16a34a" : bg}
                      stroke={isDone ? "#15803d" : border}
                      strokeWidth="2"
                    />
                    {/* Inner White Circle */}
                    <circle cx="0" cy="-38" r="10" fill="#ffffff" />
                    {/* Number or Checkmark inside pin */}
                    {isDone ? (
                      <path
                        d="M -5 -38 L -2 -35 L 5 -42"
                        fill="none"
                        stroke="#16a34a"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    ) : (
                      <text
                        x="0"
                        y="-34"
                        textAnchor="middle"
                        fill="#1f2937"
                        fontSize="10"
                        fontWeight="800"
                      >
                        {wp.idx + 1}
                      </text>
                    )}
                  </g>
                </g>
              );
            })}
          </svg>

          {/* DOCKED CARDS FLOATING BESIDE EACH ROAD BEND */}
          <div className="cv-highway-docked-cards">
            {waypoints.map((wp) => {
              const isDone = progressState[wp.idx] === "completed";
              const isSelected = selectedStageIndex === wp.idx;
              const cardTop = wp.y - 70;

              return (
                <div
                  key={wp.idx}
                  className={`cv-highway-dock-card ${wp.isEven ? "dock-left" : "dock-right"} ${
                    isSelected ? "active-dock" : ""
                  } ${isDone ? "done-dock" : ""}`}
                  style={{ top: `${cardTop}px` }}
                  onClick={() => setSelectedStageIndex(wp.idx)}
                >
                  <div className="cv-highway-dock-header">
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <span
                        className="cv-highway-dock-badge"
                        style={{ background: isDone ? "#16a34a" : wp.pinColor.bg }}
                      >
                        WAYPOINT 0{wp.idx + 1}
                      </span>
                      {wp.mission.estimated_effort && (
                        <span className="cv-roadmap-card-time">
                          <Clock size={11} /> {wp.mission.estimated_effort}
                        </span>
                      )}
                    </div>
                    <button
                      type="button"
                      className={`cv-stage-toggle-btn ${isDone ? "is-complete" : ""}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleStageStatus(wp.idx);
                      }}
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

                  <h3 className="cv-roadmap-card-title">{wp.mission.title}</h3>
                  {wp.mission.description && (
                    <p className="cv-roadmap-card-desc">{wp.mission.description}</p>
                  )}

                  {/* SATELLITE COMPETENCY PILLS */}
                  {Array.isArray(wp.mission.skills) && wp.mission.skills.length > 0 && (
                    <div className="cv-roadmap-card-skills">
                      {wp.mission.skills.slice(0, 3).map((sk, sIdx) => (
                        <span key={sIdx} className="cv-roadmap-skill-pill">
                          <Sparkles size={10} /> {sk}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* PRACTICAL CAPSTONE CALLOUT */}
                  {wp.mission.practical_task && (
                    <div className="cv-roadmap-card-capstone">
                      <Hammer size={12} className="capstone-icon" />
                      <div>
                        <strong>Milestone Task:</strong>
                        <span>{wp.mission.practical_task}</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* RIGHT: INTERACTIVE MILESTONE INSPECTOR PANEL */}
        {activeMission && (
          <aside className="cv-roadmap-inspector-panel">
            <div className="cv-inspector-header">
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span className="cv-inspector-kicker">WAYPOINT DOSSIER</span>
                <span className="cv-inspector-index">WAYPOINT 0{selectedStageIndex + 1}</span>
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
                  <CheckCircle2 size={16} /> Waypoint Completed
                </>
              ) : (
                <>
                  <Check size={16} /> Mark Waypoint as Complete
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
