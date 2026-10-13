import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, Sparkles, Activity, ShieldCheck } from "lucide-react";
import { getProfileSnapshot } from "../services/careerService";
import { getApiError } from "../services/api";
import { useAuth } from "../context/AuthContext";

/* ─── EDITORIAL SECTION PRIMITIVE ────────────────────────────────────────── */
function EditorialSection({ index, title, body, note, list }) {
  return (
    <section className="cv-editorial-section">
      <div className="cv-section-index">{index}</div>
      <div className="cv-section-content">
        <h2>{title}</h2>
        <p>{body}</p>
        {note && (
          <div className="cv-note-block">
            <Activity size={16} />
            <div>
              <strong>Connected.</strong>{note}
            </div>
          </div>
        )}
        {list && (
          <div className="cv-evidence-lines">
            {list.map(([label, detail], i) => (
              <div className="cv-evidence-line" key={i}>
                <strong>{label}</strong>
                <span>{detail}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

/* ─── DASHBOARD / HOME OPENING ────────────────────────────────────────────── */
export default function DashboardPage() {
  const { user }       = useAuth();
  const navigate       = useNavigate();
  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState("");

  const firstName = user?.name?.split(" ")[0] || snapshot?.basic?.name?.split(" ")[0] || "Candidate";

  useEffect(() => {
    getProfileSnapshot()
      .then((data) => setSnapshot(data))
      .catch((err) => setError(getApiError(err, "")))
      .finally(() => setLoading(false));
  }, []);

  const profile   = snapshot?.unified;
  const skills    = profile?.unified_skills     || [];
  const projects  = profile?.projects           || [];
  const resume    = profile?.resume_summary;
  const connected = [
    resume?.uploaded,
    Boolean(profile?.github_summary?.connected),
    Boolean(profile?.leetcode_summary?.connected),
    Boolean(profile?.hackerrank_summary?.connected),
  ].filter(Boolean).length;

  return (
    <div>
      {/* ─── OPENING HERO ──────────────────────────────────────────────────── */}
      <section className="cv-chapter-intro opening">
        <span className="cv-chapter-number">AN OPENING NOTE</span>

        <div>
          <div className="cv-chapter-kicker">A personal career operating system</div>
          <h1 className="cv-chapter-title">
            {firstName}'s career<br />
            is already<br />
            <span className="serif">a story.</span>
          </h1>
          <p className="cv-chapter-deck">
            CareerVerse helps you understand what your experience says
            about where you could go next—grounded in real evidence,
            not a generated summary.
          </p>
          <Link to="/profile" className="cv-opening-cta">
            Enter your career <ArrowRight size={15} />
          </Link>
        </div>

        <div>
          <div className="cv-opening-mark" role="img" aria-label="Abstract editorial mark suggesting paths through a story">
            <span>Experience<br />in motion</span>
          </div>
          <p className="cv-intro-aside">
            Start with what is real. Move at your own pace. Leave room for
            the parts of your story still taking shape.
          </p>
        </div>
      </section>

      {/* ─── LIVE CAREER SIGNALS ──────────────────────────────────────────── */}
      <EditorialSection
        index="YOUR SIGNALS"
        title={<>The evidence you have already built.</>}
        body="CareerVerse reads across your verified resume, GitHub contributions, certifications, and practice sessions to build a picture of what your experience actually says."
        list={[
          ["Verified skills",      loading ? "Loading…" : skills.length > 0 ? `${skills.length} skills normalized` : "Connect a source to populate"],
          ["Project evidence",     loading ? "Loading…" : projects.length > 0 ? `${projects.length} projects analyzed` : "Link GitHub to begin"],
          ["Connected sources",    loading ? "Loading…" : `${connected} of 4 active`],
          ["Career readiness",     loading ? "Loading…" : resume?.uploaded ? "Resume uploaded and parsed" : "Upload a resume to ground your profile"],
        ]}
      />

      {/* ─── THE CHAPTERS ─────────────────────────────────────────────────── */}
      <section className="cv-editorial-section">
        <div className="cv-section-index">THE CHAPTERS</div>
        <div className="cv-section-content">
          <h2>Begin anywhere.<br />Follow what feels useful.</h2>
          <p>Each chapter asks a different question about how your experience connects to what might come next.</p>
          <div className="cv-chapter-index-list">
            {[
              { number: "01", label: "Your Story",     to: "/profile" },
              { number: "02", label: "Your Options",   to: "/career-discovery" },
              { number: "03", label: "Your Gaps",      to: "/skill-gap" },
              { number: "04", label: "Your Journey",   to: "/career-roadmap" },
              { number: "05", label: "Cyra Vance",     to: "/ai/interview" },
              { number: "06", label: "Career Mirror",  to: "/ai/intelligence" },
            ].map((ch) => (
              <Link key={ch.to} to={ch.to} className="cv-chapter-index-row">
                <span className="row-number">{ch.number}</span>
                <span className="row-label">{ch.label}</span>
                <ArrowRight size={13} />
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ─── NEXT BEST MOVE ───────────────────────────────────────────────── */}
      <EditorialSection
        index="NEXT BEST MOVE"
        title={<>The clearest step forward right now.</>}
        body={
          !resume?.uploaded
            ? "Upload your verified resume to ground your AI career profile. Everything else—skill gap, roadmap, and Dr. Cyra Vance—becomes more precise once your evidence is in."
            : skills.length === 0
            ? "Your resume is in. Connect GitHub to add project evidence and unlock role-specific skill comparisons."
            : "Your profile has enough signal to explore role directions. Open Career Navigator to see where your current experience could take you."
        }
        note={null}
      />

      {/* ─── A NOTE ON EVIDENCE ───────────────────────────────────────────── */}
      <EditorialSection
        index="A NOTE ON EVIDENCE"
        title={<>Nothing personal is invented for you.</>}
        body="Every signal shown in CareerVerse is traceable to a source you connected. If a section appears empty, it is because the evidence is not there yet—not because it was hidden or replaced with a placeholder."
      />

      {/* ─── FOOTER ───────────────────────────────────────────────────────── */}
      <footer className="cv-chapter-footer">
        <span>CAREERVERSE · A CAREER IN MOTION</span>
        <Link to="/profile">Begin with your story <ArrowRight size={12} /></Link>
      </footer>
    </div>
  );
}
