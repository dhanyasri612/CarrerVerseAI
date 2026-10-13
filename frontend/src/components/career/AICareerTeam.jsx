import React from "react";
import { ArrowRight, Sparkles } from "lucide-react";
import { AGENT_ROSTER, CVAgentAvatar } from "../../design-system/components/CVAgentAvatar";
import { useAIActivity } from "../../context/AIActivityContext";
import { useNavigate } from "react-router-dom";

const TEAM_PIPELINE = [
  { key: "profile", path: "/profile" },
  { key: "navigator", path: "/career-discovery" },
  { key: "skillgap", path: "/skill-gap" },
  { key: "pathfinder", path: "/career-roadmap" },
  { key: "alex", path: "/ai/interview" },
  { key: "intelligence", path: "/ai/intelligence" },
];

export function AICareerTeam() {
  const { activeAgent } = useAIActivity();
  const navigate = useNavigate();

  return (
    <div
      className="cv-ai-team-strip"
      style={{
        padding: "var(--cv-space-6)",
        backgroundColor: "var(--cv-surface)",
        borderRadius: "var(--cv-radius-lg)",
        border: "1px solid var(--cv-border)",
        boxShadow: "var(--cv-shadow-sm)",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "var(--cv-space-5)",
          flexWrap: "wrap",
          gap: "0.5rem",
        }}
      >
        <div>
          <span className="cv-eyebrow">
            <Sparkles size={12} /> Multi-Agent Orchestration
          </span>
          <h3 className="cv-headline" style={{ margin: "0.25rem 0 0 0" }}>
            The AI Career Team Working for You
          </h3>
        </div>
        <span style={{ fontSize: "0.75rem", color: "var(--cv-text-muted)" }}>
          Connected across LangGraph & Vector Memory
        </span>
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "0.5rem",
          overflowX: "auto",
          paddingBottom: "0.5rem",
        }}
      >
        {TEAM_PIPELINE.map((item, index) => {
          const agent = AGENT_ROSTER[item.key];
          const isRunning = activeAgent === item.key;

          return (
            <React.Fragment key={item.key}>
              <div
                onClick={() => navigate(item.path)}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  minWidth: "120px",
                  padding: "0.75rem 0.5rem",
                  borderRadius: "var(--cv-radius-md)",
                  backgroundColor: isRunning ? "var(--cv-accent-soft)" : "var(--cv-bg-subtle)",
                  border: isRunning ? "1px solid var(--cv-accent-border)" : "1px solid transparent",
                  cursor: "pointer",
                  transition: "all var(--cv-dur-micro) var(--cv-ease-out)",
                  textAlign: "center",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "var(--cv-surface-active)")}
                onMouseLeave={(e) =>
                  (e.currentTarget.style.backgroundColor = isRunning ? "var(--cv-accent-soft)" : "var(--cv-bg-subtle)")
                }
              >
                <CVAgentAvatar agentKey={item.key} state={isRunning ? "speaking" : "idle"} size={36} />
                <span
                  style={{
                    fontSize: "0.75rem",
                    fontWeight: "700",
                    color: "var(--cv-text)",
                    marginTop: "0.5rem",
                    lineHeight: "1.2",
                  }}
                >
                  {agent.shortName}
                </span>
                <span
                  style={{
                    fontSize: "0.6875rem",
                    color: "var(--cv-text-muted)",
                    marginTop: "0.2rem",
                    lineHeight: "1.2",
                  }}
                >
                  {agent.role.split(" ")[0]}
                </span>
              </div>

              {index < TEAM_PIPELINE.length - 1 && (
                <div style={{ color: "var(--cv-border-strong)", flexShrink: 0 }}>
                  <ArrowRight size={16} />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
