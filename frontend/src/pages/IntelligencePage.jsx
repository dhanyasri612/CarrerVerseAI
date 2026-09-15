import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import FeaturePage from "../components/FeaturePage";
import { EmptyState, ErrorState, LoadingState } from "../components/AsyncState";
import { getApiError } from "../services/api";
import {
  getJobs,
  getParsedResume,
  getRecommendations,
  getResumes,
  getRoadmap,
  getResumeImprovement,
  getSkillGap,
  syncGithub,
} from "../services/careerService";

const pageSettings = {
  analysis: [
    "Resume analysis",
    "Understand the signal in your resume",
    "A structured view of the information extracted from your latest PDF.",
  ],
  "skill-gap": [
    "Skill gap analysis",
    "See what moves you closer",
    "Compare your resume with a target role from the platform.",
  ],
  recommendations: [
    "Career recommendations",
    "Roles that fit your signal",
    "Recommendations are ranked against your resume skills.",
  ],
  roadmap: [
    "Career roadmap",
    "Turn missing skills into a plan",
    "Follow the next learning steps for a selected role.",
  ],
  github: [
    "GitHub integration",
    "Bring your public work into the picture",
    "Sync a GitHub profile to enrich your career intelligence.",
  ],
  improvement: [
    "Resume improvement",
    "Make your resume stronger",
    "Get actionable suggestions for a target role.",
  ],
};

function DataList({ items }) {
  return items?.length ? (
    <ul className="clean-list">
      {items.map((item, index) => (
        <li key={`${item}-${index}`}>{String(item)}</li>
      ))}
    </ul>
  ) : (
    <p className="muted-copy">Nothing reported yet.</p>
  );
}

