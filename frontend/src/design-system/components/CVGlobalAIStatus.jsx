import React, { useState, useRef, useEffect } from "react";
import { Sparkles, Activity, CheckCircle2, AlertCircle, Clock, ChevronRight } from "lucide-react";
import { useAIActivity } from "../../context/AIActivityContext";
import { CVAgentAvatar, AGENT_ROSTER } from "./CVAgentAvatar";
import { CVSignalDot } from "./CVBadge";

export function CVGlobalAIStatus() {
  const { status, statusText, activeAgent, activeStage, activityLog } = useAIActivity();
  const [isOpen, setIsOpen] = useState(false);
  const popoverRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  const isRunning = status === "running";

  return (
    <div style={{ position: "relative" }} ref={popoverRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="AI Career Team Status"
        title="View live AI agent activity"
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "0.5rem",
          padding: "0.375rem 0.75rem",
          borderRadius: "var(--cv-radius-full)",
          backgroundColor: isRunning ? "var(--cv-accent-soft)" : "var(--cv-surface-active)",
          border: isRunning ? "1px solid var(--cv-accent-border)" : "1px solid var(--cv-border)",
          color: isRunning ? "var(--cv-accent)" : "var(--cv-text)",
          fontSize: "0.8125rem",
          fontWeight: "600",
          cursor: "pointer",
          transition: "all var(--cv-dur-micro) var(--cv-ease-out)",
        }}
      >
        <CVSignalDot status={isRunning ? "running" : "ready"} pulse={isRunning} />
        <span style={{ maxWidth: "160px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {isRunning ? statusText : "AI Team · Ready"}
        </span>
      </button>

      {isOpen && (
        <div
          className="cv-ai-status-popover cv-animate-fade-scale"
          style={{
            position: "absolute",
            top: "calc(100% + 8px)",
            right: 0,
            width: "360px",
            backgroundColor: "var(--cv-surface)",
            border: "1px solid var(--cv-border)",
            borderRadius: "var(--cv-radius-lg)",
            boxShadow: "var(--cv-shadow-popover)",
            zIndex: "var(--cv-z-popover)",
            padding: "var(--cv-space-4)",
          }}
        >
          {/* Header */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "var(--cv-space-3)",
              paddingBottom: "var(--cv-space-2)",
              borderBottom: "1px solid var(--cv-border-subtle)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Sparkles size={16} color="var(--cv-accent)" />
              <span style={{ fontSize: "0.8125rem", fontWeight: "700", color: "var(--cv-text)" }}>
                AI Career Team Engine
              </span>
            </div>
            <span
              style={{
                fontSize: "0.6875rem",
                fontFamily: "var(--cv-font-mono)",
                color: isRunning ? "var(--cv-accent)" : "var(--cv-success)",
                fontWeight: "600",
              }}
            >
              {isRunning ? "● PROCESSING" : "● STANDBY"}
            </span>
          </div>

          {/* Active Agents Strip */}
          <div style={{ marginBottom: "var(--cv-space-4)" }}>
            <div
              style={{
                fontSize: "0.6875rem",
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: "var(--cv-text-muted)",
                marginBottom: "0.5rem",
                fontWeight: "600",
              }}
            >
              Orchestrated Agents
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "0.375rem" }}>
              {Object.entries(AGENT_ROSTER).map(([key, agent]) => {
                const isActive = activeAgent === key;
                return (
                  <div
                    key={key}
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      padding: "0.5rem 0.25rem",
                      borderRadius: "var(--cv-radius-sm)",
                      backgroundColor: isActive ? "var(--cv-accent-soft)" : "var(--cv-bg-subtle)",
                      border: isActive ? "1px solid var(--cv-accent-border)" : "1px solid transparent",
                      textAlign: "center",
                    }}
                  >
                    <CVAgentAvatar agentKey={key} state={isActive ? "speaking" : "idle"} size={24} showRings={false} />
                    <span
                      style={{
                        fontSize: "0.6875rem",
                        fontWeight: "600",
                        color: "var(--cv-text)",
                        marginTop: "0.25rem",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        maxWidth: "90%",
                      }}
                    >
                      {agent.shortName}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Activity Log */}
          <div>
            <div
              style={{
                fontSize: "0.6875rem",
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: "var(--cv-text-muted)",
                marginBottom: "0.5rem",
                fontWeight: "600",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <span>Recent Signal Executions</span>
              <Activity size={12} />
            </div>

            <div
              style={{
                maxHeight: "160px",
                overflowY: "auto",
                display: "flex",
                flexDirection: "column",
                gap: "0.375rem",
              }}
            >
              {activityLog.map((log) => (
                <div
                  key={log.id}
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: "0.5rem",
                    padding: "0.375rem 0.5rem",
                    borderRadius: "4px",
                    backgroundColor: "var(--cv-bg-subtle)",
                    fontSize: "0.75rem",
                  }}
                >
                  <span
                    style={{
                      fontFamily: "var(--cv-font-mono)",
                      fontSize: "0.6875rem",
                      color: "var(--cv-text-faint)",
                      marginTop: "1px",
                    }}
                  >
                    {log.timestamp}
                  </span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: "600", color: "var(--cv-text)" }}>{log.agent}</div>
                    <div style={{ color: "var(--cv-text-muted)", fontSize: "0.6875rem" }}>
                      {log.message}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
