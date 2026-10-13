/**
 * CareerVerse Dashboard — Reimagined as the "Opening" editorial chapter.
 * Enhanced with Daily Work & Streak Tracker, LeetCode/HackerRank DSA launcher,
 * and real-time evidence synthesis.
 */

import { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Activity,
  Flame,
  CheckCircle2,
  Code2,
  Brain,
  Calendar,
  Sparkles,
  Zap,
} from "lucide-react";
import { getProfileSnapshot, getJobs } from "../services/careerService";
import { useAuth } from "../context/AuthContext";
import { CHAPTERS } from "../components/LayoutReimagined";
import { getActivityMetrics } from "../services/activityTracker";
import DsaPracticeModal from "../components/career/DsaPracticeModal";
import MonthlyStreakTracker from "../components/MonthlyStreakTracker";

export default function DashboardReimagined() {
  const { user } = useAuth();
  const [snapshot, setSnapshot] = useState(null);
  const [jobCount, setJobCount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showDsaModal, setShowDsaModal] = useState(false);
  const [activityMetrics, setActivityMetrics] = useState(() => getActivityMetrics());
  const [showAllActivities, setShowAllActivities] = useState(false);

  // Group duplicate activities and sort latest first
  const aggregatedTodayActivities = useMemo(() => {
    const list = activityMetrics.todayActivities || [];
    const map = new Map();
    list.forEach((act) => {
      const key = (act.title || "Session").trim();
      if (!map.has(key)) {
        map.set(key, {
          ...act,
          count: 1,
          latestTimestamp: act.timestamp,
        });
      } else {
        const existing = map.get(key);
        existing.count += 1;
        if (new Date(act.timestamp) > new Date(existing.latestTimestamp)) {
          existing.latestTimestamp = act.timestamp;
        }
      }
    });
    return Array.from(map.values()).sort(
      (a, b) => new Date(b.latestTimestamp) - new Date(a.latestTimestamp)
    );
  }, [activityMetrics.todayActivities]);

  useEffect(() => {
    let cancelled = false;
    Promise.all([getProfileSnapshot(), getJobs()])
      .then(([snap, jobs]) => {
        if (cancelled) return;
        setSnapshot(snap);
        setJobCount(Array.isArray(jobs) ? jobs.length : 0);
      })
      .catch(() => {
        if (!cancelled) setError("Profile signals unavailable.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Refresh activity metrics on focus
  useEffect(() => {
    const handleFocus = () => setActivityMetrics(getActivityMetrics());
    window.addEventListener("focus", handleFocus);
    return () => window.removeEventListener("focus", handleFocus);
  }, []);

  const profile = snapshot?.unified;
  const basic = snapshot?.basic || profile?.user_profile || {};
  const firstName = basic?.name?.split(" ")[0] || user?.name?.split(" ")[0] || "there";

  const skills = profile?.unified_skills?.length ?? null;
  const projects = profile?.projects?.length ?? null;
  const experience = profile?.experience?.length ?? null;
  const resume = profile?.resume_summary?.uploaded;
  const github = profile?.github_summary?.connected;
  const lcSolved = profile?.leetcode_summary?.total_solved ?? null;
  const certs = profile?.certifications_summary?.total_certifications ?? null;

  const signalItems = [
    ["Verified skills", skills, "Normalized across all connected sources"],
    ["Projects", projects, "Parsed from resume and GitHub repositories"],
    ["LeetCode solved", lcSolved !== null ? lcSolved : "Connect LeetCode", "Algorithmic practice count"],
    ["Experience roles", experience, "Extracted and deduplicated"],
    ["Open roles", jobCount, "In the available jobs catalogue"],
    ["Certifications", certs, "Verified credentials with Drive assets"],
  ];

  const missingSections = profile?.completeness?.missing_sections || [];
  const nextMove = !resume
    ? "Upload a resume to ground your AI career profile in verified evidence."
    : missingSections.length > 0
    ? `Strengthen evidence in ${missingSections[0]} to unlock more targeted directions.`
    : "Explore role directions in Career Navigator to map what comes next.";

  return (
    <div className="cv2-page">
      {/* ── Opening intro ─────────────────────────────────────────────── */}
      <section className="cv2-chapter-intro opening">
        <div>
          <div className="cv2-chapter-kicker">AN OPENING NOTE</div>
          <h1 className="cv2-chapter-title">
            {firstName ? (
              <>
                Good to see you, <span className="serif">{firstName}.</span>
              </>
            ) : (
              <>
                Your career<br />
                is already<br />
                <span className="serif">a story.</span>
              </>
            )}
          </h1>
          <p className="cv2-chapter-deck">
            CareerVerse connects the real evidence across your work, projects, skills, and practice to help you decide what comes next.
          </p>
          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap", alignItems: "center" }}>
            <Link to="/career-discovery" className="cv2-opening-cta">
              Launch Career Navigator <ArrowRight size={16} />
            </Link>
            <Link
              to="/dsa-practice"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                padding: "8px 16px",
                background: "#0f172a",
                color: "#fbbf24",
                borderRadius: "8px",
                textDecoration: "none",
                fontWeight: 600,
                fontSize: "0.85rem",
                boxShadow: "0 2px 8px rgba(15, 23, 42, 0.15)",
              }}
            >
              <Code2 size={15} /> Daily DSA Practice & Roadmap <ArrowRight size={13} />
            </Link>
          </div>
        </div>

        {/* Abstract orbital mark */}
        <div className="cv2-opening-mark" role="img" aria-label="An abstract editorial mark suggesting career paths">
          <span>
            Career<br />
            in motion
          </span>
        </div>

        <p className="cv2-intro-aside">
          Start with what is real. Move at your own pace.
          {error && (
            <>
              {" "}
              • <span style={{ color: "var(--cv-warning)" }}>{error}</span>
            </>
          )}
        </p>
      </section>

      {/* ── DAILY WORK & PROGRESS TRACKER (NEW REQUIREMENT) ───────────── */}
      <section className="cv2-editorial">
        <div className="cv2-section-index">DAILY WORK & HABITS</div>
        <div className="cv2-section-content">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "10px", marginBottom: "1rem" }}>
            <div>
              <h2 style={{ margin: "0 0 4px 0" }}>Daily Momentum & Activity Tracking</h2>
              <p style={{ margin: 0, color: "var(--cv-muted)", fontSize: "0.9rem" }}>
                Tracks every interview practice round, DSA problem solved, and roadmap milestone completed.
              </p>
            </div>

            {/* Streak Flame Pill */}
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                background: "linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%)",
                border: "1px solid #fdba74",
                padding: "8px 16px",
                borderRadius: "20px",
                color: "#9a3412",
                fontWeight: 800,
                fontSize: "0.92rem",
              }}
            >
              <Flame size={18} color="#ea580c" />
              <span>{activityMetrics.streak}-Day Active Streak</span>
            </div>
          </div>

          {/* Monthly Consistency & Streak Calendar (LeetCode / GeeksforGeeks Style) */}
          <MonthlyStreakTracker onOpenDsaModal={() => setShowDsaModal(true)} />

          {/* Today's Completed Work — Compact & Sleek */}
          <div
            style={{
              background: "#ffffff",
              border: "1px solid #e2e8f0",
              borderRadius: "14px",
              padding: "1rem 1.25rem",
              boxShadow: "0 1px 3px rgba(0,0,0,0.02)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <strong style={{ fontSize: "0.88rem", color: "#0f172a" }}>
                  Today's Activity
                </strong>
                {activityMetrics.todayCount > 0 && (
                  <span
                    style={{
                      background: "#dcfce7",
                      color: "#15803d",
                      fontSize: "0.72rem",
                      fontWeight: 700,
                      padding: "2px 8px",
                      borderRadius: "12px",
                      border: "1px solid #86efac",
                    }}
                  >
                    ✓ {activityMetrics.todayCount} completed
                  </span>
                )}
              </div>
              <span style={{ fontSize: "0.74rem", color: "#64748b" }}>
                Auto-synced
              </span>
            </div>

            {aggregatedTodayActivities.length === 0 ? (
              <p style={{ margin: "0 0 10px 0", fontSize: "0.82rem", color: "#64748b" }}>
                No sessions completed yet today. Complete an interview or practice a DSA problem to extend your streak!
              </p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginBottom: "10px" }}>
                {(showAllActivities ? aggregatedTodayActivities : aggregatedTodayActivities.slice(0, 3)).map((act, idx) => (
                  <div
                    key={act.id || idx}
                    style={{
                      background: "#f8fafc",
                      border: "1px solid #e2e8f0",
                      padding: "6px 10px",
                      borderRadius: "8px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      gap: "10px",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", minWidth: 0, overflow: "hidden" }}>
                      <CheckCircle2 size={14} color="#16a34a" style={{ flexShrink: 0 }} />
                      <span
                        style={{
                          fontSize: "0.82rem",
                          fontWeight: 600,
                          color: "#0f172a",
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                        }}
                        title={act.title}
                      >
                        {act.title}
                      </span>
                      {act.count > 1 && (
                        <span
                          style={{
                            background: "#e0e7ff",
                            color: "#4338ca",
                            fontSize: "0.68rem",
                            fontWeight: 800,
                            padding: "1px 6px",
                            borderRadius: "10px",
                            flexShrink: 0,
                          }}
                        >
                          ×{act.count}
                        </span>
                      )}
                    </div>
                    <span style={{ fontSize: "0.72rem", color: "#94a3b8", flexShrink: 0 }}>
                      {new Date(act.latestTimestamp || act.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                ))}

                {aggregatedTodayActivities.length > 3 && (
                  <button
                    type="button"
                    onClick={() => setShowAllActivities(!showAllActivities)}
                    style={{
                      background: "none",
                      border: "none",
                      color: "#4f46e5",
                      fontSize: "0.74rem",
                      fontWeight: 700,
                      cursor: "pointer",
                      padding: "2px 4px",
                      alignSelf: "flex-start",
                    }}
                  >
                    {showAllActivities
                      ? "Show less ▲"
                      : `+${aggregatedTodayActivities.length - 3} more activities ▼`}
                  </button>
                )}
              </div>
            )}

            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", paddingTop: "4px" }}>
              <Link
                to="/dsa-practice"
                className="cv2-opening-cta"
                style={{ padding: "5px 12px", fontSize: "0.78rem", textDecoration: "none" }}
              >
                <Code2 size={13} /> Practice DSA
              </Link>
              <Link
                to="/ai/interview"
                className="cv2-text-link"
                style={{ padding: "5px 12px", border: "1px solid #cbd5e1", borderRadius: "8px", textDecoration: "none", fontSize: "0.78rem" }}
              >
                <Brain size={13} /> Voice Interview
              </Link>
              <Link
                to="/career-roadmap"
                className="cv2-text-link"
                style={{ padding: "5px 12px", border: "1px solid #cbd5e1", borderRadius: "8px", textDecoration: "none", fontSize: "0.78rem" }}
              >
                <Zap size={13} /> Roadmap Tech Tree
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ── Career signals editorial section ──────────────────────────── */}
      <section className="cv2-editorial">
        <div className="cv2-section-index">YOUR CURRENT SIGNAL</div>
        <div className="cv2-section-content">
          <h2>
            {loading ? (
              "Reading your profile…"
            ) : skills ? (
              <>
                Your profile holds {skills} verified {skills === 1 ? "skill" : "skills"} across {projects ?? "—"}{" "}
                {projects === 1 ? "project" : "projects"}.
              </>
            ) : (
              <>Your story is waiting for its first chapter.</>
            )}
          </h2>
          <p>
            {loading
              ? "Connecting to profile services…"
              : "Signal strength depends on the number of sources connected and the evidence they carry."}
          </p>

          {/* Evidence lines */}
          {!loading && (
            <div className="cv2-evidence-lines">
              {signalItems.map(([label, value, detail]) => (
                <div className="cv2-evidence-line" key={label}>
                  <strong>{label}</strong>
                  <span>{value !== null ? `${value} • ${detail}` : "Not yet connected"}</span>
                </div>
              ))}
            </div>
          )}

          {loading && (
            <div className="cv2-loading" style={{ marginTop: "24px" }}>
              <span className="cv2-spinner" />
              <span>Loading profile signals…</span>
            </div>
          )}
        </div>
      </section>

      {/* ── Next best move ─────────────────────────────────────────────── */}
      <section className="cv2-editorial">
        <div className="cv2-section-index">NEXT BEST MOVE</div>
        <div className="cv2-section-content">
          <h2>One concrete step forward.</h2>
          <p>{nextMove}</p>

          {!resume && (
            <div className="cv2-note" style={{ marginTop: "28px" }}>
              <Activity size={17} />
              <div>
                <strong>Resume not yet connected.</strong>
                Uploading a resume immediately enriches your skill, project, and experience signals.
              </div>
            </div>
          )}

          <div className="cv2-action-row">
            <Link to={resume ? "/career-discovery" : "/resume"} className="cv2-text-link">
              {resume ? "Explore career directions" : "Upload your resume"}
              <ArrowRight size={14} />
            </Link>
            <Link to="/ai/intelligence" className="cv2-text-link">
              Career Intelligence report
              <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      </section>

      {/* ── Chapter index ──────────────────────────────────────────────── */}
      <section className="cv2-editorial">
        <div className="cv2-section-index">THE CHAPTERS</div>
        <div className="cv2-section-content">
          <h2>
            Begin anywhere.<br />
            Follow what feels useful.
          </h2>
          <p>
            Each chapter asks a different question about how your experience connects to what might come next.
          </p>
          <div className="cv2-chapter-index-list">
            {CHAPTERS.map((c) => (
              <Link key={c.key} to={c.href} className="cv2-chapter-row">
                <span className="cv2-row-number">{c.number}</span>
                <span className="cv2-row-label">{c.label}</span>
                <ArrowRight size={14} />
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer nav ─────────────────────────────────────────────────── */}
      <div className="cv2-chapter-footer">
        <span>CAREERVERSE • A CAREER IN MOTION</span>
        <Link to="/profile">
          Begin with your story <ArrowRight size={13} />
        </Link>
      </div>

    </div>
  );
}
