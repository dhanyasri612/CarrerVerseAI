import React, { useState, useEffect } from "react";
import {
  Code2,
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
  TrendingUp,
  X,
  Check,
  Zap,
  Monitor,
  Paintbrush,
  Smartphone,
  Cloud,
  ChevronRight,
} from "lucide-react";
import { recordActivity } from "../../services/activityTracker";

// Icons for central highway milestones
const CENTRAL_ICONS = [Server, Code2, Layers, Cpu, Database, Terminal, GitBranch];

export default function RoadmapTechTree({
  missions = [],
  targetRole = "Software Developer",
  timeline,
}) {
  const [selectedNode, setSelectedNode] = useState(null);
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
        if (next === "completed") {
          const mTitle = missions[idx]?.title || `Milestone ${idx + 1}`;
          recordActivity({
            type: "roadmap",
            title: `Completed Roadmap Milestone: ${mTitle}`,
            detail: `Progressed in ${targetRole} tech tree`,
            score: 2,
          });
        }
      } catch (e) {}
      return updated;
    });
  };

  const completedCount = missions.filter((_, i) => progressState[i] === "completed").length;
  const progressPercent = missions.length > 0 ? Math.round((completedCount / missions.length) * 100) : 0;

  // Supplementary branch domains (mirroring roadmap.sh side branches)
  const lateralBranches = [
    {
      id: "branch-frontend",
      title: "Client-Side Engineering",
      icon: Monitor,
      x: 180,
      y: 200,
      side: "left",
      desc: "Modern DOM architectures, responsive layouts, web performance, and state management.",
      skills: ["React", "TypeScript", "TailwindCSS", "Next.js"],
      task: "Build a fluid interactive dashboard with sub-100ms interaction latency.",
    },
    {
      id: "branch-uiux",
      title: "Design Systems & UI",
      icon: Paintbrush,
      x: 110,
      y: 330,
      side: "left",
      desc: "Visual hierarchy, micro-interactions, accessibility compliance (WCAG), and component libraries.",
      skills: ["Figma", "Design Tokens", "Accessibility", "Animation"],
      task: "Develop an accessible design system with atomic tokens and keyboard navigation.",
    },
    {
      id: "branch-mobile",
      title: "Mobile & Cross-Platform",
      icon: Smartphone,
      x: 620,
      y: 200,
      side: "right",
      desc: "Responsive touch interfaces, offline sync, native device APIs, and push architectures.",
      skills: ["React Native", "Mobile Optimization", "PWA", "Offline SQLite"],
      task: "Create a cross-platform progressive client that caches offline mutations.",
    },
    {
      id: "branch-cloud",
      title: "Cloud & Distributed Systems",
      icon: Cloud,
      x: 690,
      y: 330,
      side: "right",
      desc: "Containerization, CI/CD automated deployment, microservices, and observability.",
      skills: ["Docker", "Kubernetes", "AWS / GCP", "Prometheus"],
      task: "Set up automated GitHub Actions CI/CD with Docker container registry deployment.",
    },
  ];

  // Central spine nodes generated from candidate missions
  const centralNodes = missions.map((m, idx) => {
    const isFirst = idx === 0;
    const isHex = isFirst || idx === missions.length - 1;
    const IconComp = CENTRAL_ICONS[idx % CENTRAL_ICONS.length];
    const yPos = 180 + idx * 100;
    return {
      ...m,
      idx,
      isHex,
      IconComp,
      x: 400,
      y: yPos,
      isDone: progressState[idx] === "completed",
    };
  });

  const totalHeight = Math.max(760, 260 + centralNodes.length * 100);
  const flagY = 180 + centralNodes.length * 100;

  return (
    <div className="cv-techtree-root">
      {/* ─── TOP HEADER (ROADMAP.SH STYLE) ─────────────────────────────────── */}
      <div className="cv-techtree-header">
        <div className="cv-techtree-logo">
          <span className="logo-text">careerverse</span>
          <span className="logo-dot">.</span>
          <span className="logo-ext">ai</span>
        </div>
        <p className="cv-techtree-tagline">Plan what to learn next • Interactive Tech Tree</p>

        {/* PROGRESS PILL */}
        <div className="cv-techtree-progress-bar">
          <div className="cv-techtree-progress-track">
            <div
              className="cv-techtree-progress-glow"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <span className="cv-techtree-progress-label">
            <Zap size={13} style={{ color: "#fbbf24" }} />
            {completedCount} of {missions.length} Milestones Verified ({progressPercent}%)
          </span>
        </div>
      </div>

      {/* ─── DARK TECH-TREE CANVAS ────────────────────────────────────────── */}
      <div className="cv-techtree-canvas-wrapper">
        <svg
          className="cv-techtree-svg"
          viewBox={`0 0 800 ${totalHeight}`}
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            {/* NEON AMBER GLOW FILTER */}
            <filter id="neonGlow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="6" result="blur1" />
              <feGaussianBlur stdDeviation="14" result="blur2" />
              <feMerge>
                <feMergeNode in="blur2" />
                <feMergeNode in="blur1" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>

            {/* PEDESTAL SHADOW */}
            <filter id="hexDrop" x="-30%" y="-30%" width="160%" height="160%">
              <feDropShadow dx="0" dy="8" stdDeviation="12" floodColor="rgba(245, 158, 11, 0.35)" />
            </filter>

            {/* GRADIENT FOR CENTRAL ILLUMINATED HIGHWAY */}
            <linearGradient id="spineGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f59e0b" />
              <stop offset="50%" stopColor="#fbbf24" />
              <stop offset="100%" stopColor="#d97706" />
            </linearGradient>

            {/* CIRCUIT GRID PATTERN */}
            <pattern id="circuitGrid" width="40" height="40" patternUnits="userSpaceOnUse">
              <circle cx="20" cy="20" r="1" fill="rgba(255, 255, 255, 0.05)" />
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255, 255, 255, 0.02)" strokeWidth="0.5" />
            </pattern>
          </defs>

          {/* BACKGROUND CIRCUIT GRID */}
          <rect width="800" height={totalHeight} fill="url(#circuitGrid)" />

          {/* ─── LATERAL BRANCH CIRCUIT LINES (SLATE BLUE) ──────────────────── */}
          {/* Top branching splitter from Root to Left & Right channels */}
          <path
            d="M 400 120 L 400 135 L 180 135 L 180 170"
            stroke="#334155"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="180" cy="135" r="3.5" fill="#64748b" />

          <path
            d="M 180 135 L 110 135 L 110 300"
            stroke="#334155"
            strokeWidth="2"
            strokeDasharray="4 4"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="110" cy="135" r="3" fill="#64748b" />

          {/* Right lateral branching circuit */}
          <path
            d="M 400 120 L 400 135 L 620 135 L 620 170"
            stroke="#334155"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="620" cy="135" r="3.5" fill="#64748b" />

          <path
            d="M 620 135 L 690 135 L 690 300"
            stroke="#334155"
            strokeWidth="2"
            strokeDasharray="4 4"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="690" cy="135" r="3" fill="#64748b" />

          {/* Intermediate branch connectors from spine to nodes */}
          <path
            d="M 400 280 L 260 280 L 260 240 L 180 240"
            stroke="#1e293b"
            strokeWidth="2"
            strokeDasharray="5 5"
          />
          <circle cx="260" cy="280" r="3" fill="#475569" />

          <path
            d="M 400 380 L 540 380 L 540 240 L 620 240"
            stroke="#1e293b"
            strokeWidth="2"
            strokeDasharray="5 5"
          />
          <circle cx="540" cy="380" r="3" fill="#475569" />

          {/* ─── CENTRAL NEON SPINE (GOLDEN HIGHWAY) ────────────────────────── */}
          {/* Glowing under-blur */}
          <line
            x1="400"
            y1="100"
            x2="400"
            y2={flagY - 20}
            stroke="#f59e0b"
            strokeWidth="6"
            opacity="0.7"
            filter="url(#neonGlow)"
          />
          {/* Sharp core spine line */}
          <line
            x1="400"
            y1="100"
            x2="400"
            y2={flagY - 20}
            stroke="url(#spineGradient)"
            strokeWidth="3.5"
            strokeLinecap="round"
          />

          {/* ─── ROOT TOP HEXAGON NODE (</>) ───────────────────────────────── */}
          <g transform="translate(400, 60)" className="cv-techtree-root-hex">
            <polygon
              points="0,-32 28,-16 28,16 0,32 -28,16 -28,-16"
              fill="#0f172a"
              stroke="#fbbf24"
              strokeWidth="2.5"
              filter="url(#neonGlow)"
            />
            <polygon
              points="0,-30 26,-15 26,15 0,30 -26,15 -26,-15"
              fill="#1e293b"
              stroke="rgba(251, 191, 36, 0.4)"
              strokeWidth="1.5"
            />
            {/* Code symbol </> */}
            <text
              x="0"
              y="6"
              textAnchor="middle"
              fill="#fbbf24"
              fontSize="16"
              fontWeight="900"
              fontFamily="monospace"
            >
              &lt;/&gt;
            </text>
          </g>

          {/* ─── LATERAL BRANCH HEXAGONS (CLIENT / DESIGN / MOBILE / CLOUD) ─── */}
          {lateralBranches.map((br) => {
            const IconC = br.icon;
            const isSel = selectedNode?.id === br.id;
            return (
              <g
                key={br.id}
                transform={`translate(${br.x}, ${br.y})`}
                className="cv-techtree-branch-hex"
                onClick={() => setSelectedNode(br)}
                style={{ cursor: "pointer" }}
              >
                {/* Hexagon border */}
                <polygon
                  points="0,-26 23,-13 23,13 0,26 -23,13 -23,-13"
                  fill="#0f172a"
                  stroke={isSel ? "#fbbf24" : "#475569"}
                  strokeWidth="2"
                  filter={isSel ? "url(#neonGlow)" : "none"}
                />
                <polygon
                  points="0,-24 21,-12 21,12 0,24 -21,12 -21,-12"
                  fill="#1e293b"
                  stroke="rgba(255, 255, 255, 0.08)"
                  strokeWidth="1"
                />
                {/* Embedded Icon */}
                <foreignObject x="-12" y="-12" width="24" height="24" style={{ pointerEvents: "none" }}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: isSel ? "#fbbf24" : "#94a3b8",
                      width: "100%",
                      height: "100%",
                      pointerEvents: "none",
                    }}
                  >
                    <IconC size={16} />
                  </div>
                </foreignObject>

                {/* Hit area overlay for 100% click reliability */}
                <circle cx="0" cy="0" r="30" fill="transparent" cursor="pointer" pointerEvents="all" />

                {/* Branch Label below */}
                <text
                  x="0"
                  y="42"
                  textAnchor="middle"
                  fill="#94a3b8"
                  fontSize="10"
                  fontWeight="600"
                  letterSpacing="0.04em"
                  style={{ pointerEvents: "none" }}
                >
                  {br.title}
                </text>
              </g>
            );
          })}

          {/* ─── CENTRAL SPINE NODES (SEQUENTIAL CAREER PATH) ───────────────── */}
          {centralNodes.map((node) => {
            const IconComponent = node.IconComp;
            const isDone = node.isDone;
            const isSel = selectedNode?.idx === node.idx;

            return (
              <g
                key={node.idx}
                transform={`translate(${node.x}, ${node.y})`}
                className="cv-techtree-central-node"
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedNode(node);
                }}
                style={{ cursor: "pointer" }}
              >
                {/* Animated Selection Halo */}
                {isSel && (
                  <circle
                    r="36"
                    fill="none"
                    stroke="#fbbf24"
                    strokeWidth="2.5"
                    strokeDasharray="6 6"
                    filter="url(#neonGlow)"
                    className="cv-active-node-ring"
                  />
                )}

                {node.isHex ? (
                  // HEXAGON NODE (for Milestone 1 and Final Milestone)
                  <>
                    <polygon
                      points="0,-28 25,-14 25,14 0,28 -25,14 -25,-14"
                      fill="#0f172a"
                      stroke={isDone ? "#22c55e" : isSel ? "#fde047" : "#fbbf24"}
                      strokeWidth="2.5"
                      filter={isDone ? "none" : "url(#neonGlow)"}
                    />
                    <polygon
                      points="0,-26 23,-13 23,13 0,26 -23,13 -23,-13"
                      fill="#1e293b"
                      stroke="rgba(251, 191, 36, 0.3)"
                      strokeWidth="1"
                    />
                  </>
                ) : (
                  // CIRCULAR NODE (for middle milestones)
                  <>
                    <circle
                      r="25"
                      fill="#0f172a"
                      stroke={isDone ? "#22c55e" : isSel ? "#fde047" : "#fbbf24"}
                      strokeWidth="2.5"
                      filter={isDone ? "none" : "url(#neonGlow)"}
                    />
                    <circle
                      r="23"
                      fill="#1e293b"
                      stroke="rgba(251, 191, 36, 0.3)"
                      strokeWidth="1"
                    />
                  </>
                )}

                {/* Node Icon */}
                <foreignObject x="-12" y="-12" width="24" height="24" style={{ pointerEvents: "none" }}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: isDone ? "#22c55e" : "#fbbf24",
                      width: "100%",
                      height: "100%",
                      pointerEvents: "none",
                    }}
                  >
                    <IconComponent size={16} />
                  </div>
                </foreignObject>

                {/* Completed Badge Indicator */}
                {isDone && (
                  <circle
                    cx="18"
                    cy="-18"
                    r="8"
                    fill="#22c55e"
                    stroke="#0f172a"
                    strokeWidth="1.5"
                  />
                )}
                {isDone && (
                  <text
                    x="18"
                    y="-15"
                    textAnchor="middle"
                    fill="#ffffff"
                    fontSize="9"
                    fontWeight="800"
                    style={{ pointerEvents: "none" }}
                  >
                    ✓
                  </text>
                )}

                {/* Top Clickable Hit Area */}
                <circle cx="0" cy="0" r="32" fill="transparent" cursor="pointer" pointerEvents="all" />

                {/* Milestone Node Stage Text */}
                <text
                  x="0"
                  y="40"
                  textAnchor="middle"
                  fill="#e2e8f0"
                  fontSize="11"
                  fontWeight="700"
                  letterSpacing="0.02em"
                  style={{ pointerEvents: "none" }}
                >
                  {node.title.length > 22 ? `${node.title.slice(0, 20)}…` : node.title}
                </text>
              </g>
            );
          })}

          {/* ─── ISOMETRIC 3D LAPTOP (BOTTOM-LEFT ACCENT, MATCHING IMAGE 1) ─── */}
          <g transform={`translate(110, ${flagY - 60})`} className="cv-techtree-3d-laptop">
            {/* Screen base shadow */}
            <ellipse cx="60" cy="80" rx="50" ry="18" fill="rgba(0,0,0,0.4)" />
            {/* Laptop Screen housing */}
            <polygon
              points="15,10 85,0 95,50 25,60"
              fill="#1e293b"
              stroke="#475569"
              strokeWidth="2"
            />
            {/* Laptop Glass Screen */}
            <polygon
              points="20,14 80,5 88,46 28,55"
              fill="#090d16"
              stroke="#0f172a"
              strokeWidth="1"
            />
            {/* Colorful Syntax Highlighting Lines on Screen */}
            <line x1="28" y1="20" x2="55" y2="16" stroke="#f59e0b" strokeWidth="2.5" strokeLinecap="round" />
            <line x1="32" y1="28" x2="68" y2="23" stroke="#38bdf8" strokeWidth="2.5" strokeLinecap="round" />
            <line x1="32" y1="36" x2="78" y2="30" stroke="#4ade80" strokeWidth="2.5" strokeLinecap="round" />
            <line x1="36" y1="44" x2="62" y2="40" stroke="#f43f5e" strokeWidth="2.5" strokeLinecap="round" />
            {/* Laptop Keyboard Deck (trapezoid in isometric view) */}
            <polygon
              points="25,60 95,50 115,75 40,86"
              fill="#0f172a"
              stroke="#334155"
              strokeWidth="2"
            />
            {/* Trackpad */}
            <polygon
              points="60,70 82,67 86,76 64,79"
              fill="#1e293b"
              stroke="#475569"
              strokeWidth="1"
            />
          </g>

          {/* ─── ISOMETRIC 3D SERVERS & DATABASE (BOTTOM-RIGHT ACCENT) ─────── */}
          <g transform={`translate(640, ${flagY - 60})`} className="cv-techtree-3d-server">
            {/* Shadow under server rack and database */}
            <ellipse cx="40" cy="80" rx="45" ry="16" fill="rgba(0,0,0,0.4)" />
            {/* Server Blade 1 (top) */}
            <polygon points="0,15 45,0 75,12 30,27" fill="#334155" stroke="#475569" strokeWidth="1.5" />
            <polygon points="0,15 30,27 30,36 0,24" fill="#1e293b" stroke="#334155" strokeWidth="1.5" />
            <polygon points="30,27 75,12 75,21 30,36" fill="#0f172a" stroke="#334155" strokeWidth="1.5" />
            {/* LED blinking dots */}
            <circle cx="8" cy="20" r="1.5" fill="#4ade80" />
            <circle cx="14" cy="22" r="1.5" fill="#38bdf8" />

            {/* Server Blade 2 (middle) */}
            <polygon points="0,32 45,17 75,29 30,44" fill="#334155" stroke="#475569" strokeWidth="1.5" />
            <polygon points="0,32 30,44 30,53 0,41" fill="#1e293b" stroke="#334155" strokeWidth="1.5" />
            <polygon points="30,44 75,29 75,38 30,53" fill="#0f172a" stroke="#334155" strokeWidth="1.5" />
            <circle cx="8" cy="37" r="1.5" fill="#fbbf24" />
            <circle cx="14" cy="39" r="1.5" fill="#4ade80" />

            {/* Database Cylinder Disks (stacked below) */}
            <g transform="translate(10, 56)">
              {/* Cylinder 1 */}
              <ellipse cx="40" cy="10" rx="24" ry="9" fill="#38455c" stroke="#475569" strokeWidth="1.5" />
              <path d="M 16 10 A 24 9 0 0 0 64 10 L 64 18 A 24 9 0 0 1 16 18 Z" fill="#1e293b" stroke="#475569" strokeWidth="1.5" />
              {/* Cylinder 2 */}
              <ellipse cx="40" cy="20" rx="24" ry="9" fill="#38455c" stroke="#475569" strokeWidth="1.5" />
              <path d="M 16 20 A 24 9 0 0 0 64 20 L 64 28 A 24 9 0 0 1 16 28 Z" fill="#1e293b" stroke="#475569" strokeWidth="1.5" />
              <circle cx="24" cy="24" r="1.5" fill="#38bdf8" />
            </g>
          </g>

          {/* ─── ISOMETRIC 3D GOLDEN FLAG PEDESTAL (IMAGE 1 FINAL PLATEAU) ─── */}
          <g transform={`translate(400, ${flagY})`} className="cv-techtree-finish-plinth">
            {/* Glowing Plinth Underlight */}
            <ellipse cx="0" cy="22" rx="60" ry="24" fill="rgba(245, 158, 11, 0.4)" filter="url(#neonGlow)" />

            {/* 3D Isometric Golden Hexagonal Base (Top face) */}
            <polygon
              points="0,-16 48,0 48,22 0,38 -48,22 -48,0"
              fill="#eab308"
              stroke="#fef08a"
              strokeWidth="2.5"
              filter="url(#hexDrop)"
            />
            {/* Front Left Extruded Face */}
            <polygon
              points="-48,0 0,16 0,34 -48,18"
              fill="#ca8a04"
              stroke="#eab308"
              strokeWidth="1"
            />
            {/* Front Right Extruded Face */}
            <polygon
              points="0,16 48,0 48,18 0,34"
              fill="#a16207"
              stroke="#eab308"
              strokeWidth="1"
            />

            {/* Flagpole & Waving Flag (🚩) */}
            <line x1="0" y1="10" x2="0" y2="-28" stroke="#1f2937" strokeWidth="3" strokeLinecap="round" />
            <polygon
              points="0,-28 26,-20 0,-12"
              fill="#1e293b"
              stroke="#0f172a"
              strokeWidth="1.5"
            />
            <circle cx="0" cy="-28" r="3" fill="#eab308" />
          </g>
        </svg>

        {/* ─── SLIDE-OVER MILESTONE DOSSIER (OPENS ON NODE CLICK) ─────────── */}
        {selectedNode && (
          <aside className="cv-techtree-drawer">
            <div className="cv-techtree-drawer-header">
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span className="cv-techtree-drawer-badge">
                  {selectedNode.idx !== undefined ? `STAGE 0${selectedNode.idx + 1}` : "SPECIALIZATION"}
                </span>
                <span className="cv-techtree-drawer-role">{targetRole}</span>
              </div>
              <button
                type="button"
                className="cv-techtree-drawer-close"
                onClick={() => setSelectedNode(null)}
                aria-label="Close"
              >
                <X size={18} />
              </button>
            </div>

            <h3 className="cv-techtree-drawer-title">{selectedNode.title}</h3>
            {selectedNode.description && (
              <p className="cv-techtree-drawer-desc">{selectedNode.description}</p>
            )}
            {selectedNode.desc && !selectedNode.description && (
              <p className="cv-techtree-drawer-desc">{selectedNode.desc}</p>
            )}

            {/* STATUS TOGGLE */}
            {selectedNode.idx !== undefined && (
              <div className="cv-techtree-drawer-status-box">
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <TrendingUp size={16} style={{ color: "#fbbf24" }} />
                  <div>
                    <small>Milestone Status</small>
                    <strong>{progressState[selectedNode.idx] === "completed" ? "Verified Complete" : "In Progress"}</strong>
                  </div>
                </div>
                <button
                  type="button"
                  className={`cv-techtree-drawer-action-btn ${
                    progressState[selectedNode.idx] === "completed" ? "is-complete" : ""
                  }`}
                  onClick={() => toggleStageStatus(selectedNode.idx)}
                >
                  {progressState[selectedNode.idx] === "completed" ? (
                    <>
                      <CheckCircle2 size={16} /> Completed
                    </>
                  ) : (
                    <>
                      <Check size={16} /> Mark as Complete
                    </>
                  )}
                </button>
              </div>
            )}

            {/* LEARNING OBJECTIVES */}
            {Array.isArray(selectedNode.learning_objectives) && selectedNode.learning_objectives.length > 0 && (
              <div className="cv-techtree-drawer-section">
                <h4>
                  <BookOpen size={14} /> Learning Objectives
                </h4>
                <ul>
                  {selectedNode.learning_objectives.map((obj, i) => (
                    <li key={i}>{obj}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* TARGET COMPETENCIES */}
            {Array.isArray(selectedNode.skills) && selectedNode.skills.length > 0 && (
              <div className="cv-techtree-drawer-section">
                <h4>
                  <Sparkles size={14} /> Required Competencies
                </h4>
                <div className="cv-techtree-drawer-skills">
                  {selectedNode.skills.map((skill, i) => (
                    <span
                      key={i}
                      className="cv-techtree-drawer-pill"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* PRACTICAL PROJECT CAPSTONE */}
            {(selectedNode.practical_task || selectedNode.task) && (
              <div className="cv-techtree-drawer-section capstone">
                <h4>
                  <Hammer size={14} /> Practical Capstone Task
                </h4>
                <div className="cv-techtree-drawer-capstone-card">
                  <p>{selectedNode.practical_task || selectedNode.task}</p>
                </div>
              </div>
            )}
          </aside>
        )}
      </div>


    </div>
  );
}
