import React, { useEffect, useState } from "react";
import { Link, useLocation, useSearchParams } from "react-router-dom";
import { ArrowRight, ArrowLeft, Activity, ShieldCheck, Target, Sparkles } from "lucide-react";
import { getApiError } from "../services/api";
import { getSkillGapAnalysis } from "../services/careerService";
import { LoadingState, ErrorState } from "../components/AsyncState";

function ESection({ index, title, body, note, list, children }) {
  return (
    <section className="cv-editorial-section">
      <div className="cv-section-index">{index}</div>
      <div className="cv-section-content">
        <h2>{title}</h2>
        {body && <p>{body}</p>}
        {note && (
          <div className="cv-note-block">
            <Activity size={16} />
            <div><strong>Status.</strong>{note}</div>
          </div>
        )}
        {list && (
          <div className="cv-evidence-lines">
            {list.map(([label, detail], i) => (
              <div className="cv-evidence-line" key={i}>
                <strong>{label}</strong><span>{detail}</span>
              </div>
            ))}
          </div>
        )}
        {children}
      </div>
    </section>
  );
}

const DEFAULT_ROLES = [
  "Full Stack Developer",
  "Software Developer",
  "Data Scientist",
  "Machine Learning Engineer",
  "Frontend Developer",
  "Backend Developer",
  "UI/UX Designer",
  "AI & NLP Engineer",
];

