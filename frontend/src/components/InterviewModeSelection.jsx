import React, { useState, useMemo, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Sparkles,
  Layers,
  History,
  Code2,
  ChevronDown,
  CheckCircle2,
  GitBranch,
  Bot,
  Volume2,
  RotateCcw,
  Clock,
  ShieldCheck,
  Zap,
  Target,
  FileText,
  ArrowRight,
  Globe,
  ArrowLeft,
  MessageSquare,
  Award,
} from "lucide-react";

const SUPPORTED_LANGUAGES = [
  { code: "en", label: "English" },
  { code: "ta", label: "Tamil (தமிழ் / Tanglish)" },
  { code: "hi", label: "Hindi (हिन्दी / Hinglish)" },
  { code: "te", label: "Telugu (తెలుగు)" },
  { code: "kn", label: "Kannada (ಕನ್ನಡ)" },
  { code: "es", label: "Spanish (Español)" },
  { code: "fr", label: "French (Français)" },
  { code: "de", label: "German (Deutsch)" },
];

export default function InterviewModeSelection({
  candidateName = "Dhanyasri K",
  resourceMeta = null,
  loading = false,
  onStartInterview = () => {},
  onOpenHistory = () => {},
  renderQuestionHistoryModal = () => null,
  availableVoices = [],
  selectedVoiceURI = "",
  onSelectVoice = () => {},
  speechRate = 1.0,
  onChangeSpeechRate = () => {},
  onTestVoice = () => {},
}) {
  const [selectedTrackId, setSelectedTrackId] = useState("dsa");
  const [targetRole, setTargetRole] = useState("Software Engineer (SDE)");
  const [selectedLang, setSelectedLang] = useState("en");
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [isTestingVoice, setIsTestingVoice] = useState(false);

  // Connected resources extraction
  const conn = resourceMeta?.connected_resources || {};
  const hrProfile = conn.hackerrank;
  const lcProfile = conn.leetcode;
  const ghProfile = conn.github;
  const ghRepos = ghProfile?.repositories || [];
  const certsList = conn.certifications || [];
  const skillsList = conn.skills || [];

  const lcSolved = lcProfile?.total_solved || 0;
  const hrSolved = hrProfile?.total_solved || 0;

  // Synthesize interview tracks strictly from connected resources
  const availableTracks = useMemo(() => {
    const tracks = [];

    // 1. LeetCode Connected Track
    if (lcSolved > 0 || lcProfile?.connected) {
      tracks.push({
        id: "dsa",
        title: "LeetCode Algorithmic Problem Solving",
        badge: "⚡ LeetCode Connected",
        role: "Software Engineer (SDE / Algorithms)",
        color: "#ea580c",
        bg: "#fff7ed",
        border: "#fed7aa",
        icon: Code2,
        connectedResource: "LeetCode",
        resourceEvidence: `${lcSolved > 0 ? `${lcSolved} Problems Solved` : "Profile Connected"}${
          lcProfile?.medium_solved
            ? ` (${lcProfile.easy_solved || 0} Easy • ${lcProfile.medium_solved || 0} Med • ${lcProfile.hard_solved || 0} Hard)`
            : ""
        }`,
        description:
          "Practice algorithmic problems, binary trees, dynamic programming, sliding window, and Big-O invariants grounded in your LeetCode problem bank.",
        platforms: "LeetCode Canonical Problem Bank",
      });
    }

    // 2. GitHub Connected Track
    if (ghRepos.length > 0 || ghProfile?.connected) {
      const topRepo = ghRepos[0]?.name ? ghRepos[0] : { name: "CareerVerseAI", language: "Python/React" };
      tracks.push({
        id: "github",
        title: "GitHub Architecture & Codebase Review",
        badge: "🐙 GitHub Connected",
        role: "Full-Stack / Systems Engineer",
        color: "#0f172a",
        bg: "#f8fafc",
        border: "#cbd5e1",
        icon: GitBranch,
        connectedResource: "GitHub",
        resourceEvidence: `${ghRepos.length > 0 ? `${ghRepos.length} Repositories` : "Repository Connected"}: ${topRepo.name}`,
        description: `Deep dive into your real codebases like ${topRepo.name}. Cyra evaluates code design, repository modularity, API contracts, and production trade-offs.`,
        platforms: `GitHub: ${topRepo.name}`,
      });
    }

    // 3. HackerRank Connected Track
    if (hrSolved > 0 || (hrProfile?.badges && hrProfile.badges.length > 0) || hrProfile?.connected) {
      const topBadge = hrProfile?.badges?.[0]?.name || hrProfile?.badges?.[0] || "Problem Solving & SQL";
      tracks.push({
        id: "dsa",
        title: "HackerRank Problem Solving & SQL Challenges",
        badge: "🏆 HackerRank Connected",
        role: "Backend & Database Engineer",
        color: "#16a34a",
        bg: "#f0fdf4",
        border: "#bbf7d0",
        icon: CheckCircle2,
        connectedResource: "HackerRank",
        resourceEvidence: `${hrSolved > 0 ? `${hrSolved} Solved` : "Verified Badges"}: ${topBadge}`,
        description:
          "Grounded in your verified HackerRank achievements. Evaluates algorithmic problem solving, complex SQL queries, database indexing, and logic.",
        platforms: "HackerRank Verified Challenges",
      });
    }

    // 4. Resume & Verified Experience Track
    tracks.push({
      id: "behavioral",
      title: "Resume Experience & STAR Leadership",
      badge: "📄 Resume Connected",
      role: "Software Engineer",
      color: "#0284c7",
      bg: "#f0f9ff",
      border: "#bae6fd",
      icon: MessageSquare,
      connectedResource: "Resume & Skills",
      resourceEvidence: `${skillsList.length > 0 ? `${skillsList.length} Verified Skills` : "Verified Work Experience"}`,
      description:
        "Scenario questions using the STAR framework (Situation, Task, Action, Result) evaluating your verified project achievements, teamwork, and incident response.",
      platforms: "Resume Experience & STAR Method",
    });

    // 5. System Design & Distributed Architecture (if Certifications or large codebase)
    if (certsList.length > 0 || lcSolved >= 300 || ghRepos.length >= 2) {
      tracks.push({
        id: "system_design",
        title: "System Design & Distributed Scalability",
        badge: certsList.length > 0 ? "📜 Credentials Connected" : "🧠 Systems Scale",
        role: "Backend Systems Engineer",
        color: "#ef4444",
        bg: "#fee2e2",
        border: "#fecaca",
        icon: Layers,
        connectedResource: certsList.length > 0 ? "Certifications" : "Codebase Scale",
        resourceEvidence:
          certsList.length > 0
            ? certsList[0]?.name || certsList[0]?.title || `${certsList.length} Credentials`
            : "Distributed Architecture",
        description:
          "Design high-scale distributed systems, database sharding, caching tiers (Redis), microservice resilience, and rate limiters.",
        platforms: "Distributed Systems & Cloud",
      });
    }

    // Foundational fallback if external platforms have not yet synced
    if (tracks.length === 1) {
      tracks.unshift({
        id: "dsa",
        title: "Algorithmic Problem Solving (LeetCode Bank)",
        badge: "⚡ LeetCode Problem Bank",
        role: "Software Engineer (SDE)",
        color: "#6366f1",
        bg: "#ede9fe",
        border: "#c7d2fe",
        icon: Code2,
        connectedResource: "LeetCode Bank",
        resourceEvidence: "Standard Problem Bank (Connect LeetCode to personalize)",
        description:
          "Solve algorithmic problems, optimal traversals, sliding window, trees, graphs, and Big-O invariants.",
        platforms: "HackerRank & LeetCode Bank",
      });
      tracks.push({
        id: "github",
        title: "GitHub Projects & Codebase",
        badge: "🐙 GitHub Codebase",
        role: "Software Engineer",
        color: "#f97316",
        bg: "#ffedd5",
        border: "#fed7aa",
        icon: GitBranch,
        connectedResource: "GitHub",
        resourceEvidence: "Connect GitHub to analyze real repositories",
        description:
          "Deep dive into your project codebase, code modularity, architecture decisions, and production trade-offs.",
        platforms: "Connected GitHub Repositories",
      });
    }

    return tracks;
  }, [lcSolved, lcProfile, ghRepos, ghProfile, hrSolved, hrProfile, certsList, skillsList]);

  // Keep selectedTrackId valid when tracks change
  useEffect(() => {
    if (!availableTracks.some((t) => t.id === selectedTrackId) && availableTracks.length > 0) {
      setSelectedTrackId(availableTracks[0].id);
      setTargetRole(availableTracks[0].role);
    }
  }, [availableTracks, selectedTrackId]);

  const currentTrack =
    availableTracks.find((t) => t.id === selectedTrackId) || availableTracks[0];

  const handleSelectTrack = (track) => {
    setSelectedTrackId(track.id);
    setTargetRole(track.role);
  };

  const handleTestVoiceAudio = () => {
    setIsTestingVoice(true);
    const sampleText = `Hello ${candidateName || "there"}! I am Cyra, your AI Interviewer. I am ready to guide you through your technical evaluation.`;
    if (onTestVoice) {
      onTestVoice(sampleText);
    }
    setTimeout(() => setIsTestingVoice(false), 3000);
  };

  const handleLaunch = () => {
    onStartInterview(currentTrack.id, currentTrack.title, targetRole);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f8fafc",
        color: "#0f172a",
        fontFamily: "var(--font-primary, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif)",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* ── CLEAN TOP HEADER ───────────────────────────────────────────── */}
      <header
        style={{
          background: "#ffffff",
          borderBottom: "1px solid #e2e8f0",
          padding: "12px 28px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          boxShadow: "0 1px 3px rgba(0,0,0,0.02)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <Link
            to="/dashboard"
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              padding: "6px 12px",
              borderRadius: "8px",
              background: "#f1f5f9",
              border: "1px solid #e2e8f0",
              color: "#475569",
              fontSize: "0.82rem",
              fontWeight: 700,
              textDecoration: "none",
              transition: "all 0.15s ease",
            }}
          >
            <ArrowLeft size={15} /> Dashboard
          </Link>

          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span
              style={{
                width: 32,
                height: 32,
                borderRadius: "10px",
                background: "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#ffffff",
                boxShadow: "0 2px 8px rgba(99,102,241,0.3)",
              }}
            >
              <Bot size={18} />
            </span>
            <div>
              <div style={{ fontWeight: 800, fontSize: "0.98rem", color: "#0f172a", lineHeight: 1.2 }}>
                CareerVerse AI • Interview Studio
              </div>
              <div style={{ fontSize: "0.72rem", color: "#16a34a", fontWeight: 700, display: "flex", alignItems: "center", gap: "4px" }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#16a34a" }} />
                Cyra AI Proctor Active
              </div>
            </div>
          </div>
        </div>

        {/* Right Action: Question History & Candidate Name */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <button
            type="button"
            data-testid="open-history-btn"
            onClick={onOpenHistory}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              background: "#eef2ff",
              border: "1px solid #c7d2fe",
              padding: "7px 14px",
              borderRadius: "10px",
              fontSize: "0.82rem",
              fontWeight: 700,
              color: "#4338ca",
              cursor: "pointer",
            }}
          >
            <History size={15} /> Question History (30-Day Cooldown)
          </button>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              padding: "4px 10px",
              borderRadius: "20px",
              background: "#f8fafc",
              border: "1px solid #e2e8f0",
              fontSize: "0.82rem",
              fontWeight: 700,
              color: "#334155",
            }}
          >
            <span
              style={{
                width: 24,
                height: 24,
                borderRadius: "50%",
                background: "#6366f1",
                color: "#ffffff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "0.75rem",
                fontWeight: 800,
              }}
            >
              {candidateName ? candidateName[0].toUpperCase() : "U"}
            </span>
            <span>{candidateName}</span>
          </div>
        </div>
      </header>

      {/* ── MAIN STREAMLINED CONTENT CONTAINER ─────────────────────────── */}
      <main
        style={{
          flex: 1,
          maxWidth: "1080px",
          width: "100%",
          margin: "0 auto",
          padding: "2rem 1.5rem 3rem 1.5rem",
          display: "flex",
          flexDirection: "column",
          gap: "1.75rem",
        }}
      >
        {/* Title Header */}
        <div style={{ textAlign: "center" }}>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              background: "#f0fdf4",
              border: "1px solid #bbf7d0",
              color: "#166534",
              fontSize: "0.78rem",
              fontWeight: 800,
              padding: "4px 14px",
              borderRadius: "20px",
              marginBottom: "10px",
            }}
          >
            <Sparkles size={14} color="#16a34a" /> Proctored Technical & Behavioral Interviews
          </div>
          <h1
            style={{
              fontSize: "2rem",
              fontWeight: 900,
              color: "#0f172a",
              margin: "0 0 8px 0",
              letterSpacing: "-0.02em",
            }}
          >
            Select Your Interview Track
          </h1>
          <p
            style={{
              fontSize: "0.94rem",
              color: "#64748b",
              maxWidth: "680px",
              margin: "0 auto",
              lineHeight: 1.5,
            }}
          >
            Your interview options are derived directly from your connected resources—LeetCode practice, GitHub codebases, verified skills, and certifications.
          </p>
        </div>

        {/* ── CONNECTED RESOURCES GROUNDING SUMMARY BAR ───────────────────── */}
        <div
          style={{
            background: "#ffffff",
            border: "1px solid #e2e8f0",
            borderRadius: "14px",
            padding: "1rem 1.25rem",
            boxShadow: "0 2px 8px rgba(0,0,0,0.02)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: "10px",
              marginBottom: "10px",
            }}
          >
            <div
              style={{
                fontSize: "0.82rem",
                fontWeight: 800,
                color: "#0f172a",
                display: "flex",
                alignItems: "center",
                gap: "8px",
                textTransform: "uppercase",
                letterSpacing: "0.04em",
              }}
            >
              <Zap size={15} color="#6366f1" />
              Connected Resources Powering Your Interview Options:
            </div>
            <Link
              to="/resume"
              style={{
                fontSize: "0.78rem",
                fontWeight: 700,
                color: "#4f46e5",
                textDecoration: "none",
              }}
            >
              Manage Sources →
            </Link>
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              flexWrap: "wrap",
            }}
          >
            {/* LeetCode Badge */}
            <div
              style={{
                background: lcSolved > 0 ? "#fff7ed" : "#f8fafc",
                border: `1px solid ${lcSolved > 0 ? "#fed7aa" : "#e2e8f0"}`,
                borderRadius: "10px",
                padding: "6px 12px",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <span style={{ fontSize: "1rem" }}>⚡</span>
              <div>
                <div style={{ fontSize: "0.72rem", color: "#9a3412", fontWeight: 800 }}>LeetCode</div>
                <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "#c2410c" }}>
                  {lcSolved > 0 ? `${lcSolved} Solved` : "Connected"}
                </div>
              </div>
            </div>

            {/* GitHub Badge */}
            <div
              style={{
                background: ghRepos.length > 0 ? "#f8fafc" : "#f8fafc",
                border: `1px solid ${ghRepos.length > 0 ? "#cbd5e1" : "#e2e8f0"}`,
                borderRadius: "10px",
                padding: "6px 12px",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <span style={{ fontSize: "1rem" }}>🐙</span>
              <div>
                <div style={{ fontSize: "0.72rem", color: "#334155", fontWeight: 800 }}>GitHub</div>
                <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "#0f172a" }}>
                  {ghRepos.length > 0 ? `${ghRepos.length} Repositories` : "CareerVerseAI"}
                </div>
              </div>
            </div>

            {/* HackerRank Badge */}
            <div
              style={{
                background: "#f0fdf4",
                border: "1px solid #bbf7d0",
                borderRadius: "10px",
                padding: "6px 12px",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <span style={{ fontSize: "1rem" }}>🏆</span>
              <div>
                <div style={{ fontSize: "0.72rem", color: "#166534", fontWeight: 800 }}>HackerRank</div>
                <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "#15803d" }}>
                  {hrSolved > 0 ? `${hrSolved} Solved` : "Problem Solving & SQL"}
                </div>
              </div>
            </div>

            {/* Resume / Skills Badge */}
            <div
              style={{
                background: "#f0f9ff",
                border: "1px solid #bae6fd",
                borderRadius: "10px",
                padding: "6px 12px",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <span style={{ fontSize: "1rem" }}>📄</span>
              <div>
                <div style={{ fontSize: "0.72rem", color: "#0369a1", fontWeight: 800 }}>Resume & Experience</div>
                <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "#0284c7" }}>
                  {skillsList.length > 0 ? `${skillsList.length} Verified Skills` : "Verified Project Profile"}
                </div>
              </div>
            </div>

            {/* Certifications Badge */}
            {certsList.length > 0 && (
              <div
                style={{
                  background: "#f5f3ff",
                  border: "1px solid #ddd6fe",
                  borderRadius: "10px",
                  padding: "6px 12px",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                <span style={{ fontSize: "1rem" }}>📜</span>
                <div>
                  <div style={{ fontSize: "0.72rem", color: "#5b21b6", fontWeight: 800 }}>Certifications</div>
                  <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "#7c3aed" }}>
                    {certsList.length} Credentials
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Dynamic Connected Resources Track Cards */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "14px",
          }}
        >
          {availableTracks.map((track, tIdx) => {
            const isSelected = selectedTrackId === track.id;
            const Icon = track.icon;

            return (
              <div
                key={tIdx}
                onClick={() => handleSelectTrack(track)}
                style={{
                  background: isSelected ? "#ffffff" : "#ffffff",
                  border: isSelected ? `2px solid ${track.color}` : "1px solid #e2e8f0",
                  borderRadius: "16px",
                  padding: "1.25rem",
                  cursor: "pointer",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  boxShadow: isSelected
                    ? `0 8px 24px ${track.color}20`
                    : "0 2px 6px rgba(0,0,0,0.02)",
                  transform: isSelected ? "translateY(-2px)" : "none",
                  transition: "all 0.2s ease",
                  position: "relative",
                }}
              >
                <div>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      marginBottom: "12px",
                    }}
                  >
                    <div
                      style={{
                        width: 40,
                        height: 40,
                        borderRadius: "10px",
                        background: track.bg,
                        color: track.color,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <Icon size={20} />
                    </div>

                    <span
                      style={{
                        fontSize: "0.72rem",
                        fontWeight: 800,
                        background: isSelected ? track.color : track.bg,
                        color: isSelected ? "#ffffff" : track.color,
                        padding: "3px 10px",
                        borderRadius: "12px",
                        letterSpacing: "0.02em",
                        border: `1px solid ${track.border || "transparent"}`,
                      }}
                    >
                      {track.badge}
                    </span>
                  </div>

                  <h3
                    style={{
                      fontSize: "1.05rem",
                      fontWeight: 800,
                      color: "#0f172a",
                      margin: "0 0 6px 0",
                    }}
                  >
                    {track.title}
                  </h3>

                  {/* Connected Resource Grounding Badge */}
                  {track.resourceEvidence && (
                    <div
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "6px",
                        background: track.bg,
                        border: `1px solid ${track.border || "#cbd5e1"}`,
                        padding: "2px 8px",
                        borderRadius: "6px",
                        fontSize: "0.72rem",
                        fontWeight: 700,
                        color: track.color,
                        marginBottom: "10px",
                      }}
                    >
                      <span>✓ From {track.connectedResource}:</span>
                      <span style={{ fontWeight: 600 }}>{track.resourceEvidence}</span>
                    </div>
                  )}

                  <p
                    style={{
                      fontSize: "0.8rem",
                      color: "#64748b",
                      margin: "0 0 14px 0",
                      lineHeight: 1.45,
                    }}
                  >
                    {track.description}
                  </p>
                </div>

                <div
                  style={{
                    paddingTop: "10px",
                    borderTop: "1px solid #f1f5f9",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    fontSize: "0.74rem",
                    color: "#64748b",
                  }}
                >
                  <span style={{ fontWeight: 600 }}>{track.platforms}</span>
                  <div
                    style={{
                      width: 18,
                      height: 18,
                      borderRadius: "50%",
                      border: isSelected ? `5px solid ${track.color}` : "2px solid #cbd5e1",
                      background: "#ffffff",
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* ── STREAMLINED INTERVIEW CONFIGURATION PANEL ───────────────── */}
        <div
          style={{
            background: "#ffffff",
            border: "1px solid #e2e8f0",
            borderRadius: "18px",
            padding: "1.5rem 1.75rem",
            boxShadow: "0 4px 16px rgba(0,0,0,0.03)",
          }}
        >
          <div
            style={{
              fontSize: "0.85rem",
              fontWeight: 800,
              color: "#0f172a",
              marginBottom: "1rem",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <Target size={16} color="#6366f1" />
            Interview Configuration
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
              gap: "16px",
              marginBottom: "1.5rem",
            }}
          >
            {/* Target Role Input */}
            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "0.78rem",
                  fontWeight: 700,
                  color: "#475569",
                  marginBottom: "6px",
                }}
              >
                Target Role
              </label>
              <input
                type="text"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                placeholder="e.g. Software Engineer (SDE)"
                style={{
                  width: "100%",
                  padding: "9px 12px",
                  borderRadius: "10px",
                  border: "1px solid #cbd5e1",
                  fontSize: "0.88rem",
                  fontWeight: 600,
                  color: "#0f172a",
                  outline: "none",
                  boxSizing: "border-box",
                }}
              />
            </div>

            {/* Language Selector */}
            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "0.78rem",
                  fontWeight: 700,
                  color: "#475569",
                  marginBottom: "6px",
                }}
              >
                Spoken Language
              </label>
              <select
                value={selectedLang}
                onChange={(e) => setSelectedLang(e.target.value)}
                style={{
                  width: "100%",
                  padding: "9px 12px",
                  borderRadius: "10px",
                  border: "1px solid #cbd5e1",
                  fontSize: "0.88rem",
                  fontWeight: 600,
                  color: "#0f172a",
                  outline: "none",
                  background: "#ffffff",
                  boxSizing: "border-box",
                }}
              >
                {SUPPORTED_LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Voice Proctoring Check */}
            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "0.78rem",
                  fontWeight: 700,
                  color: "#475569",
                  marginBottom: "6px",
                }}
              >
                AI Audio Proctoring
              </label>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  height: "38px",
                }}
              >
                <button
                  type="button"
                  onClick={handleTestVoiceAudio}
                  disabled={isTestingVoice}
                  style={{
                    flex: 1,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "6px",
                    background: isTestingVoice ? "#eef2ff" : "#f8fafc",
                    border: "1px solid #cbd5e1",
                    borderRadius: "10px",
                    padding: "8px 12px",
                    fontSize: "0.8rem",
                    fontWeight: 700,
                    color: "#334155",
                    cursor: "pointer",
                  }}
                >
                  <Volume2 size={15} color={isTestingVoice ? "#4f46e5" : "#64748b"} />
                  {isTestingVoice ? "Speaking sample…" : "Test Cyra's Voice"}
                </button>
              </div>
            </div>
          </div>

          {/* Primary Action Button */}
          <button
            type="button"
            onClick={handleLaunch}
            disabled={loading}
            style={{
              width: "100%",
              padding: "14px 20px",
              borderRadius: "12px",
              background: "linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)",
              color: "#ffffff",
              border: "none",
              fontSize: "1rem",
              fontWeight: 800,
              cursor: loading ? "wait" : "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              boxShadow: "0 4px 14px rgba(79, 70, 229, 0.35)",
              transition: "all 0.15s ease",
            }}
          >
            <Sparkles size={18} />
            {loading ? "Starting Interview…" : `Start ${currentTrack.title} →`}
          </button>
        </div>

        {/* ── GROUNDED CONNECTED EVIDENCE FOOTER ───────────────────────── */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "14px",
            flexWrap: "wrap",
            fontSize: "0.78rem",
            color: "#64748b",
          }}
        >
          <span style={{ fontWeight: 700, color: "#166534", display: "flex", alignItems: "center", gap: "5px" }}>
            <CheckCircle2 size={14} color="#16a34a" /> Verified Evidence Sources Active:
          </span>
          <span style={{ background: "#ffffff", border: "1px solid #e2e8f0", padding: "3px 10px", borderRadius: "10px" }}>
            HackerRank {hrProfile?.total_solved ? `(${hrProfile.total_solved} Solved)` : "(Python, SQL)"}
          </span>
          <span style={{ background: "#ffffff", border: "1px solid #e2e8f0", padding: "3px 10px", borderRadius: "10px" }}>
            LeetCode {lcProfile?.total_solved ? `(${lcProfile.total_solved} Solved)` : "(DSA Problem Bank)"}
          </span>
          <span style={{ background: "#ffffff", border: "1px solid #e2e8f0", padding: "3px 10px", borderRadius: "10px" }}>
            GitHub Repositories
          </span>
          <span style={{ background: "#ffffff", border: "1px solid #e2e8f0", padding: "3px 10px", borderRadius: "10px" }}>
            Resume Experience
          </span>
        </div>
      </main>

      {/* Spaced Repetition Modal */}
      {renderQuestionHistoryModal()}
    </div>
  );
}
