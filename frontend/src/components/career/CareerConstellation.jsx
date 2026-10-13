import React, { useState } from "react";
import {
  Code,
  FolderGit2,
  Briefcase,
  GitBranch,
  MapPin,
  TrendingUp,
  Video,
  Sparkles,
  Award,
  Zap,
} from "lucide-react";
import { CVDrawer } from "../../design-system/components/CVDrawer";
import { CVBadge } from "../../design-system/components/CVBadge";
import { CVButton } from "../../design-system/components/CVButton";
import { useNavigate } from "react-router-dom";

export function CareerConstellation({ profile, stats = {} }) {
  const [selectedNode, setSelectedNode] = useState(null);
  const navigate = useNavigate();

  const skillsCount = stats.skillsCount || profile?.unified_skills?.length || 0;
  const projectsCount = stats.projectsCount || profile?.projects?.length || 0;
  const experiencesCount = stats.experiencesCount || profile?.experience?.length || 0;
  const isGithubConnected = Boolean(profile?.github_summary?.connected);
  const hasResume = Boolean(profile?.resume_summary?.uploaded);

  const nodes = [
    {
      id: "skills",
      label: "Verified Skills",
      value: `${skillsCount} skills`,
      icon: Code,
      angle: 0,
      radius: 135,
      color: "#6366F1",
      detailTitle: "Aggregated Skill Taxonomy",
      detailDesc: `You have ${skillsCount} skills extracted from your resume, GitHub repositories, and verified assessments.`,
      actionLabel: "View Skill Taxonomy",
      actionPath: "/profile",
    },
    {
      id: "projects",
      label: "Projects & Code",
      value: `${projectsCount} projects`,
      icon: FolderGit2,
      angle: 52,
      radius: 145,
      color: "#38BDF8",
      detailTitle: "Project Evidence Gallery",
      detailDesc: `Connected evidence spans ${projectsCount} repositories and parsed project descriptions with technology breakdown.`,
      actionLabel: "Explore Projects",
      actionPath: "/profile",
    },
    {
      id: "experience",
      label: "Work History",
      value: `${experiencesCount} roles`,
      icon: Briefcase,
      angle: 105,
      radius: 130,
      color: "#10B981",
      detailTitle: "Professional Experience",
      detailDesc: `${experiencesCount} verified career roles contributing to your domain seniority signals.`,
      actionLabel: "Manage Experience",
      actionPath: "/profile",
    },
    {
      id: "github",
      label: "GitHub Sync",
      value: isGithubConnected ? "Connected" : "Connect Repo",
      icon: GitBranch,
      angle: 160,
      radius: 140,
      color: "#F59E0B",
      detailTitle: "GitHub Source Verification",
      detailDesc: isGithubConnected
        ? "Active GitHub link providing real repository commits and language distributions."
        : "Connect your GitHub account to automatically verify programming evidence.",
      actionLabel: isGithubConnected ? "View Profile Signals" : "Connect GitHub",
      actionPath: "/profile",
    },
    {
      id: "discovery",
      label: "Career Directions",
      value: "Explore Roles",
      icon: MapPin,
      angle: 215,
      radius: 150,
      color: "#8B5CF6",
      detailTitle: "Career Navigator Engine",
      detailDesc: "Matches your real evidence against industry role requirements using semantic embeddings and Neo4j graph.",
      actionLabel: "Launch Career Navigator",
      actionPath: "/career-discovery",
    },
    {
      id: "gaps",
      label: "Skill Gaps",
      value: "Target Analysis",
      icon: TrendingUp,
      angle: 265,
      radius: 135,
      color: "#EC4899",
      detailTitle: "Skill Gap Matrix",
      detailDesc: "Identifies demonstrated, developing, and priority skills for your target career direction.",
      actionLabel: "Open Skill Gap Matrix",
      actionPath: "/skill-gap",
    },
    {
      id: "interview",
      label: "Cyra Vance Interview",
      value: "AI Practice Room",
      icon: Video,
      angle: 315,
      radius: 140,
      color: "#06B6D4",
      detailTitle: "Virtual AI Interviewer & Senior Mentor",
      detailDesc: "Interactive technical interview room proctored by Dr. Cyra Vance, grounded in your real projects.",
      actionLabel: "Enter Interview Room",
      actionPath: "/ai/interview",
    },
  ];

  return (
    <div
      className="cv-constellation-container"
      style={{
        position: "relative",
        width: "100%",
        maxWidth: "460px",
        height: "380px",
        margin: "0 auto",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* Orbital Background Rings */}
      <svg
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          pointerEvents: "none",
        }}
        viewBox="0 0 460 380"
      >
        <circle
          cx="230"
          cy="190"
          r="80"
          fill="none"
          stroke="var(--cv-border-subtle)"
          strokeWidth="1"
          strokeDasharray="4 4"
        />
        <circle
          cx="230"
          cy="190"
          r="140"
          fill="none"
          stroke="var(--cv-border-subtle)"
          strokeWidth="1"
        />
        {/* Radiating lines from center to nodes */}
        {nodes.map((node) => {
          const rad = (node.angle * Math.PI) / 180;
          const x = 230 + Math.cos(rad) * node.radius;
          const y = 190 + Math.sin(rad) * (node.radius * 0.78);
          return (
            <line
              key={node.id}
              x1="230"
              y1="190"
              x2={x}
              y2={y}
              stroke="var(--cv-border)"
              strokeWidth="1"
              strokeDasharray="2 3"
            />
          );
        })}
      </svg>

      {/* Center "YOU" Node */}
      <div
        style={{
          position: "absolute",
          width: "68px",
          height: "68px",
          borderRadius: "50%",
          backgroundColor: "var(--cv-surface)",
          border: "2px solid var(--cv-accent)",
          boxShadow: "0 0 20px var(--cv-glow)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 5,
          cursor: "pointer",
        }}
        onClick={() => navigate("/profile")}
        title="Your Verified Career Core"
      >
        <Sparkles size={16} color="var(--cv-accent)" />
        <span
          style={{
            fontFamily: "var(--cv-font-sans)",
            fontSize: "0.75rem",
            fontWeight: "800",
            letterSpacing: "0.05em",
            color: "var(--cv-text)",
            marginTop: "2px",
          }}
        >
          YOU
        </span>
      </div>

      {/* Orbiting Satellite Nodes */}
      {nodes.map((node) => {
        const rad = (node.angle * Math.PI) / 180;
        const left = 230 + Math.cos(rad) * node.radius - 20;
        const top = 190 + Math.sin(rad) * (node.radius * 0.78) - 20;
        const Icon = node.icon;

        return (
          <div
            key={node.id}
            onClick={() => setSelectedNode(node)}
            style={{
              position: "absolute",
              left: `${left}px`,
              top: `${top}px`,
              width: "40px",
              height: "40px",
              borderRadius: "50%",
              backgroundColor: "var(--cv-surface)",
              border: `1.5px solid ${node.color}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              boxShadow: "var(--cv-shadow-sm)",
              zIndex: 4,
              transition: "transform var(--cv-dur-micro) var(--cv-ease-out), box-shadow var(--cv-dur-micro) var(--cv-ease-out)",
            }}
            title={`${node.label}: ${node.value}`}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "scale(1.15)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "scale(1)";
            }}
          >
            <Icon size={16} color={node.color} />
          </div>
        );
      })}

      {/* Contextual Signal Drawer */}
      <CVDrawer
        isOpen={Boolean(selectedNode)}
        onClose={() => setSelectedNode(null)}
        title={selectedNode?.detailTitle}
        subtitle={selectedNode?.label}
      >
        {selectedNode && (
          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            <div
              style={{
                padding: "var(--cv-space-4)",
                backgroundColor: "var(--cv-bg-subtle)",
                borderRadius: "var(--cv-radius-md)",
                border: "1px solid var(--cv-border-subtle)",
              }}
            >
              <div style={{ fontSize: "0.875rem", fontWeight: "600", color: "var(--cv-text)", marginBottom: "0.25rem" }}>
                Current Signal Value
              </div>
              <div style={{ fontFamily: "var(--cv-font-mono)", fontSize: "1.25rem", color: "var(--cv-accent)", fontWeight: "700" }}>
                {selectedNode.value}
              </div>
            </div>

            <p style={{ color: "var(--cv-text-muted)", fontSize: "0.875rem", lineHeight: "1.6" }}>
              {selectedNode.detailDesc}
            </p>

            <CVButton
              variant="primary"
              onClick={() => {
                navigate(selectedNode.actionPath);
                setSelectedNode(null);
              }}
            >
              {selectedNode.actionLabel} →
            </CVButton>
          </div>
        )}
      </CVDrawer>
    </div>
  );
}