function SourcePicker({
  resumes,
  jobs,
  resumeId,
  jobId,
  setResumeId,
  setJobId,
}) {
  return (
    <div className="source-picker panel-card">
      <label>
        Resume
        <select
          value={resumeId}
          onChange={(event) => setResumeId(event.target.value)}
        >
          {resumes.map((resume) => (
            <option key={resume.id} value={resume.id}>
              {resume.file_name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Target role
        <select
          value={jobId}
          onChange={(event) => setJobId(event.target.value)}
        >
          {jobs.map((job) => (
            <option key={job.id} value={job.id}>
              {job.title} · {job.company}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}

export default function IntelligencePage({ mode }) {
  const [data, setData] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [resumeId, setResumeId] = useState("");
  const [jobId, setJobId] = useState("");
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [key, setKey] = useState("");
  const [eyebrow, title, description] =
    pageSettings[mode] || pageSettings.analysis;

  useEffect(() => {
    async function loadSources() {
      setLoading(true);
      try {
        const resumeData = await getResumes();
        setResumes(resumeData);
        if (resumeData[0]) setResumeId(String(resumeData[0].id));
        if (mode !== "analysis" && mode !== "github") {
          const jobData = await getJobs();
          setJobs(jobData);
          if (jobData[0]) setJobId(String(jobData[0].id));
        }
      } catch (err) {
        setError(getApiError(err, "Unable to load the data for this view."));
      } finally {
        setLoading(false);
      }
    }
    loadSources();
  }, [mode]);

  useEffect(() => {
    if (!resumeId || (mode !== "analysis" && mode !== "github" && !jobId))
      return;
    const requestKey = `${mode}:${resumeId}:${jobId}`;
    if (key === requestKey) return;
    async function loadData() {
      try {
        let result;
        if (mode === "analysis") result = await getParsedResume(resumeId);
        if (mode === "recommendations")
          result = await getRecommendations(resumeId);
        if (mode === "skill-gap") result = await getSkillGap(resumeId, jobId);
        if (mode === "roadmap") result = await getRoadmap(resumeId, jobId);
        if (mode === "improvement")
          result = await getResumeImprovement(resumeId, jobId);
        setData(result);
        setKey(requestKey);
      } catch (err) {
        setError(getApiError(err, "This analysis is not available yet."));
      }
    }
    loadData();
  }, [mode, resumeId, jobId, key]);

  const handleSync = async (event) => {
    event.preventDefault();
    if (!username.trim()) return;
    setBusy(true);
    setError("");
    try {
      setData(await syncGithub(username.trim()));
    } catch (err) {
      setError(getApiError(err, "Unable to sync this GitHub profile."));
    } finally {
      setBusy(false);
    }
  };

  const noSources =
    !resumes.length ||
    (mode !== "analysis" && mode !== "github" && !jobs.length);
  return (
    <FeaturePage eyebrow={eyebrow} title={title} description={description}>
      {mode === "github" ? (
        <>
          <form className="panel-card inline-form" onSubmit={handleSync}>
            <label>
              GitHub username
              <input
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="octocat"
              />
            </label>
            <button className="primary-button" disabled={busy}>
              {busy ? "Syncing..." : "Sync profile"}
            </button>
          </form>
          {error ? <ErrorState message={error} /> : null}
          {data ? (
            <GithubResult data={data} />
          ) : (
            <EmptyState title="Connect a GitHub profile">
              Repositories, languages, and activity will appear after a
              successful sync.
            </EmptyState>
          )}
        </>
      ) : loading ? (
        <LoadingState />
      ) : noSources ? (
        <EmptyState
          title={
            !resumes.length
              ? "Upload a resume first"
              : "No target jobs available"
          }
          action={
            !resumes.length ? (
              <Link className="primary-button" to="/resume">
                Upload resume
              </Link>
            ) : null
          }
        >
          This backend workflow needs the source data before it can calculate
          results.
        </EmptyState>
      ) : (
        <>
          {mode !== "analysis" ? (
            <SourcePicker
              {...{ resumes, jobs, resumeId, jobId, setResumeId, setJobId }}
            />
          ) : null}
          {error ? <ErrorState message={error} /> : null}
          {!data ? <LoadingState /> : <Result mode={mode} data={data} />}
        </>
      )}
    </FeaturePage>
  );
}

function GithubResult({ data }) {
  return (
    <div className="content-grid two-columns">
      <div className="panel-card">
        <span className="eyebrow">@{data.username}</span>
        <h3>GitHub profile synced</h3>
        <div className="github-stats">
          <strong>{data.total_repositories} repos</strong>
          <strong>{data.total_stars} stars</strong>
          <strong>{data.total_forks} forks</strong>
        </div>
        <a href={data.profile_url} target="_blank" rel="noreferrer">
          Open GitHub profile
        </a>
      </div>
      <div className="panel-card">
        <h3>Languages</h3>
        <div className="tag-list">
          {(data.languages || []).map((item) => (
            <span className="tag" key={item}>
              {item}
            </span>
          ))}
        </div>
        <h3 className="subheading">Topics</h3>
        <div className="tag-list">
          {(data.topics || []).map((item) => (
            <span className="tag" key={item}>
              {item}
            </span>
          ))}
        </div>
      </div>
      <div className="panel-card full-span">
        <h3>Repositories</h3>
        {(data.repositories || []).length ? (
          <div className="content-grid two-columns">
            {data.repositories.map((repo) => (
              <article className="repo-row" key={repo.name}>
                <strong>{repo.name}</strong>
                <p>{repo.description || "No description provided."}</p>
                <span>
                  {repo.language || "Project"} · {repo.stars || 0} stars ·{" "}
                  {repo.forks || 0} forks
                </span>
              </article>
            ))}
          </div>
        ) : (
          <p className="muted-copy">No public repositories returned.</p>
        )}
      </div>
    </div>
  );
}

function Result({ mode, data }) {
  if (mode === "analysis")
    return (
      <div className="analysis-grid">
        {[
          ["Personal information", [data.name, data.email, data.phone]],
          ["Education", data.education],
          ["Skills", data.skills],
          ["Experience", data.experience],
          ["Projects", data.projects],
          ["Certifications", data.certifications],
        ].map(([label, items]) => (
          <div className="panel-card" key={label}>
            <h3>{label}</h3>
            <DataList items={items} />
          </div>
        ))}
      </div>
    );
  if (mode === "recommendations")
    return (
      <div className="content-grid two-columns">
        {data.length ? (
          data.map((item) => (
            <div className="panel-card" key={item.job_id}>
              <span className="eyebrow">{item.company}</span>
              <h3>{item.title}</h3>
              <strong className="score-value">
                {item.match_percentage}% match
              </strong>
              <p>Matched skills</p>
              <div className="tag-list">
                {item.matched_skills.map((skill) => (
                  <span className="tag" key={skill}>
                    {skill}
                  </span>
                ))}
              </div>
              <p>Missing: {item.missing_skills.join(", ") || "None"}</p>
            </div>
          ))
        ) : (
          <EmptyState title="No recommendations yet" />
        )}
      </div>
    );
  if (mode === "skill-gap")
    return (
      <div className="content-grid two-columns">
        <div className="panel-card">
          <h3>Match score</h3>
          <strong className="score-value">{data.match_percentage}%</strong>
          <div className="progress-track">
            <span style={{ width: `${data.match_percentage}%` }} />
          </div>
        </div>
        <div className="panel-card">
          <h3>Matched skills</h3>
          <DataList items={data.matched_skills} />
        </div>
        <div className="panel-card">
          <h3>Missing skills</h3>
          <DataList items={data.missing_skills} />
        </div>
      </div>
    );
  if (mode === "improvement")
    return (
      <div className="content-grid three-columns">
        {[
          ["Strengths", data.strengths],
          ["Current issues", data.weaknesses],
          ["Suggestions", data.suggestions],
        ].map(([label, items]) => (
          <div className="panel-card" key={label}>
            <h3>{label}</h3>
            <DataList items={items} />
          </div>
        ))}
      </div>
    );
  return (
    <div className="content-grid two-columns">
      <div className="panel-card">
        <h3>Current skills</h3>
        <DataList items={data.current_skills} />
      </div>
      <div className="panel-card">
        <h3>Skills to learn</h3>
        <DataList items={data.missing_skills} />
      </div>
      <div className="roadmap-list full-span">
        {data.roadmap.length ? (
          data.roadmap.map((step) => (
            <div className="panel-card roadmap-step" key={step.step}>
              <span className="step-number">{step.step}</span>
              <div>
                <h3>{step.skill}</h3>
                <p>{step.description}</p>
              </div>
            </div>
          ))
        ) : (
          <EmptyState title="You are aligned with this role" />
        )}
      </div>
    </div>
  );
}