export default function SkillGapPage() {
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();

  const queryRole = searchParams.get("role");
  const stateRole = location.state?.targetRole;
  const storedRole = typeof window !== "undefined" ? sessionStorage.getItem("careerverse_target_role") : null;
  const activeRole = queryRole || stateRole || storedRole || "Full Stack Developer";

  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState("");

  // Gather available roles from discovery if user visited discovery page
  const discoveredRoles = React.useMemo(() => {
    try {
      const stored = sessionStorage.getItem("careerverse_discovered_roles");
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }, []);

  const availableRoles = React.useMemo(() => {
    const list = [...discoveredRoles, activeRole, ...DEFAULT_ROLES].filter(Boolean);
    return Array.from(new Set(list));
  }, [discoveredRoles, activeRole]);

  const load = async (roleToLoad) => {
    const target = roleToLoad || activeRole;
    setLoading(true);
    setError("");
    try {
      const result = await getSkillGapAnalysis(target);
      setData(result);
    } catch (err) {
      setError(getApiError(err, `Unable to load skill gap analysis for ${target}.`));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(activeRole);
  }, [activeRole]);

  const handleRoleSelect = (roleName) => {
    if (roleName === activeRole && !error && !loading) return;
    sessionStorage.setItem("careerverse_target_role", roleName);
    setSearchParams({ role: roleName });
  };

  const analysis      = data?.skill_gap_analysis || data || {};
  const rawGaps       = Array.isArray(analysis.skill_gaps) ? analysis.skill_gaps : [];
  
  const matched = (Array.isArray(analysis.matched_skills) && analysis.matched_skills.length > 0)
    ? analysis.matched_skills
    : rawGaps.filter(g => g.status === "demonstrated" || g.gap_level === "none")
        .map(g => ({ name: g.skill, source: (g.evidence_sources || []).join(", ") || "Verified Profile", evidence: (g.candidate_evidence || []).join(", ") || "Demonstrated" }))
        .concat((Array.isArray(analysis.strengths) ? analysis.strengths : []).map(s => typeof s === "string" ? { name: s, source: "Profile Evidence", evidence: "Demonstrated" } : s));

  const missing = (Array.isArray(analysis.missing_skills) && analysis.missing_skills.length > 0)
    ? analysis.missing_skills
    : rawGaps.filter(g => g.status === "missing" || g.gap_level === "high")
        .map(g => ({ name: g.skill, priority: g.gap_level ? `${g.gap_level.toUpperCase()} Priority` : "Required", explanation: g.explanation }));

  const partial = (Array.isArray(analysis.partial_skills) && analysis.partial_skills.length > 0)
    ? analysis.partial_skills
    : rawGaps.filter(g => g.status === "partially_demonstrated" || g.gap_level === "medium" || g.gap_level === "low")
        .map(g => ({ name: g.skill, gap: g.explanation || "Developing", explanation: g.explanation }));

  const targetRole    = analysis.target_role || activeRole || "Software Developer";
  const totalCount    = matched.length + missing.length + partial.length;
  const readiness     = analysis.readiness_score
    || analysis.overall_readiness
    || (totalCount > 0 ? Math.round((matched.length / totalCount) * 100) / 100 : 0.5);

  if (loading && !data) return <LoadingState label={`Analyzing skills for ${activeRole}…`} />;
  if (error && !data)   return <ErrorState message={error} onRetry={() => load(activeRole)} />;

  return (
    <div>
      {/* ─── CHAPTER INTRO ───────────────────────────────────────────────── */}
      <header className="cv-chapter-intro">
        <span className="cv-chapter-number">03 / 06</span>
        <div>
          <div className="cv-chapter-kicker">03 &nbsp; / &nbsp; Your Gaps</div>
          <h1 className="cv-chapter-title">A useful gap is a distance<br /><span className="serif">with context.</span></h1>
          <p className="cv-chapter-deck">
            Skills should not be marked present, developing, or missing without
            both your evidence and requirements from a chosen direction.
          </p>
        </div>
        <p className="cv-intro-aside">
          {activeRole
            ? `Comparing your profile against: ${activeRole}`
            : "Select a target role in Career Navigator to ground this comparison."
          }
        </p>
      </header>

      {/* ─── DIRECTION SELECTOR ─────────────────────────────────────────── */}
      <section className="cv-editorial-section" style={{ borderBottom: "1px solid var(--cv-rule, rgba(0,0,0,0.08))", paddingBottom: "1.25rem" }}>
        <div className="cv-section-index">TARGET DIRECTION</div>
        <div className="cv-section-content">
          <p style={{ margin: "0 0 0.75rem", fontSize: "var(--cv-text-body-sm)", color: "var(--cv-muted)" }}>
            Select a career direction to evaluate your current profile against its specific requirements:
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", alignItems: "center" }}>
            {availableRoles.map((roleName) => {
              const isActive = roleName.toLowerCase() === activeRole.toLowerCase();
              return (
                <button
                  key={roleName}
                  onClick={() => handleRoleSelect(roleName)}
                  disabled={loading}
                  style={{
                    cursor: loading ? "wait" : "pointer",
                    padding: "7px 16px",
                    borderRadius: "20px",
                    border: isActive ? "1.5px solid var(--cv-ink, #1f1d1a)" : "1px solid var(--cv-rule, #dcd7ce)",
                    background: isActive ? "var(--cv-ink, #1f1d1a)" : "transparent",
                    color: isActive ? "#faf7f2" : "var(--cv-ink, #1f1d1a)",
                    fontSize: "0.85rem",
                    fontWeight: isActive ? 600 : 400,
                    transition: "all 0.15s ease",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  {isActive && <Sparkles size={13} />}
                  {roleName}
                </button>
              );
            })}
          </div>
          {loading && (
            <p style={{ color: "var(--cv-muted)", fontSize: "0.82rem", marginTop: "0.5rem" }}>
              Evaluating requirements for {activeRole}…
            </p>
          )}
        </div>
      </section>

      <div style={{ opacity: loading ? 0.45 : 1, pointerEvents: loading ? "none" : "auto", transition: "opacity 0.25s ease" }}>
        {/* ─── READINESS SIGNAL ────────────────────────────────────────────── */}
        {readiness != null && totalCount > 0 ? (
          <ESection
            index="READINESS SIGNAL"
            title={<>Your current standing for this direction.</>}
            list={[
              ["Role target",     targetRole || activeRole],
              ["Readiness score", typeof readiness === "number" ? `${Math.round(readiness * 100)}%` : readiness],
              ["Skills matched",  `${matched.length} skills evidenced`],
              ["Skills missing",  `${missing.length} gaps identified`],
              ["Skills partial",  `${partial.length} skills developing`],
            ]}
          />
        ) : null}

        {/* ─── ALREADY EVIDENCED ───────────────────────────────────────────── */}
        <section className="cv-editorial-section">
          <div className="cv-section-index">ALREADY EVIDENCED</div>
          <div className="cv-section-content">
            <h2>What you can already demonstrate.</h2>
            <p>Skills with evidence in your profile, traceable to a source you connected.</p>
            {matched.length === 0
              ? <div className="cv-note-block"><ShieldCheck size={16} /><div><strong>No matched skills yet.</strong>Connect a resume or GitHub to populate this section.</div></div>
              : <div className="cv-evidence-lines">
                  {matched.map((s, i) => {
                    const sName = typeof s === "string" ? s : s.name;
                    return (
                      <div className="cv-evidence-line" key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div>
                          <strong>{sName}</strong>
                          <span style={{ marginLeft: "8px", fontSize: "0.82rem", color: "#64748b" }}>{s.source || s.evidence || "Evidenced"}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
            }
          </div>
        </section>

        {/* ─── STILL DEVELOPING ────────────────────────────────────────────── */}
        {partial.length > 0 && (
          <section className="cv-editorial-section">
            <div className="cv-section-index">STILL DEVELOPING</div>
            <div className="cv-section-content">
              <h2>Skills where evidence is partial or emerging.</h2>
              <div className="cv-evidence-lines">
                {partial.map((s, i) => {
                  const sName = typeof s === "string" ? s : s.name;
                  return (
                    <div className="cv-evidence-line" key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div>
                        <strong>{sName}</strong>
                        <span style={{ marginLeft: "8px", fontSize: "0.82rem", color: "#64748b" }}>{s.gap || "Partial evidence"}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </section>
        )}

        {/* ─── NOT YET EVIDENCED ───────────────────────────────────────────── */}
        <section className="cv-editorial-section">
          <div className="cv-section-index">NOT YET EVIDENCED</div>
          <div className="cv-section-content">
            <h2>Requirements not yet in your profile.</h2>
            <p>These are requirements from the target role that your current evidence does not yet cover.</p>
            {missing.length === 0
              ? <p style={{ color: "var(--cv-success)" }}>No critical gaps detected for this role direction.</p>
              : <div className="cv-evidence-lines">
                  {missing.map((s, i) => {
                    const sName = typeof s === "string" ? s : s.name;
                    return (
                      <div className="cv-evidence-line" key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div>
                          <strong>{sName}</strong>
                          <span style={{ marginLeft: "8px", fontSize: "0.82rem", color: "#b45309" }}>{s.priority || s.importance || "Required"}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
            }
          </div>
        </section>
      </div>

      {/* ─── ACTION ROW ──────────────────────────────────────────────────── */}
      <div className="cv-action-row">
        <Link to="/career-discovery" className="cv-text-link">Return to possible directions <ArrowRight size={14} /></Link>
        <Link
          to={`/career-roadmap?role=${encodeURIComponent(targetRole || activeRole)}`}
          state={{ targetRole: targetRole || activeRole }}
          className="cv-text-link"
        >
          Continue to your journey for {targetRole || activeRole} <ArrowRight size={14} />
        </Link>
      </div>



      <footer className="cv-chapter-footer">
        <Link to="/career-discovery"><ArrowLeft size={12} /> Your Options</Link>
        <span>03 / 06</span>
        <Link to={`/career-roadmap?role=${encodeURIComponent(targetRole || activeRole)}`}>Your Journey &nbsp; 04 <ArrowRight size={12} /></Link>
      </footer>
    </div>
  );
}
