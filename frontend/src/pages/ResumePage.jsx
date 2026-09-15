import { useEffect, useRef, useState } from "react";
import FeaturePage from "../components/FeaturePage";
import { EmptyState, ErrorState, LoadingState } from "../components/AsyncState";
import {
  deleteResume,
  getResumes,
  parseResume,
  uploadResume,
} from "../services/careerService";
import { getApiError } from "../services/api";
import { Link } from "react-router-dom";

export default function ResumePage() {
  const inputRef = useRef(null);
  const [resumes, setResumes] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const load = async () => {
    setError("");
    try {
      setResumes(await getResumes());
    } catch (err) {
      setError(getApiError(err, "Unable to load your resumes."));
    }
  };
  useEffect(() => {
    load();
  }, []);
  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    if (file.type !== "application/pdf") {
      setError("Only PDF files are allowed by the backend.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await uploadResume(file);
      await load();
    } catch (err) {
      setError(getApiError(err, "Resume upload failed."));
    } finally {
      setBusy(false);
    }
  };
  const handleDelete = async (id) => {
    setBusy(true);
    setError("");
    try {
      await deleteResume(id);
      await load();
    } catch (err) {
      setError(getApiError(err, "Unable to delete this resume."));
    } finally {
      setBusy(false);
    }
  };
  const handleParse = async (id) => {
    setBusy(true);
    setError("");
    try {
      await parseResume(id);
      await load();
    } catch (err) {
      setError(getApiError(err, "Unable to parse this resume."));
    } finally {
      setBusy(false);
    }
  };
  return (
    <FeaturePage
      eyebrow="Resume intelligence"
      title="Turn your resume into a career signal"
      description="Upload a PDF to make your profile available to the platform's analysis workflows."
    >
      <div className="panel-card upload-panel">
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          onChange={handleUpload}
          hidden
        />
        <div>
          <span className="eyebrow">PDF only</span>
          <h3>
            {busy ? "Processing your file..." : "Upload your latest resume"}
          </h3>
          <p>
            Keep one current resume available for recommendations and roadmap
            analysis.
          </p>
        </div>
        <button
          className="primary-button"
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={busy}
        >
          {busy ? "Working..." : "Choose PDF"}
        </button>
      </div>
      {error ? <ErrorState message={error} onRetry={load} /> : null}
      {!resumes ? (
        <LoadingState />
      ) : resumes.length === 0 ? (
        <EmptyState title="No resume uploaded yet">
          Upload a PDF to unlock resume-backed career intelligence.
        </EmptyState>
      ) : (
        <div className="resume-list">
          {resumes.map((resume) => (
            <div className="panel-card resume-item" key={resume.id}>
              <div>
                <strong>{resume.file_name}</strong>
                <span>
                  {resume.parsed_status
                    ? "Parsed"
                    : "Uploaded, awaiting parsing"}{" "}
                  · {Math.ceil(resume.file_size / 1024)} KB
                </span>
              </div>
              <div className="row-actions">
                <button
                  className="ghost-button"
                  type="button"
                  onClick={() => handleParse(resume.id)}
                  disabled={busy}
                >
                  {resume.parsed_status ? "Reparse" : "Parse resume"}
                </button>
                {resume.parsed_status ? (
                  <Link className="ghost-button" to="/resume-analysis">
                    Analysis
                  </Link>
                ) : null}
                <button
                  className="text-button danger-text"
                  type="button"
                  onClick={() => handleDelete(resume.id)}
                  disabled={busy}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </FeaturePage>
  );
}
