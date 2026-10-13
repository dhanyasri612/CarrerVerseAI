import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  ArrowLeft,
  Activity,
  MapPin,
  BriefcaseBusiness,
  Pencil,
  GitBranch,
  Award,
  GraduationCap,
  RefreshCw,
  ShieldCheck,
  X,
  Check,
  ExternalLink,
  Code2,
  BookOpen,
  Plus,
  FileText,
  Upload,
  Sparkles,
  Layers,
  ChevronRight,
  CheckCircle2,
} from "lucide-react";
import { EmptyState, ErrorState, LoadingState } from "../components/AsyncState";
import { getApiError } from "../services/api";
import {
  clearProfileSnapshot,
  getProfileSnapshot,
  syncGithub,
  syncHackerRank,
  syncLeetCode,
  updateProfile,
  getCertifications,
  importGoogleDriveCert,
  uploadCertificate,
} from "../services/careerService";
import { CVButton } from "../design-system/components/CVButton";
import { CVDrawer } from "../design-system/components/CVDrawer";
import { CVInput, CVTextarea } from "../design-system/components/CVInputs";
import DsaPracticeModal from "../components/career/DsaPracticeModal";
import { recordActivity } from "../services/activityTracker";

const FIELDS = [
  ["name", "Full name", "text"],
  ["email", "Email", "email"],
  ["phone", "Phone", "tel"],
  ["college", "College", "text"],
  ["degree", "Degree", "text"],
  ["graduation_year", "Graduation year", "number"],
  ["location", "Location", "text"],
];

