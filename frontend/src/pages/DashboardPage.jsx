import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { EmptyState, ErrorState, LoadingState } from "../components/AsyncState";
import { getApiError } from "../services/api";
import { getJobs, getProfile, getResumes } from "../services/careerService";

export default function DashboardPage() {
  const [state, setState] = useState(null);
  const [error, setError] = useState("");
  const load = async () => {
    setError("");
    try {
      const [profile, resumes, jobs] = await Promise.all([
        getProfile(),
        getResumes(),
        getJobs(),
      ]);
      setState({ profile, resumes, jobs });
    } catch (err) {
      setError(getApiError(err, "Unable to load your career intelligence."));
    }
  };
  useEffect(() => {
    load();
  }, []);
  if (!state && !error)
    return <LoadingState label="Building your career intelligence..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;
  const { profile, resumes, jobs } = state;
  const resume = resumes[0];
  const firstName = profile.name?.split(" ")[0] || "there";
  return (
    <div className="dashboard-page">
      <div className="section-header compact">
        <p className="eyebrow">Overview</p>
        <h2>Good to see you, {firstName}</h2>
        <p className="page-description">
          Your workspace is ready for the next career decision.
        </p>
      </div>
      <div className="stats-grid">
        <div className="stat-card tone-purple">
          <span>Profile focus</span>
          <strong>{profile.degree || "In progress"}</strong>
        </div>
        <div className="stat-card tone-blue">
          <span>Resume status</span>
          <strong>{resume ? "Ready" : "Missing"}</strong>
        </div>
        <div className="stat-card tone-teal">
          <span>Target roles</span>
          <strong>{jobs.length}</strong>
        </div>
        <div className="stat-card tone-orange">
          <span>Profile fields</span>
          <strong>
            {
              [
                profile.phone,
                profile.college,
                profile.degree,
                profile.location,
                profile.bio,
              ].filter(Boolean).length
            }
            /5
          </strong>
        </div>
      </div>
      <div className="content-grid two-columns">
        <div className="panel-card">
          <h3>Profile summary</h3>
          <p>
            {profile.bio ||
              "Add a short bio so CareerVerse can understand your direction."}
          </p>
          <Link className="text-link" to="/profile">
            Update profile
          </Link>
        </div>
        <div className="panel-card">
          <h3>Resume signal</h3>
          <p>
            {resume
              ? `${resume.file_name} is ${resume.parsed_status ? "parsed and ready" : "uploaded and ready to parse"}.`
              : "Upload a PDF to unlock analysis, recommendations, and a roadmap."}
          </p>
          <Link
            className="primary-button"
            to={resume ? "/resume-analysis" : "/resume"}
          >
            {resume ? "View analysis" : "Upload resume"}
          </Link>
        </div>
      </div>
      <div className="content-grid three-columns">
        <div className="panel-card">
          <h3>Skills overview</h3>
          <EmptyState title="Build your skill profile">
            Parse your resume to see extracted skills.
          </EmptyState>
        </div>
        <div className="panel-card">
          <h3>Skill gap</h3>
          <p>
            Compare your resume against one of {jobs.length} available roles.
          </p>
          <Link className="text-link" to="/skill-gap">
            Open skill gap
          </Link>
        </div>
        <div className="panel-card">
          <h3>GitHub activity</h3>
          <p>
            Sync a public profile to add projects, languages, and repository
            signals.
          </p>
          <Link className="text-link" to="/github">
            Connect GitHub
          </Link>
        </div>
      </div>
    </div>
  );
}
