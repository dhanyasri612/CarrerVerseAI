import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  ArrowLeft,
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Trash2,
  ExternalLink,
  ShieldCheck,
  GitBranch,
  Code2,
  Trophy,
  Check,
  Clock,
  Sparkles,
} from "lucide-react";
import {
  getResumes,
  uploadResume,
  deleteResume,
  parseResume,
  getProfileSnapshot,
  syncGithub,
  syncLeetCode,
  syncHackerRank,
  clearProfileSnapshot,
} from "../services/careerService";
import { getApiError } from "../services/api";

function cleanSourceInput(raw, type) {
  let val = (raw || "").trim();
  if (!val) return "";
  try {
    if (val.startsWith("http://") || val.startsWith("https://")) {
      const url = new URL(val);
      const parts = url.pathname.split("/").filter(Boolean);
      if (type === "HackerRank") {
        const profileIdx = parts.indexOf("profile");
        if (profileIdx !== -1 && parts[profileIdx + 1]) {
          return parts[profileIdx + 1];
        }
      }
      if (type === "LeetCode") {
        const uIdx = parts.indexOf("u");
        if (uIdx !== -1 && parts[uIdx + 1]) {
          return parts[uIdx + 1];
        }
      }
      return parts[parts.length - 1] || val;
    }
  } catch (e) {}
  if (val.includes("/")) {
    val = val.split("/").filter(Boolean).pop() || val;
  }
  return val.replace(/^@/, "").trim();
}

