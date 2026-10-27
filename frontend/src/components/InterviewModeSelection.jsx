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
import "../pages/InterviewPage.css";

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
  const [selectedRepoId, setSelectedRepoId] = useState("");
  const [sessionMode, setSessionMode] = useState("fresh");
  const [questionCount, setQuestionCount] = useState(5);

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
        badge: "LeetCode Connected",
        role: "Software Engineer (SDE / Algorithms)",
        color: "var(--accent, #6366f1)",
        bg: "var(--accent-soft, rgba(99, 102, 241, 0.12))",
        border: "var(--accent-border, rgba(99, 102, 241, 0.25))",
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
        badge: "GitHub Connected",
        role: "Full-Stack / Systems Engineer",
        color: "var(--accent, #6366f1)",
        bg: "var(--accent-soft, rgba(99, 102, 241, 0.12))",
        border: "var(--accent-border, rgba(99, 102, 241, 0.25))",
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
        id: "hackerrank",
        title: "HackerRank Problem Solving & SQL Challenges",
        badge: "HackerRank Connected",
        role: "Backend & Database Engineer",
        color: "var(--accent, #6366f1)",
        bg: "var(--accent-soft, rgba(99, 102, 241, 0.12))",
        border: "var(--accent-border, rgba(99, 102, 241, 0.25))",
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
      badge: "Resume Connected",
      role: "Software Engineer",
      color: "var(--accent, #6366f1)",
      bg: "var(--accent-soft, rgba(99, 102, 241, 0.12))",
      border: "var(--accent-border, rgba(99, 102, 241, 0.25))",
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
        badge: certsList.length > 0 ? "Credentials Connected" : "Systems Scale",
        role: "Backend Systems Engineer",
        color: "var(--accent, #6366f1)",
        bg: "var(--accent-soft, rgba(99, 102, 241, 0.12))",
        border: "var(--accent-border, rgba(99, 102, 241, 0.25))",
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
        badge: "LeetCode Problem Bank",
        role: "Software Engineer (SDE)",
        color: "var(--accent, #6366f1)",
        bg: "var(--accent-soft, rgba(99, 102, 241, 0.12))",
        border: "var(--accent-border, rgba(99, 102, 241, 0.25))",
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
        badge: "GitHub Codebase",
        role: "Software Engineer",
        color: "var(--accent, #6366f1)",
        bg: "var(--accent-soft, rgba(99, 102, 241, 0.12))",
        border: "var(--accent-border, rgba(99, 102, 241, 0.25))",
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
    onStartInterview(
      currentTrack.id,
      currentTrack.title,
      targetRole,
      selectedRepoId ? Number(selectedRepoId) : null,
      sessionMode,
      questionCount,
    );
  };

  return (
    <div className="interview-page-wrapper">
      {/* ── CLEAN TOP HEADER ───────────────────────────────────────────── */}
      <header className="interview-header">
        <div className="interview-header-brand">
          <Link
            to="/dashboard"
            className="interview-back-btn"
            title="Return to Dashboard"
          >
            <ArrowLeft size={15} /> Dashboard
          </Link>

          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span
              style={{
                width: 32,
                height: 32,
                borderRadius: "8px",
                background: "var(--accent, #6366f1)",
                color: "var(--accent-contrast, #ffffff)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 2px 8px var(--accent-glow, rgba(99, 102, 241, 0.25))",
              }}
            >
              <Bot size={18} />
            </span>
            <div>
              <div style={{ fontWeight: 700, fontSize: "0.98rem", color: "var(--text)", lineHeight: 1.2 }}>
                CareerVerse AI • Interview Studio
              </div>
              <div className="interview-header-status">
                <span className="interview-pulse-dot" />
                Cyra AI Proctor Active
              </div>
            </div>
          </div>
        </div>

        {/* Right Action: Question History & Candidate Name */}
        <div className="interview-header-controls">
          <button
            type="button"
            data-testid="open-history-btn"
            onClick={onOpenHistory}
            className="interview-back-btn"
            style={{ fontWeight: 700, color: "var(--text)" }}
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
              background: "var(--surface-2)",
              border: "1px solid var(--border)",
              fontSize: "0.82rem",
              fontWeight: 700,
              color: "var(--text)",
            }}
          >
            <span
              style={{
                width: 24,
                height: 24,
                borderRadius: "50%",
                background: "var(--accent, #6366f1)",
                color: "var(--accent-contrast, #ffffff)",
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
      <main className="interview-setup-container">
        {/* Title Header */}
        <div className="interview-setup-hero">
          <div className="interview-setup-eyebrow">
            <Sparkles size={14} /> Proctored Technical &amp; Behavioral Interviews
          </div>
          <h1 className="interview-setup-title">
            Select Your Interview Track
          </h1>
          <p className="interview-setup-subtitle">
            Your interview options are derived directly from your connected resources—LeetCode practice, GitHub codebases, verified skills, and certifications.
          </p>
        </div>

        {/* ── CONNECTED RESOURCES GROUNDING SUMMARY BAR ───────────────────── */}
        <div className="interview-grounding-bar">
          <div className="interview-grounding-header">
            <div className="interview-grounding-label">
              <Zap size={15} color="var(--accent)" />
              Connected Resources Powering Your Interview Options:
            </div>
            <Link
              to="/resume"
              style={{
                fontSize: "0.78rem",
                fontWeight: 700,
                color: "var(--accent)",
                textDecoration: "none",
              }}
            >
              Manage Sources →
            </Link>
          </div>

          <div className="interview-grounding-pills">
            {/* LeetCode Badge */}
            <div className={`interview-evidence-pill ${lcSolved > 0 ? "connected" : ""}`}>
              <span style={{ fontSize: "0.95rem" }}>⚡</span>
              <div>
                <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 700 }}>LeetCode</div>
                <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--text)" }}>
                  {lcSolved > 0 ? `${lcSolved} Solved` : "Connected"}
                </div>
              </div>
            </div>

            {/* GitHub Badge */}
            <div className={`interview-evidence-pill ${ghRepos.length > 0 ? "connected" : ""}`}>
              <span style={{ fontSize: "0.95rem" }}>🐙</span>
              <div>
                <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 700 }}>GitHub</div>
                <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--text)" }}>
                  {ghRepos.length > 0 ? `${ghRepos.length} Repositories` : "CareerVerseAI"}
                </div>
              </div>
            </div>

            {/* HackerRank Badge */}
            <div className="interview-evidence-pill connected">
              <span style={{ fontSize: "0.95rem" }}>🏆</span>
              <div>
                <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 700 }}>HackerRank</div>
                <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--text)" }}>
                  {hrSolved > 0 ? `${hrSolved} Solved` : "Problem Solving & SQL"}
                </div>
              </div>
            </div>

            {/* Resume / Skills Badge */}
            <div className="interview-evidence-pill connected">
              <span style={{ fontSize: "0.95rem" }}>📄</span>
              <div>
                <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 700 }}>Resume &amp; Experience</div>
                <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--text)" }}>
                  {skillsList.length > 0 ? `${skillsList.length} Verified Skills` : "Verified Project Profile"}
                </div>
              </div>
            </div>

            {/* Certifications Badge */}
            {certsList.length > 0 && (
              <div className="interview-evidence-pill connected">
                <span style={{ fontSize: "0.95rem" }}>📜</span>
                <div>
                  <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 700 }}>Certifications</div>
                  <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--text)" }}>
                    {certsList.length} Credentials
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Dynamic Connected Resources Track Cards */}
        <div className="interview-tracks-grid">
          {availableTracks.map((track, tIdx) => {
            const isSelected = selectedTrackId === track.id;
            const Icon = track.icon;

            return (
              <div
                key={tIdx}
                onClick={() => handleSelectTrack(track)}
                tabIndex={0}
                role="button"
                aria-pressed={isSelected}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    handleSelectTrack(track);
                  }
                }}
                className={`interview-track-card ${isSelected ? "selected" : ""}`}
              >
                <div>
                  <div className="interview-track-card-head">
                    <div className="interview-track-icon">
                      <Icon size={20} />
                    </div>

                    <span className="interview-track-badge">
                      {track.badge}
                    </span>
                  </div>

                  <h3 className="interview-track-title">
                    {track.title}
                  </h3>

                  {/* Connected Resource Grounding Badge */}
                  {track.resourceEvidence && (
                    <div className="interview-track-evidence">
                      <span>✓ From {track.connectedResource}:</span>
                      <span style={{ fontWeight: 600 }}>{track.resourceEvidence}</span>
                    </div>
                  )}

                  <p className="interview-track-desc">
                    {track.description}
                  </p>
                </div>

                <div className="interview-track-footer">
                  <span style={{ fontWeight: 600 }}>{track.platforms}</span>
                  <div className="interview-radio-dot">
                    {isSelected && <div className="interview-radio-dot-inner" />}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* ── STREAMLINED INTERVIEW CONFIGURATION PANEL ───────────────── */}
        <div className="interview-config-card">
          <div className="interview-config-title">
            <Target size={16} color="var(--accent)" />
            Interview Configuration
          </div>

          <div className="interview-config-grid">
            {/* Target Role Input */}
            <div>
              <label className="interview-field-label">
                Target Role
              </label>
              <input
                type="text"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                placeholder="e.g. Software Engineer (SDE)"
                className="interview-input"
              />
            </div>

            {/* Language Selector */}
            <div>
              <label className="interview-field-label">
                Spoken Language
              </label>
              <select
                value={selectedLang}
                onChange={(e) => setSelectedLang(e.target.value)}
                className="interview-select"
              >
                {SUPPORTED_LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Session Mode Selector */}
            <div>
              <label className="interview-field-label">
                Session Mode
              </label>
              <select
                value={sessionMode}
                onChange={(e) => setSessionMode(e.target.value)}
                className="interview-select"
              >
                <option value="fresh">Fresh Comprehensive (5-Phased Sequence)</option>
                <option value="revision">Targeted Revision (Weak Areas Focus)</option>
                <option value="mock_exam">Mock Assessment (Strict Evaluation)</option>
              </select>
            </div>

            {/* Session Length / Question Count Selector */}
            <div>
              <label className="interview-field-label">
                Session Length
              </label>
              <select
                value={questionCount}
                onChange={(e) => setQuestionCount(Number(e.target.value))}
                className="interview-select"
              >
                <option value={5}>5 Questions (Standard Round)</option>
                <option value={8}>8 Questions (In-Depth Assessment)</option>
              </select>
            </div>

            {/* Repository Selector */}
            {ghRepos.length > 0 && (
              <div>
                <label className="interview-field-label">
                  Grounded Codebase
                </label>
                <select
                  value={selectedRepoId}
                  onChange={(e) => setSelectedRepoId(e.target.value)}
                  className="interview-select"
                >
                  <option value="">Auto-Detect Most Relevant Repo</option>
                  {ghRepos.map((repo, idx) => (
                    <option key={repo.id || idx} value={repo.id || repo.name}>
                      {repo.name} {repo.language ? `(${repo.language})` : ""}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Voice Proctoring Check */}
            <div>
              <label className="interview-field-label">
                AI Audio Proctoring
              </label>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", height: "38px" }}>
                <button
                  type="button"
                  onClick={handleTestVoiceAudio}
                  disabled={isTestingVoice}
                  className="interview-back-btn"
                  style={{ flex: 1, justifyContent: "center", height: "38px" }}
                >
                  <Volume2 size={15} color="var(--accent)" />
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
            className="interview-launch-btn"
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
            gap: "10px",
            flexWrap: "wrap",
            fontSize: "0.78rem",
            color: "var(--text-muted)",
          }}
        >
          <span style={{ fontWeight: 700, color: "var(--success)", display: "flex", alignItems: "center", gap: "5px" }}>
            <CheckCircle2 size={14} /> Verified Evidence Sources Active:
          </span>
          <span style={{ background: "var(--surface)", border: "1px solid var(--border)", padding: "3px 10px", borderRadius: "6px" }}>
            HackerRank {hrProfile?.total_solved ? `(${hrProfile.total_solved} Solved)` : "(Python, SQL)"}
          </span>
          <span style={{ background: "var(--surface)", border: "1px solid var(--border)", padding: "3px 10px", borderRadius: "6px" }}>
            LeetCode {lcProfile?.total_solved ? `(${lcProfile.total_solved} Solved)` : "(DSA Problem Bank)"}
          </span>
          <span style={{ background: "var(--surface)", border: "1px solid var(--border)", padding: "3px 10px", borderRadius: "6px" }}>
            GitHub Repositories
          </span>
          <span style={{ background: "var(--surface)", border: "1px solid var(--border)", padding: "3px 10px", borderRadius: "6px" }}>
            Resume Experience
          </span>
        </div>
      </main>

      {/* Spaced Repetition Modal */}
      {renderQuestionHistoryModal()}
    </div>
  );
}
