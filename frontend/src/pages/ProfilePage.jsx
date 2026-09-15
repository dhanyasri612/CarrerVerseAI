import { useEffect, useState } from "react";
import FeaturePage from "../components/FeaturePage";
import { ErrorState, LoadingState } from "../components/AsyncState";
import { getProfile, updateProfile } from "../services/careerService";
import { getApiError } from "../services/api";

const fields = [
  ["name", "Full name"],
  ["email", "Email"],
  ["phone", "Phone"],
  ["college", "College"],
  ["degree", "Degree"],
  ["graduation_year", "Graduation year"],
  ["location", "Location"],
  ["bio", "Bio"],
];

export default function ProfilePage() {
  const [form, setForm] = useState(null);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);
  const load = async () => {
    try {
      setForm(await getProfile());
    } catch (err) {
      setError(getApiError(err, "Unable to load your profile."));
    }
  };
  useEffect(() => {
    load();
  }, []);
  const submit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      setForm(await updateProfile(form));
      setSaved(true);
    } catch (err) {
      setError(getApiError(err, "Unable to save your profile."));
    } finally {
      setBusy(false);
    }
  };
  return (
    <FeaturePage
      eyebrow="Your profile"
      title="Keep your career context current"
      description="These fields are the profile data supported by the backend and used by intelligence services."
    >
      {!form ? (
        error ? (
          <ErrorState message={error} onRetry={load} />
        ) : (
          <LoadingState />
        )
      ) : (
        <form className="panel-card profile-form" onSubmit={submit}>
          {fields.map(([name, label]) => (
            <label key={name}>
              {label}
              {name === "bio" ? (
                <textarea
                  rows="4"
                  value={form[name] || ""}
                  onChange={(e) => setForm({ ...form, [name]: e.target.value })}
                />
              ) : (
                <input
                  type={
                    name === "email"
                      ? "email"
                      : name === "graduation_year"
                        ? "number"
                        : "text"
                  }
                  value={form[name] || ""}
                  onChange={(e) => setForm({ ...form, [name]: e.target.value })}
                />
              )}
            </label>
          ))}
          {error ? <div className="form-message error">{error}</div> : null}
          {saved ? (
            <div className="form-message success">Profile saved.</div>
          ) : null}
          <button className="primary-button" type="submit" disabled={busy}>
            {busy ? "Saving..." : "Save profile"}
          </button>
        </form>
      )}
    </FeaturePage>
  );
}