const list = (v) => (Array.isArray(v) ? v : []);
const display = (v, fb = "Not provided") => v || fb;

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [dbCerts, setDbCerts] = useState([]);
  const [form, setForm] = useState(null);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);
  const [editing, setEditing] = useState(false);

  // Section tabs
  const [activeTab, setActiveTab] = useState("overview"); // overview | github | dsa | certs | skills | exp

  // Modals
  const [showDsaModal, setShowDsaModal] = useState(false);
  const [showAddCertModal, setShowAddCertModal] = useState(false);

  // New Cert Form State
  const [newCertDriveUrl, setNewCertDriveUrl] = useState("");
  const [newCertName, setNewCertName] = useState("");
  const [newCertIssuer, setNewCertIssuer] = useState("");
  const [certActionLoading, setCertActionLoading] = useState(false);
  const [certActionMsg, setCertActionMsg] = useState("");

  const load = async ({ force = false } = {}) => {
    setError("");
    try {
      const [{ unified, basic }, certs] = await Promise.all([
        getProfileSnapshot({ force }),
        getCertifications().catch(() => []),
      ]);
      setProfile(unified);
      setForm(basic || unified.user_profile);
      setDbCerts(Array.isArray(certs) ? certs : []);
    } catch (err) {
      setError(getApiError(err, "Unable to load your profile."));
    }
  };

  useEffect(() => {
    load();
  }, []);

  const user = profile?.user_profile;
  const skills = profile?.unified_skills || [];
  const projects = profile?.projects || [];
  const experience = profile?.experience || [];
  const education = profile?.education || [];

  // Combine unified summary certs with database certs to guarantee nothing is missed
  const certifications = useMemo(() => {
    const fromSummary = profile?.certifications_summary?.items || [];
    const map = new Map();
    // Prefer database records
    dbCerts.forEach((c) => {
      const key = (c.certification_name || c.name || "").toLowerCase().trim();
      if (key) map.set(key, c);
    });
    fromSummary.forEach((c) => {
      const key = (c.certification_name || c.name || "").toLowerCase().trim();
      if (key && !map.has(key)) map.set(key, c);
    });
    return Array.from(map.values());
  }, [profile, dbCerts]);

  const completeness = profile?.completeness;
  const groupedSkills = profile?.skills_by_category || [];

  const lcSummary = profile?.leetcode_summary || {};
  const hrSummary = profile?.hackerrank_summary || {};
  const ghSummary = profile?.github_summary || {};

  const connectedCount = useMemo(
    () =>
      [
        ghSummary?.connected,
        profile?.linkedin_summary?.connected,
        lcSummary?.connected,
        hrSummary?.connected,
        profile?.resume_summary?.uploaded,
      ].filter(Boolean).length,
    [profile, ghSummary, lcSummary, hrSummary]
  );

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      const updated = await updateProfile(form);
      setForm(updated);
      setProfile((prev) => ({ ...prev, user_profile: { ...prev.user_profile, ...updated } }));
      setSaved(true);
      setEditing(false);
    } catch (err) {
      setError(getApiError(err, "Unable to save your profile."));
    } finally {
      setBusy(false);
    }
  };

  const syncSource = async (fn, label, defaultUser = "") => {
    const username = window.prompt(`Enter your ${label} username to connect & sync:`, defaultUser || "");
    if (!username || !username.trim()) return;
    setBusy(true);
    setError("");
    try {
      await fn(username.trim());
      await clearProfileSnapshot();
      await load({ force: true });
    } catch (err) {
      setError(getApiError(err, `Unable to sync ${label}. Please verify your username.`));
    } finally {
      setBusy(false);
    }
  };

  const handleDriveImport = async (e) => {
    e.preventDefault();
    if (!newCertDriveUrl.trim()) return;
    setCertActionLoading(true);
    setCertActionMsg("");
    try {
      await importGoogleDriveCert(
        newCertDriveUrl.trim(),
        newCertName.trim() || "Certificate.pdf"
      );
      setCertActionMsg("Certificate successfully imported and PDF skills parsed!");
      setNewCertDriveUrl("");
      setNewCertName("");
      setNewCertIssuer("");
      recordActivity({
        type: "cert",
        title: "Imported Certificate from Google Drive",
        detail: "Extracted verified credential metadata and skills from PDF",
      });
      await load({ force: true });
      setTimeout(() => {
        setShowAddCertModal(false);
        setCertActionMsg("");
      }, 1200);
    } catch (err) {
      setCertActionMsg(getApiError(err, "Could not import Google Drive certificate."));
    } finally {
      setCertActionLoading(false);
    }
  };

  if (!profile) {
    return error ? (
      <ErrorState message={error} onRetry={load} />
    ) : (
      <LoadingState label="Loading your career story…" />
    );
  }

  return (
    <div>
      {/* ─── CHAPTER INTRO ───────────────────────────────────────────────── */}
      <header className="cv-chapter-intro">
        <span className="cv-chapter-number">01 / 08</span>
        <div>
          <div className="cv-chapter-kicker">01 &nbsp; / &nbsp; Your Evidence Profile</div>
          <h1 className="cv-chapter-title">
            Your career,<br />
            <span className="serif">organized by evidence.</span>
          </h1>
          <p className="cv-chapter-deck">
            Cleanly segmented intelligence across GitHub repositories, LeetCode algorithms, verified certifications with Drive assets, and verified skills.
          </p>
        </div>
        <p className="cv-intro-aside">
          Evidence completeness: <strong>{completeness?.score ?? 0}%</strong> • {connectedCount} of 5 sources active
        </p>
      </header>

      {/* ─── SECTION NAVIGATION TAB BAR ──────────────────────────────────── */}
      <div
        style={{
          display: "flex",
          borderBottom: "1px solid #e2e8f0",
          background: "#ffffff",
          overflowX: "auto",
          gap: "8px",
          padding: "8px 0",
          marginBottom: "2rem",
          position: "sticky",
          top: "60px",
          zIndex: 10,
        }}
      >
        {[
          { id: "overview", label: "Overview & Signals" },
          { id: "certs", label: `Certifications & Drive (${certifications.length})` },
          { id: "dsa", label: `LeetCode & DSA (${lcSummary?.total_solved ?? 0})` },
          { id: "github", label: `GitHub Intelligence (${projects.length})` },
          { id: "skills", label: `Skills (${skills.length})` },
          { id: "exp", label: "Experience & Education" },
        ].map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: "8px 16px",
              borderRadius: "8px",
              border: "none",
              background: activeTab === tab.id ? "#0f172a" : "transparent",
              color: activeTab === tab.id ? "#fbbf24" : "#64748b",
              fontWeight: activeTab === tab.id ? 700 : 500,
              fontSize: "0.85rem",
              cursor: "pointer",
              whiteSpace: "nowrap",
              transition: "all 0.15s ease",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ─── TAB 1: OVERVIEW ─────────────────────────────────────────────── */}
      {activeTab === "overview" && (
        <>
          <section className="cv-editorial-section">
            <div className="cv-section-index">IDENTITY & STORY</div>
            <div className="cv-section-content">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <h2 style={{ margin: "0 0 6px 0" }}>{display(user?.name, "Your Profile")}</h2>
                  <p style={{ margin: 0, color: "#64748b" }}>
                    {display(user?.college)} • {display(user?.degree)} ({display(user?.graduation_year, "—")})
                  </p>
                </div>
                <button
                  type="button"
                  className="cv-text-button"
                  onClick={() => setEditing(true)}
                  style={{ border: "1px solid #cbd5e1", padding: "6px 14px", display: "inline-flex", alignItems: "center", gap: "6px" }}
                >
                  <Pencil size={13} /> Edit identity
                </button>
              </div>

              <div className="cv-evidence-lines" style={{ marginTop: "1.5rem" }}>
                <div className="cv-evidence-line">
                  <strong>Profile Readiness Score</strong>
                  <span style={{ fontWeight: 800, color: "#16a34a" }}>{completeness?.score ?? 0}%</span>
                </div>
                <div className="cv-evidence-line">
                  <strong>Email & Contact</strong>
                  <span>{display(user?.email)} • {display(user?.phone)}</span>
                </div>
                <div className="cv-evidence-line">
                  <strong>Location</strong>
                  <span>{display(user?.location)}</span>
                </div>
                <div className="cv-evidence-line">
                  <strong>Resume Asset</strong>
                  <span>{profile?.resume_summary?.uploaded ? "Uploaded and parsed" : "Not yet uploaded"}</span>
                </div>
              </div>
            </div>
          </section>

          {/* Connected Sources Strip */}
          <section className="cv-editorial-section">
            <div className="cv-section-index">SOURCE INTEGRATIONS</div>
            <div className="cv-section-content">
              <h2>Connected Evidence Feeds.</h2>
              <div className="cv-evidence-lines">
                <div className="cv-evidence-line">
                  <strong>GitHub</strong>
                  <span>
                    {ghSummary?.connected ? (
                      <span style={{ color: "#16a34a", display: "inline-flex", alignItems: "center", gap: "4px" }}>
                        <Check size={13} /> Connected ({ghSummary.username})
                      </span>
                    ) : (
                      <button className="cv-text-button" onClick={() => syncSource(syncGithub, "GitHub")}>
                        <RefreshCw size={12} /> Connect GitHub
                      </button>
                    )}
                  </span>
                </div>
                <div className="cv-evidence-line">
                  <strong>LeetCode</strong>
                  <span>
                    {lcSummary?.connected ? (
                      <span style={{ color: "#16a34a", display: "inline-flex", alignItems: "center", gap: "4px" }}>
                        <Check size={13} /> Connected ({lcSummary.username} • {lcSummary.total_solved} solved)
                      </span>
                    ) : (
                      <button className="cv-text-button" onClick={() => syncSource(syncLeetCode, "LeetCode")}>
                        <RefreshCw size={12} /> Connect LeetCode
                      </button>
                    )}
                  </span>
                </div>
                <div className="cv-evidence-line">
                  <strong>HackerRank</strong>
                  <span>
                    {hrSummary?.connected ? (
                      <span style={{ color: "#16a34a", display: "inline-flex", alignItems: "center", gap: "4px" }}>
                        <Check size={13} /> Connected ({hrSummary.username})
                      </span>
                    ) : (
                      <button className="cv-text-button" onClick={() => syncSource(syncHackerRank, "HackerRank")}>
                        <RefreshCw size={12} /> Connect HackerRank
                      </button>
                    )}
                  </span>
                </div>
              </div>
            </div>
          </section>
        </>
      )}

      {/* ─── TAB 2: CERTIFICATIONS & DRIVE ASSETS ─────────────────────────── */}
      {activeTab === "certs" && (
        <section className="cv-editorial-section">
          <div className="cv-section-index">CREDENTIALS & DRIVE</div>
          <div className="cv-section-content">
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
              <div>
                <h2 style={{ margin: "0 0 4px 0" }}>Verified Credentials & Drive Files</h2>
                <p style={{ margin: 0, color: "#64748b", fontSize: "0.9rem" }}>
                  Certificates attached through Google Drive links or parsed from PDF files.
                </p>
              </div>
              <button
                type="button"
                className="cv-opening-cta"
                onClick={() => setShowAddCertModal(true)}
                style={{ padding: "8px 16px", fontSize: "0.85rem" }}
              >
                <Plus size={14} /> Attach Drive Certificate
              </button>
            </div>

            {certifications.length === 0 ? (
              <div style={{ background: "#f8fafc", padding: "2.5rem", borderRadius: "12px", textAlign: "center", border: "1px dashed #cbd5e1" }}>
                <Award size={36} color="#94a3b8" style={{ marginBottom: "10px" }} />
                <h3 style={{ margin: "0 0 6px 0", color: "#0f172a" }}>No certifications attached yet</h3>
                <p style={{ margin: "0 0 16px 0", color: "#64748b", fontSize: "0.88rem" }}>
                  Attach a Google Drive share link or upload a PDF to extract certificate skills and credentials.
                </p>
                <button
                  type="button"
                  className="cv-opening-cta"
                  onClick={() => setShowAddCertModal(true)}
                >
                  <Plus size={14} /> Attach Drive Link or PDF
                </button>
              </div>
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "1.25rem" }}>
                {certifications.map((c, i) => {
                  const certTitle = c.certification_name || c.name || "Professional Certification";
                  const issuer = c.issuing_organization || c.issuer || c.provider || "Recognized Issuer";
                  const fileUrl = c.certificate_file_url || c.credential_url;
                  const skillsList = c.extracted_skills || [];
                  const isVerified = c.verification_status === "VERIFIED";

                  return (
                    <div
                      key={c.id || i}
                      style={{
                        background: "#ffffff",
                        border: "1px solid #e2e8f0",
                        borderRadius: "14px",
                        padding: "1.5rem",
                        boxShadow: "0 2px 5px rgba(0,0,0,0.03)",
                        display: "flex",
                        flexDirection: "column",
                        gap: "1rem",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", flexWrap: "wrap", gap: "10px" }}>
                        <div style={{ display: "flex", gap: "14px" }}>
                          <div
                            style={{
                              width: 44,
                              height: 44,
                              borderRadius: "10px",
                              background: "#fef3c7",
                              color: "#d97706",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              flexShrink: 0,
                            }}
                          >
                            <Award size={24} />
                          </div>
                          <div>
                            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                              <h3 style={{ margin: 0, fontSize: "1.1rem", color: "#0f172a", fontWeight: 700 }}>
                                {certTitle}
                              </h3>
                              <span
                                style={{
                                  fontSize: "0.72rem",
                                  padding: "2px 8px",
                                  borderRadius: "12px",
                                  background: isVerified ? "#dcfce7" : "#fef3c7",
                                  color: isVerified ? "#15803d" : "#b45309",
                                  fontWeight: 700,
                                }}
                              >
                                {isVerified ? "✓ Verified Credential" : "Verification Pending"}
                              </span>
                            </div>
                            <div style={{ fontSize: "0.85rem", color: "#64748b", marginTop: "3px" }}>
                              <strong>{issuer}</strong> {c.issue_date && <> • Issued {c.issue_date}</>}
                              {c.credential_id && <> • ID: <code>{c.credential_id}</code></>}
                            </div>
                          </div>
                        </div>

                        {fileUrl && (
                          <a
                            href={fileUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "6px",
                              padding: "7px 14px",
                              borderRadius: "8px",
                              background: "#0f172a",
                              color: "#fbbf24",
                              fontSize: "0.82rem",
                              fontWeight: 600,
                              textDecoration: "none",
                              boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                            }}
                          >
                            <ExternalLink size={13} />
                            Open in Google Drive / PDF
                          </a>
                        )}
                      </div>

                      {/* PDF Extracted Skills */}
                      {skillsList.length > 0 && (
                        <div style={{ background: "#f8fafc", padding: "10px 14px", borderRadius: "8px", border: "1px solid #f1f5f9" }}>
                          <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748b", textTransform: "uppercase", marginBottom: "6px", display: "flex", alignItems: "center", gap: "5px" }}>
                            <Sparkles size={12} color="#f59e0b" /> Extracted Skills from PDF Content:
                          </div>
                          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                            {skillsList.map((sk, ski) => (
                              <span
                                key={ski}
                                style={{
                                  fontSize: "0.78rem",
                                  padding: "3px 10px",
                                  borderRadius: "6px",
                                  border: "1px solid #e2e8f0",
                                  background: "#ffffff",
                                  color: "#334155",
                                  fontWeight: 600,
                                }}
                              >
                                {sk}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </section>
      )}

      {/* ─── TAB 3: LEETCODE & HACKERRANK DSA ─────────────────────────────── */}
      {activeTab === "dsa" && (
        <section className="cv-editorial-section">
          <div className="cv-section-index">ALGORITHMIC MASTERY</div>
          <div className="cv-section-content">
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.25rem" }}>
              <div>
                <h2 style={{ margin: "0 0 4px 0" }}>LeetCode & HackerRank Problem Solving</h2>
                <p style={{ margin: 0, color: "#64748b", fontSize: "0.9rem" }}>
                  Connected stats generate personalized similar-style practice problems and adaptive DSA roadmaps.
                </p>
              </div>
              <Link
                to="/dsa-practice"
                className="cv-opening-cta"
                style={{ padding: "8px 16px", fontSize: "0.85rem", textDecoration: "none" }}
              >
                <Code2 size={14} /> Open DSA Practice & Roadmap
              </Link>
            </div>

            {/* Solved Stats Grid */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
              <div style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "12px", padding: "1.25rem", textAlign: "center" }}>
                <div style={{ fontSize: "0.8rem", color: "#64748b", fontWeight: 700 }}>TOTAL SOLVED</div>
                <div style={{ fontSize: "2rem", fontWeight: 800, color: "#0f172a" }}>{lcSummary?.total_solved || 0}</div>
                <div style={{ fontSize: "0.78rem", color: "#64748b" }}>LeetCode verified</div>
              </div>
              <div style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "12px", padding: "1.25rem", textAlign: "center" }}>
                <div style={{ fontSize: "0.8rem", color: "#16a34a", fontWeight: 700 }}>EASY</div>
                <div style={{ fontSize: "2rem", fontWeight: 800, color: "#16a34a" }}>{lcSummary?.easy_solved || 0}</div>
                <div style={{ fontSize: "0.78rem", color: "#64748b" }}>Foundational</div>
              </div>
              <div style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "12px", padding: "1.25rem", textAlign: "center" }}>
                <div style={{ fontSize: "0.8rem", color: "#ca8a04", fontWeight: 700 }}>MEDIUM</div>
                <div style={{ fontSize: "2rem", fontWeight: 800, color: "#ca8a04" }}>{lcSummary?.medium_solved || 0}</div>
                <div style={{ fontSize: "0.78rem", color: "#64748b" }}>Core interview standard</div>
              </div>
              <div style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "12px", padding: "1.25rem", textAlign: "center" }}>
                <div style={{ fontSize: "0.8rem", color: "#dc2626", fontWeight: 700 }}>HARD</div>
                <div style={{ fontSize: "2rem", fontWeight: 800, color: "#dc2626" }}>{lcSummary?.hard_solved || 0}</div>
                <div style={{ fontSize: "0.78rem", color: "#64748b" }}>Advanced subproblems</div>
              </div>
            </div>

            <div style={{ background: "#f8fafc", padding: "1.5rem", borderRadius: "12px", border: "1px solid #e2e8f0", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div>
                <h4 style={{ margin: "0 0 4px 0", color: "#0f172a" }}>Adaptive DSA Problem Generator Ready</h4>
                <p style={{ margin: 0, fontSize: "0.88rem", color: "#64748b" }}>
                  The agent creates questions identical in flavor to your weak topics (DP, Graphs, Binary Search) with step-by-step hints and roadmap progression.
                </p>
              </div>
              <Link
                to="/dsa-practice"
                className="cv-opening-cta"
                style={{ textDecoration: "none" }}
              >
                Open DSA Studio &rarr;
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* ─── TAB 4: GITHUB INTELLIGENCE ─────────────────────────────────── */}
      {activeTab === "github" && (
        <section className="cv-editorial-section">
          <div className="cv-section-index">CODE & REPOSITORIES</div>
          <div className="cv-section-content">
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
              <div>
                <h2 style={{ margin: "0 0 4px 0" }}>GitHub Engineering Portfolio</h2>
                <p style={{ margin: 0, color: "#64748b", fontSize: "0.9rem" }}>
                  Synced repositories, commit evidence, and primary technologies.
                </p>
              </div>
              <button
                type="button"
                className="cv-text-button"
                onClick={() => syncSource(syncGithub, "GitHub", ghSummary?.username)}
                style={{ border: "1px solid #cbd5e1", padding: "6px 14px" }}
              >
                <RefreshCw size={13} /> Re-sync GitHub
              </button>
            </div>

            {projects.length === 0 ? (
              <p>No repositories analyzed yet. Sync your GitHub username to populate project evidence.</p>
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "10px" }}>
                {projects.map((p, i) => (
                  <div
                    key={i}
                    style={{
                      background: "#ffffff",
                      border: "1px solid #e2e8f0",
                      borderRadius: "10px",
                      padding: "1rem 1.25rem",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <div>
                      <strong style={{ fontSize: "0.95rem", color: "#0f172a" }}>
                        {p.title || p.name || p.repo_name}
                      </strong>
                      <div style={{ fontSize: "0.82rem", color: "#64748b", marginTop: "2px" }}>
                        {p.language || p.primary_language || "Code repository"}
                        {p.stars !== undefined && ` • ⭐ ${p.stars} stars`}
                      </div>
                    </div>
                    {p.repo_url && (
                      <a
                        href={p.repo_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{ color: "#2563eb", fontSize: "0.82rem", textDecoration: "none", display: "inline-flex", alignItems: "center", gap: "4px" }}
                      >
                        View code <ExternalLink size={12} />
                      </a>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      )}

      {/* ─── TAB 5: SKILLS ─────────────────────────────────────────────── */}
      {activeTab === "skills" && (
        <section className="cv-editorial-section">
          <div className="cv-section-index">SKILLS INDEX</div>
          <div className="cv-section-content">
            <h2 style={{ margin: "0 0 4px 0" }}>Verified Skills & Interview Cheat Sheets</h2>
            <p style={{ margin: "0 0 1.5rem 0", color: "#64748b", fontSize: "0.9rem" }}>
              Click any skill badge to inspect its <strong>Top 5 Interview Questions</strong>, model answers, and practical challenge.
            </p>

            {groupedSkills.length > 0 ? (
              groupedSkills.map((group) => (
                <div key={group.category} style={{ marginBottom: "1.5rem" }}>
                  <div style={{ fontSize: "0.78rem", fontWeight: 700, letterSpacing: "0.08em", color: "#64748b", textTransform: "uppercase", marginBottom: "0.5rem" }}>
                    {group.category}
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                    {list(group.skills).map((s) => (
                      <span
                        key={s.name}
                        style={{
                          border: "1px solid #cbd5e1",
                          padding: "6px 12px",
                          fontSize: "0.85rem",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "6px",
                          background: "#ffffff",
                          borderRadius: "6px",
                          fontWeight: 600,
                          color: "#1e293b",
                        }}
                      >
                        <CheckCircle2 size={13} color="#10b981" />
                        {s.name}
                      </span>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                {skills.map((s) => (
                  <span
                    key={s.name}
                    style={{
                      border: "1px solid #cbd5e1",
                      padding: "6px 12px",
                      borderRadius: "6px",
                      background: "#ffffff",
                      fontSize: "0.84rem",
                      fontWeight: 600,
                      color: "#334155",
                    }}
                  >
                    {s.name}
                  </span>
                ))}
              </div>
            )}
          </div>
        </section>
      )}

      {/* ─── TAB 6: EXPERIENCE & EDUCATION ───────────────────────────────── */}
      {activeTab === "exp" && (
        <>
          {experience.length > 0 && (
            <section className="cv-editorial-section">
              <div className="cv-section-index">EXPERIENCE</div>
              <div className="cv-section-content">
                <h2>Professional Trajectory</h2>
                <div className="cv-evidence-lines">
                  {experience.map((exp, i) => (
                    <div className="cv-evidence-line" key={i}>
                      <strong>
                        {exp.title || exp.role} {exp.company ? `— ${exp.company}` : ""}
                      </strong>
                      <span>{exp.start_date || exp.duration || ""}</span>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          )}

          {education.length > 0 && (
            <section className="cv-editorial-section">
              <div className="cv-section-index">EDUCATION</div>
              <div className="cv-section-content">
                <h2>Academic Foundation</h2>
                <div className="cv-evidence-lines">
                  {education.map((e, i) => (
                    <div className="cv-evidence-line" key={i}>
                      <strong>{e.degree || e.qualification || "Degree"}</strong>
                      <span>{e.institution || e.college || e.graduation_year || ""}</span>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          )}
        </>
      )}

      {/* ─── MODAL: ATTACH GOOGLE DRIVE CERTIFICATE ──────────────────────── */}
      {showAddCertModal && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 9999,
            background: "rgba(15, 23, 42, 0.75)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "1.5rem",
          }}
          onClick={() => setShowAddCertModal(false)}
        >
          <div
            style={{
              background: "#ffffff",
              width: "100%",
              maxWidth: "540px",
              borderRadius: "14px",
              padding: "2rem",
              boxShadow: "0 20px 40px rgba(0,0,0,0.2)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.25rem" }}>
              <h3 style={{ margin: 0, fontSize: "1.2rem", color: "#0f172a" }}>Attach Google Drive Certificate</h3>
              <button
                type="button"
                onClick={() => setShowAddCertModal(false)}
                style={{ border: "none", background: "none", cursor: "pointer" }}
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleDriveImport} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 700, color: "#475569", marginBottom: "4px" }}>
                  Google Drive Shareable Link (or public URL)
                </label>
                <input
                  type="url"
                  required
                  placeholder="https://drive.google.com/file/d/.../view"
                  value={newCertDriveUrl}
                  onChange={(e) => setNewCertDriveUrl(e.target.value)}
                  style={{ width: "100%", padding: "10px 12px", border: "1px solid #cbd5e1", borderRadius: "6px", outline: "none" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 700, color: "#475569", marginBottom: "4px" }}>
                  Certificate / Course Title
                </label>
                <input
                  type="text"
                  placeholder="e.g. Meta Front-End Developer Certificate"
                  value={newCertName}
                  onChange={(e) => setNewCertName(e.target.value)}
                  style={{ width: "100%", padding: "10px 12px", border: "1px solid #cbd5e1", borderRadius: "6px", outline: "none" }}
                />
              </div>

              {certActionMsg && (
                <div style={{ fontSize: "0.85rem", color: certActionMsg.includes("success") ? "#16a34a" : "#dc2626" }}>
                  {certActionMsg}
                </div>
              )}

              <div style={{ display: "flex", gap: "10px", marginTop: "8px" }}>
                <button
                  type="submit"
                  className="cv-opening-cta"
                  disabled={certActionLoading || !newCertDriveUrl}
                >
                  {certActionLoading ? "Importing & Parsing PDF..." : "Import & Parse Skills"}
                </button>
                <button
                  type="button"
                  className="cv-text-button"
                  onClick={() => setShowAddCertModal(false)}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}



    </div>
  );
}