export default function ResumePage() {
  const [resumes, setResumes] = useState([]);
  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [parsingId, setParsingId] = useState(null);
  const [syncingSource, setSyncingSource] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Source usernames
  const [githubUser, setGithubUser] = useState("");
  const [leetcodeUser, setLeetcodeUser] = useState("");
  const [hackerrankUser, setHackerrankUser] = useState("");

  const fileInputRef = useRef(null);

  const loadData = async () => {
    setError("");
    try {
      const [resumesData, snapData] = await Promise.all([
        getResumes().catch(() => []),
        getProfileSnapshot({ force: true }).catch(() => null),
      ]);
      const list = Array.isArray(resumesData) ? resumesData : resumesData ? [resumesData] : [];
      setResumes(list);
      setSnapshot(snapData);

      // Pre-fill usernames from profile snapshot if available
      const unified = snapData?.unified;
      if (unified?.github_summary?.username) setGithubUser(unified.github_summary.username);
      if (unified?.leetcode_summary?.username) setLeetcodeUser(unified.leetcode_summary.username);
      if (unified?.hackerrank_summary?.username) setHackerrankUser(unified.hackerrank_summary.username);
    } catch (err) {
      setError(getApiError(err, "Failed to load resume and sources."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleFileUpload = async (file) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".pdf") && file.type !== "application/pdf") {
      setError("Please select a PDF document (.pdf). CareerVerse resume parsing requires a PDF file.");
      return;
    }
    setUploading(true);
    setError("");
    setSuccess("");

    try {
      const uploaded = await uploadResume(file);
      setSuccess(`Resume "${file.name}" uploaded successfully! Extracting skills and evidence...`);

      // Automatically trigger parser if we got an ID
      const resumeId = uploaded?.id || uploaded?.resume_id;
      if (resumeId) {
        setParsingId(resumeId);
        try {
          await parseResume(resumeId);
          setSuccess(`Resume "${file.name}" uploaded and parsed into your career profile.`);
        } catch (parseErr) {
          console.warn("Auto-parse warning:", parseErr);
        }
      }

      await clearProfileSnapshot();
      await loadData();
    } catch (err) {
      setError(getApiError(err, "Failed to upload resume. Please ensure it is a valid PDF document."));
    } finally {
      setUploading(false);
      setParsingId(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer?.files?.[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleReparse = async (resumeId) => {
    setParsingId(resumeId);
    setError("");
    setSuccess("");
    try {
      await parseResume(resumeId);
      setSuccess("Resume re-parsed successfully. Profile evidence updated.");
      await clearProfileSnapshot();
      await loadData();
    } catch (err) {
      setError(getApiError(err, "Failed to parse resume."));
    } finally {
      setParsingId(null);
    }
  };

  const handleDelete = async (resumeId) => {
    if (!window.confirm("Are you sure you want to remove this resume from your CareerVerse dossier?")) return;
    setError("");
    setSuccess("");
    try {
      await deleteResume(resumeId);
      setSuccess("Resume removed.");
      await clearProfileSnapshot();
      await loadData();
    } catch (err) {
      setError(getApiError(err, "Failed to delete resume."));
    }
  };

  const handleSyncSource = async (type, rawInput) => {
    const cleaned = cleanSourceInput(rawInput, type);
    if (!cleaned) {
      setError(`Please enter your ${type} username before connecting.`);
      return;
    }

    // Auto-update input field with the cleaned username
    if (type === "GitHub") setGithubUser(cleaned);
    if (type === "LeetCode") setLeetcodeUser(cleaned);
    if (type === "HackerRank") setHackerrankUser(cleaned);

    setSyncingSource(type);
    setError("");
    setSuccess("");

    try {
      if (type === "GitHub") await syncGithub(cleaned);
      else if (type === "LeetCode") await syncLeetCode(cleaned);
      else if (type === "HackerRank") await syncHackerRank(cleaned);

      setSuccess(`${type} (${cleaned}) connected and synchronized with your candidate profile!`);
      await clearProfileSnapshot();
      await loadData();
    } catch (err) {
      setError(getApiError(err, `Failed to sync ${type} for user "${cleaned}". Please check your username.`));
    } finally {
      setSyncingSource(null);
    }
  };

  const profile = snapshot?.unified;
  const activeResume = resumes?.[0];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--cv-space-8)" }}>
      {/* ─── CHAPTER INTRO ───────────────────────────────────────────────── */}
      <header className="cv-chapter-intro">
        <span className="cv-chapter-number">CHAPTER 02</span>
        <div>
          <div className="cv-chapter-kicker">02 &nbsp; / &nbsp; Your Work & Sources</div>
          <h1 className="cv-chapter-title">
            Ground your story in <span className="serif">verified evidence.</span>
          </h1>
          <p className="cv-chapter-deck">
            Upload your resume and connect your technical sources. CareerVerse extracts skills,
            projects, and metrics to ground your AI recommendations without hallucinations.
          </p>
          {error && (
            <div className="cv-note-block" style={{ borderColor: "var(--cv-danger)", color: "var(--cv-danger)", marginTop: "16px" }}>
              <AlertCircle size={16} />
              <div><strong>Notice:</strong> {error}</div>
            </div>
          )}
          {success && (
            <div className="cv-note-block" style={{ borderColor: "var(--cv-success)", color: "var(--cv-success)", marginTop: "16px" }}>
              <CheckCircle2 size={16} />
              <div><strong>Success:</strong> {success}</div>
            </div>
          )}
        </div>
        <p className="cv-intro-aside">
          All uploaded resumes are parsed locally with secure extraction. Your data is strictly used to inform your candidate dossier.
        </p>
      </header>

      {/* ─── SECTION 1: RESUME UPLOAD WORKSPACE ───────────────────────────── */}
      <section className="cv-editorial-section">
        <div className="cv-section-index">01 / RESUME DOCUMENT</div>
        <div className="cv-section-content">
          <h2>Source Resume Management</h2>
          <p>
            Upload your latest CV or resume in PDF or Word format. CareerVerse analyzes your experience, education,
            and declared competencies.
          </p>

          {/* Drag and Drop Zone */}
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            style={{
              border: "2px dashed var(--border, var(--cv-border))",
              borderRadius: "8px",
              padding: "clamp(32px, 5vw, 48px)",
              textAlign: "center",
              background: "var(--surface-2, var(--cv-bg-subtle))",
              cursor: uploading ? "not-allowed" : "pointer",
              transition: "all 0.2s ease",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "12px",
              margin: "20px 0",
            }}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
              accept=".pdf,.docx,.doc,.txt"
              style={{ display: "none" }}
              disabled={uploading}
            />

            <div
              style={{
                width: "52px",
                height: "52px",
                borderRadius: "50%",
                background: "var(--accent-soft, var(--cv-accent-soft))",
                color: "var(--accent, var(--cv-accent))",
                display: "grid",
                placeItems: "center",
              }}
            >
              <UploadCloud size={26} />
            </div>

            <div>
              <strong style={{ fontSize: "1rem", color: "var(--cv-text)", display: "block", marginBottom: "4px" }}>
                {uploading ? "Uploading & Analyzing Document…" : "Drop your resume here, or browse files"}
              </strong>
              <span style={{ fontSize: "0.8rem", color: "var(--cv-muted)" }}>
                Supports PDF, DOCX, DOC, TXT (up to 10MB)
              </span>
            </div>
          </div>

          {/* Active Resumes List */}
          {resumes.length > 0 && (
            <div style={{ marginTop: "24px" }}>
              <h3 style={{ fontSize: "0.95rem", fontWeight: 700, marginBottom: "12px", color: "var(--cv-text)" }}>
                Active Uploaded Document
              </h3>
              <div
                style={{
                  border: "1px solid var(--border, var(--cv-border))",
                  borderRadius: "8px",
                  padding: "16px 20px",
                  background: "var(--surface, var(--cv-surface))",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  flexWrap: "wrap",
                  gap: "16px",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                  <div
                    style={{
                      width: "40px",
                      height: "40px",
                      borderRadius: "8px",
                      background: "var(--accent-soft, var(--cv-accent-soft))",
                      color: "var(--accent, var(--cv-accent))",
                      display: "grid",
                      placeItems: "center",
                    }}
                  >
                    <FileText size={20} />
                  </div>
                  <div>
                    <strong style={{ fontSize: "0.92rem", color: "var(--cv-text)", display: "block" }}>
                      {activeResume?.file_name || activeResume?.filename || "Uploaded Resume"}
                    </strong>
                    <span style={{ fontSize: "0.76rem", color: "var(--cv-muted)" }}>
                      {activeResume?.created_at ? new Date(activeResume.created_at).toLocaleDateString() : "Active Evidence Source"} · Verified
                    </span>
                  </div>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <button
                    type="button"
                    className="cv-button"
                    onClick={() => handleReparse(activeResume?.id || activeResume?.resume_id)}
                    disabled={parsingId === (activeResume?.id || activeResume?.resume_id)}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "6px",
                      padding: "8px 14px",
                      fontSize: "0.8rem",
                      border: "1px solid var(--cv-rule)",
                      background: "transparent",
                      color: "var(--cv-text)",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                  >
                    <RefreshCw size={13} className={parsingId ? "cv-spin" : ""} />
                    {parsingId ? "Parsing…" : "Re-parse"}
                  </button>

                  <button
                    type="button"
                    onClick={() => handleDelete(activeResume?.id || activeResume?.resume_id)}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "6px",
                      padding: "8px 12px",
                      fontSize: "0.8rem",
                      border: "1px solid color-mix(in srgb, var(--cv-danger) 30%, transparent)",
                      background: "transparent",
                      color: "var(--cv-danger)",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                  >
                    <Trash2 size={13} /> Remove
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ─── SECTION 2: CONNECTED SOURCE CHANNELS ────────────────────────── */}
      <section className="cv-editorial-section">
        <div className="cv-section-index">02 / DEVELOPER PROFILES</div>
        <div className="cv-section-content">
          <h2>Connect Coding &amp; Technical Profiles</h2>
          <p>
            Substantiate your skills with real-world repositories, solved algorithm challenges, and technical certifications.
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px", marginTop: "20px" }}>
            {/* GitHub Card */}
            <div
              style={{
                border: "1px solid var(--border, var(--cv-border))",
                borderRadius: "8px",
                padding: "20px",
                background: "var(--surface, var(--cv-surface))",
                display: "flex",
                flexDirection: "column",
                gap: "14px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <GitBranch size={20} color="var(--accent, var(--cv-accent))" />
                  <strong style={{ fontSize: "0.95rem", color: "var(--text, var(--cv-text))" }}>GitHub</strong>
                </div>
                {profile?.github_summary?.connected ? (
                  <span style={{ display: "inline-flex", alignItems: "center", gap: "4px", color: "var(--success, var(--cv-success))", fontSize: "0.72rem", fontWeight: 700 }}>
                    <Check size={12} /> CONNECTED
                  </span>
                ) : (
                  <span style={{ fontSize: "0.72rem", color: "var(--text-muted, var(--cv-muted))" }}>NOT CONNECTED</span>
                )}
              </div>

              <p style={{ fontSize: "0.78rem", color: "var(--text-muted, var(--cv-muted))", margin: 0, lineHeight: 1.45 }}>
                Sync repositories, commits, and language stats to verify practical project execution.
              </p>

              <div style={{ display: "flex", gap: "8px" }}>
                <input
                  type="text"
                  placeholder="GitHub username"
                  value={githubUser}
                  onChange={(e) => setGithubUser(e.target.value)}
                  style={{
                    flex: 1,
                    height: "38px",
                    padding: "0 12px",
                    border: "1px solid var(--border, var(--cv-border))",
                    background: "var(--surface-2, var(--cv-bg-subtle))",
                    color: "var(--text, var(--cv-text))",
                    fontSize: "0.82rem",
                    borderRadius: "6px",
                    outline: "none",
                  }}
                />
                <button
                  type="button"
                  onClick={() => handleSyncSource("GitHub", githubUser)}
                  disabled={syncingSource === "GitHub"}
                  style={{
                    padding: "0 14px",
                    height: "38px",
                    background: "var(--accent-soft, var(--cv-accent-soft))",
                    color: "var(--accent, var(--cv-accent))",
                    border: "1px solid var(--accent-border, var(--cv-accent-border))",
                    borderRadius: "6px",
                    fontSize: "0.8rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  <RefreshCw size={12} className={syncingSource === "GitHub" ? "cv-spin" : ""} />
                  {syncingSource === "GitHub" ? "Syncing…" : "Sync"}
                </button>
              </div>
            </div>

            {/* LeetCode Card */}
            <div
              style={{
                border: "1px solid var(--border, var(--cv-border))",
                borderRadius: "8px",
                padding: "20px",
                background: "var(--surface, var(--cv-surface))",
                display: "flex",
                flexDirection: "column",
                gap: "14px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <Code2 size={20} color="var(--accent, var(--cv-accent))" />
                  <strong style={{ fontSize: "0.95rem", color: "var(--text, var(--cv-text))" }}>LeetCode</strong>
                </div>
                {profile?.leetcode_summary?.connected ? (
                  <span style={{ display: "inline-flex", alignItems: "center", gap: "4px", color: "var(--success, var(--cv-success))", fontSize: "0.72rem", fontWeight: 700 }}>
                    <Check size={12} /> CONNECTED
                  </span>
                ) : (
                  <span style={{ fontSize: "0.72rem", color: "var(--text-muted, var(--cv-muted))" }}>NOT CONNECTED</span>
                )}
              </div>

              <p style={{ fontSize: "0.78rem", color: "var(--text-muted, var(--cv-muted))", margin: 0, lineHeight: 1.45 }}>
                Sync problem solving statistics (Easy, Medium, Hard) and algorithm capability signals.
              </p>

              <div style={{ display: "flex", gap: "8px" }}>
                <input
                  type="text"
                  placeholder="LeetCode username"
                  value={leetcodeUser}
                  onChange={(e) => setLeetcodeUser(e.target.value)}
                  style={{
                    flex: 1,
                    height: "38px",
                    padding: "0 12px",
                    border: "1px solid var(--border, var(--cv-border))",
                    background: "var(--surface-2, var(--cv-bg-subtle))",
                    color: "var(--text, var(--cv-text))",
                    fontSize: "0.82rem",
                    borderRadius: "6px",
                    outline: "none",
                  }}
                />
                <button
                  type="button"
                  onClick={() => handleSyncSource("LeetCode", leetcodeUser)}
                  disabled={syncingSource === "LeetCode"}
                  style={{
                    padding: "0 14px",
                    height: "38px",
                    background: "var(--accent-soft, var(--cv-accent-soft))",
                    color: "var(--accent, var(--cv-accent))",
                    border: "1px solid var(--accent-border, var(--cv-accent-border))",
                    borderRadius: "6px",
                    fontSize: "0.8rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  <RefreshCw size={12} className={syncingSource === "LeetCode" ? "cv-spin" : ""} />
                  {syncingSource === "LeetCode" ? "Syncing…" : "Sync"}
                </button>
              </div>
            </div>

            {/* HackerRank Card */}
            <div
              style={{
                border: "1px solid var(--border, var(--cv-border))",
                borderRadius: "8px",
                padding: "20px",
                background: "var(--surface, var(--cv-surface))",
                display: "flex",
                flexDirection: "column",
                gap: "14px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <Trophy size={20} color="var(--accent, var(--cv-accent))" />
                  <strong style={{ fontSize: "0.95rem", color: "var(--text, var(--cv-text))" }}>HackerRank</strong>
                </div>
                {profile?.hackerrank_summary?.connected ? (
                  <span style={{ display: "inline-flex", alignItems: "center", gap: "4px", color: "var(--success, var(--cv-success))", fontSize: "0.72rem", fontWeight: 700 }}>
                    <Check size={12} /> CONNECTED
                  </span>
                ) : (
                  <span style={{ fontSize: "0.72rem", color: "var(--text-muted, var(--cv-muted))" }}>NOT CONNECTED</span>
                )}
              </div>

              <p style={{ fontSize: "0.78rem", color: "var(--text-muted, var(--cv-muted))", margin: 0, lineHeight: 1.45 }}>
                Sync badges, problem solving ranks, and domain mastery credentials.
              </p>

              <div style={{ display: "flex", gap: "8px" }}>
                <input
                  type="text"
                  placeholder="HackerRank username"
                  value={hackerrankUser}
                  onChange={(e) => setHackerrankUser(e.target.value)}
                  style={{
                    flex: 1,
                    height: "38px",
                    padding: "0 12px",
                    border: "1px solid var(--border, var(--cv-border))",
                    background: "var(--surface-2, var(--cv-bg-subtle))",
                    color: "var(--text, var(--cv-text))",
                    fontSize: "0.82rem",
                    borderRadius: "6px",
                    outline: "none",
                  }}
                />
                <button
                  type="button"
                  onClick={() => handleSyncSource("HackerRank", hackerrankUser)}
                  disabled={syncingSource === "HackerRank"}
                  style={{
                    padding: "0 14px",
                    height: "38px",
                    background: "var(--accent-soft, var(--cv-accent-soft))",
                    color: "var(--accent, var(--cv-accent))",
                    border: "1px solid var(--accent-border, var(--cv-accent-border))",
                    borderRadius: "6px",
                    fontSize: "0.8rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  <RefreshCw size={12} className={syncingSource === "HackerRank" ? "cv-spin" : ""} />
                  {syncingSource === "HackerRank" ? "Syncing…" : "Sync"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── CHAPTER FOOTER ──────────────────────────────────────────────── */}
      <footer className="cv-chapter-footer">
        <Link to="/profile"><ArrowLeft size={12} /> Chapter 01 · Your Story</Link>
        <span>02 / 08 · WORK &amp; SOURCES</span>
        <Link to="/career-discovery">Chapter 03 · Your Options <ArrowRight size={12} /></Link>
      </footer>
    </div>
  );
}
