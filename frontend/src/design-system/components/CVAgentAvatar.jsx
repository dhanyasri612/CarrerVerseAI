import React from "react";

export const AGENT_ROSTER = {
  profile: {
    name: "Career Profile Analyst",
    shortName: "Profile Analyst",
    role: "Candidate Evidence & Synthesis",
    color: "#6366F1",
    glow: "rgba(99, 102, 241, 0.3)",
    code: "CPA",
  },
  navigator: {
    name: "Career Navigator",
    shortName: "Navigator",
    role: "Role Matching & Discovery",
    color: "#38BDF8",
    glow: "rgba(56, 189, 248, 0.3)",
    code: "NAV",
  },
  skillgap: {
    name: "Skill Gap Analyst",
    shortName: "Gap Analyst",
    role: "Taxonomy & Requirement Scoring",
    color: "#F59E0B",
    glow: "rgba(245, 158, 11, 0.3)",
    code: "SGA",
  },
  pathfinder: {
    name: "Career Pathfinder",
    shortName: "Pathfinder",
    role: "Sequential Milestones & Missions",
    color: "#10B981",
    glow: "rgba(16, 185, 129, 0.3)",
    code: "CPF",
  },
  cyra: {
    name: "Dr. Cyra Vance",
    shortName: "Cyra Vance",
    role: "Lead Technical Evaluator & Principal Mentor",
    color: "#6366F1",
    glow: "rgba(99, 102, 241, 0.4)",
    code: "CYR",
  },
  alex: {
    name: "Dr. Cyra Vance",
    shortName: "Cyra Vance",
    role: "Lead Technical Evaluator & Principal Mentor",
    color: "#6366F1",
    glow: "rgba(99, 102, 241, 0.4)",
    code: "CYR",
  },
  intelligence: {
    name: "Career Intelligence Core",
    shortName: "Intelligence",
    role: "Multi-Agent Synthesis Report",
    color: "#EC4899",
    glow: "rgba(236, 72, 153, 0.3)",
    code: "CIC",
  },
};

export function CVAgentAvatar({
  agentKey = "alex",
  state = "idle", // 'idle' | 'listening' | 'speaking' | 'thinking' | 'evaluating' | 'error'
  size = 48,
  showRings = true,
  className = "",
}) {
  const agent = AGENT_ROSTER[agentKey] || AGENT_ROSTER.alex;

  const getStateColors = () => {
    switch (state) {
      case "listening":
        return { ring: "var(--cv-success)", pulse: true, label: "Listening" };
      case "speaking":
        return { ring: "var(--cv-accent)", pulse: true, label: "Speaking" };
      case "thinking":
      case "evaluating":
        return { ring: "var(--cv-warning)", pulse: true, label: "Thinking" };
      case "error":
        return { ring: "var(--cv-danger)", pulse: false, label: "Error" };
      case "idle":
      default:
        return { ring: agent.color, pulse: false, label: "Ready" };
    }
  };

  const stateConfig = getStateColors();

  return (
    <div
      className={`cv-agent-avatar cv-agent-avatar--${state} ${className}`}
      style={{
        position: "relative",
        width: `${size}px`,
        height: `${size}px`,
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        flexShrink: 0,
      }}
    >
      {/* Outer subtle glow/pulse ring */}
      {showRings && (
        <div
          style={{
            position: "absolute",
            inset: "-4px",
            borderRadius: "50%",
            border: `1.5px solid ${stateConfig.ring}`,
            opacity: state === "idle" ? 0.4 : 0.9,
            animation: stateConfig.pulse ? "cv-pulse-glow 1.5s infinite var(--cv-ease-out)" : "none",
            transition: "all var(--cv-dur-standard) var(--cv-ease-out)",
          }}
        />
      )}

      {/* Orbiting orb or soundwave backdrop */}
      <div
        style={{
          width: "100%",
          height: "100%",
          borderRadius: "50%",
          background: `radial-gradient(circle at 35% 30%, ${agent.color} 0%, #171B26 90%)`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#FFFFFF",
          fontWeight: "700",
          fontSize: `${Math.max(10, Math.floor(size * 0.28))}px`,
          fontFamily: "var(--cv-font-mono)",
          letterSpacing: "0.05em",
          boxShadow: `0 2px 10px ${agent.glow}`,
          position: "relative",
          overflow: "hidden",
        }}
      >
        {state === "speaking" ? (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "2px",
              height: "40%",
            }}
          >
            <span style={{ width: "2px", background: "#fff", animation: "cv-wave-bar 0.8s infinite 0.1s" }} />
            <span style={{ width: "2px", background: "#fff", animation: "cv-wave-bar 0.8s infinite 0.3s" }} />
            <span style={{ width: "2px", background: "#fff", animation: "cv-wave-bar 0.8s infinite 0.2s" }} />
            <span style={{ width: "2px", background: "#fff", animation: "cv-wave-bar 0.8s infinite 0.4s" }} />
          </div>
        ) : state === "thinking" || state === "evaluating" ? (
          <div
            style={{
              width: "55%",
              height: "55%",
              borderRadius: "50%",
              border: "2px dashed #FFFFFF",
              animation: "cv-orbit-slow 2s linear infinite",
            }}
          />
        ) : (
          <span>{agent.code}</span>
        )}
      </div>
    </div>
  );
}

export function CVAgentStatus({
  agentKey = "alex",
  state = "idle",
  customText,
  onClick,
}) {
  const agent = AGENT_ROSTER[agentKey] || AGENT_ROSTER.alex;

  const stateLabels = {
    idle: "Ready",
    running: "Analyzing...",
    listening: "Listening...",
    speaking: "Speaking...",
    thinking: "Thinking...",
    evaluating: "Evaluating answer...",
    completed: "Ready",
    error: "Service error",
  };

  const displayText = customText || stateLabels[state] || "Ready";

  return (
    <div
      onClick={onClick}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "0.5rem",
        padding: "0.3rem 0.65rem",
        borderRadius: "var(--cv-radius-full)",
        backgroundColor: "var(--cv-surface-active)",
        border: "1px solid var(--cv-border)",
        cursor: onClick ? "pointer" : "default",
        fontSize: "0.75rem",
        color: "var(--cv-text)",
        fontWeight: "500",
      }}
    >
      <CVAgentAvatar agentKey={agentKey} state={state} size={18} showRings={false} />
      <span style={{ fontWeight: "600", color: "var(--cv-text)" }}>{agent.shortName}</span>
      <span style={{ color: "var(--cv-text-muted)" }}>·</span>
      <span
        style={{
          color: state === "running" || state === "listening" || state === "speaking" ? "var(--cv-accent)" : "var(--cv-text-muted)",
          fontFamily: "var(--cv-font-sans)",
        }}
      >
        {displayText}
      </span>
    </div>
  );
}
