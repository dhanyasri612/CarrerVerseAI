import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Orbit, User, Mail, Phone, Lock, Eye, EyeOff,
  ArrowRight, ShieldCheck, Sparkles, AlertCircle, CheckCircle2
} from "lucide-react";
import { registerUser } from "../services/authService";
import { getApiError } from "../services/api";
import { useTheme } from "../context/ThemeContext";

export default function RegisterPage() {
  const navigate = useNavigate();
  const { theme, setTheme } = useTheme?.() || { theme: "paper", setTheme: () => {} };

  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const getPasswordStrength = () => {
    const p = form.password;
    if (!p) return 0;
    let score = 0;
    if (p.length >= 6) score++;
    if (p.length >= 10 || (/[A-Z]/.test(p) && /[0-9]/.test(p))) score++;
    if (/[^A-Za-z0-9]/.test(p) && p.length >= 8) score++;
    return Math.min(score, 3);
  };

  const strength = getPasswordStrength();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!form.name.trim()) {
      setError("Please enter your full name.");
      return;
    }
    if (!form.email.trim()) {
      setError("Please provide a valid email address.");
      return;
    }
    if (!form.password || form.password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);

    try {
      await registerUser(form);
      navigate("/login", { state: { registeredEmail: form.email } });
    } catch (err) {
      setError(getApiError(err, "Registration could not be completed."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="cv-auth-shell">
      {/* Editorial Left Brand Sidebar */}
      <aside className="cv-auth-sidebar">
        <div className="cv-auth-brand-row">
          <Link to="/" className="cv-auth-brand-logo">
            <div className="cv-auth-brand-icon">
              <Orbit size={20} />
            </div>
            <div>
              <div className="cv-auth-brand-title">CareerVerse AI</div>
              <div className="cv-auth-brand-tag">Intelligence Dossier</div>
            </div>
          </Link>

          <div style={{ display: "flex", gap: "6px" }}>
            {["paper", "black", "clay", "cinema"].map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setTheme && setTheme(t)}
                title={`Theme: ${t}`}
                style={{
                  width: "18px",
                  height: "18px",
                  borderRadius: "50%",
                  border: theme === t ? "2px solid var(--cv-text)" : "1px solid var(--cv-rule)",
                  background:
                    t === "paper" ? "#f1eee4" :
                    t === "black" ? "#11141c" :
                    t === "clay"  ? "#eee3d5" : "#1c1b18",
                  cursor: "pointer",
                  padding: 0,
                }}
              />
            ))}
          </div>
        </div>

        <div className="cv-auth-sidebar-body">
          <div className="cv-auth-kicker">
            <Sparkles size={14} /> Chapter 00 · Candidate Ingestion
          </div>
          <h1 className="cv-auth-headline">
            Your career is not a template. <span className="serif">It is an evolving dossier.</span>
          </h1>

          <div className="cv-auth-feature-list">
            <div className="cv-auth-feature-item">
              <span className="cv-auth-feature-num">01</span>
              <div className="cv-auth-feature-text">
                <h4>Multi-Agent Synthesis</h4>
                <p>8 specialized AI agents analyze your real profile, code, and trajectory without hallucination.</p>
              </div>
            </div>

            <div className="cv-auth-feature-item">
              <span className="cv-auth-feature-num">02</span>
              <div className="cv-auth-feature-text">
                <h4>Verified Evidence Grounding</h4>
                <p>Direct sync with GitHub, LeetCode, and HackerRank to substantiate every claimed skill.</p>
              </div>
            </div>

            <div className="cv-auth-feature-item">
              <span className="cv-auth-feature-num">03</span>
              <div className="cv-auth-feature-text">
                <h4>Alex — Realistic Mock Practice</h4>
                <p>Targeted interview simulations with live evaluation and question-by-question coaching.</p>
              </div>
            </div>
          </div>
        </div>

        <div className="cv-auth-sidebar-footer">
          <span>Grounded Intelligence Framework</span>
          <span>Volume I · Edition 2026</span>
        </div>
      </aside>

      {/* Form Content Right Pane */}
      <main className="cv-auth-content-pane">
        <div className="cv-auth-form-wrapper">
          <div className="cv-auth-card">
            <div className="cv-auth-card-header">
              <span className="cv-auth-card-kicker">01 / Create Dossier</span>
              <h2 className="cv-auth-card-title">Begin your journey.</h2>
              <p className="cv-auth-card-subtitle">
                Create your CareerVerse account to map your verified skills, gaps, and career trajectories.
              </p>
            </div>

            {error && (
              <div className="cv-auth-error-banner" role="alert" style={{ marginBottom: "18px" }}>
                <AlertCircle size={18} style={{ flexShrink: 0, marginTop: "2px" }} />
                <div>{error}</div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="cv-auth-form">
              <div className="cv-auth-field">
                <label className="cv-auth-label" htmlFor="reg-name">
                  Full Name
                </label>
                <div className="cv-auth-input-wrap">
                  <span className="cv-auth-input-icon">
                    <User size={16} />
                  </span>
                  <input
                    id="reg-name"
                    name="name"
                    type="text"
                    className="cv-auth-input"
                    style={{ paddingLeft: "44px" }}
                    value={form.name}
                    onChange={handleChange}
                    placeholder="e.g. Jane Doe"
                    autoComplete="name"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="cv-auth-field">
                <label className="cv-auth-label" htmlFor="reg-email">
                  Email Address
                </label>
                <div className="cv-auth-input-wrap">
                  <span className="cv-auth-input-icon">
                    <Mail size={16} />
                  </span>
                  <input
                    id="reg-email"
                    name="email"
                    type="email"
                    className="cv-auth-input"
                    style={{ paddingLeft: "44px" }}
                    value={form.email}
                    onChange={handleChange}
                    placeholder="you@example.com"
                    autoComplete="email"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="cv-auth-field">
                <label className="cv-auth-label" htmlFor="reg-phone">
                  Phone Number
                  <span className="cv-auth-label-opt">(optional)</span>
                </label>
                <div className="cv-auth-input-wrap">
                  <span className="cv-auth-input-icon">
                    <Phone size={16} />
                  </span>
                  <input
                    id="reg-phone"
                    name="phone"
                    type="tel"
                    className="cv-auth-input"
                    style={{ paddingLeft: "44px" }}
                    value={form.phone}
                    onChange={handleChange}
                    placeholder="(555) 000-0000"
                    autoComplete="tel"
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="cv-auth-field">
                <label className="cv-auth-label" htmlFor="reg-password">
                  Password
                </label>
                <div className="cv-auth-input-wrap">
                  <span className="cv-auth-input-icon">
                    <Lock size={16} />
                  </span>
                  <input
                    id="reg-password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    className="cv-auth-input"
                    style={{ paddingLeft: "44px", paddingRight: "42px" }}
                    value={form.password}
                    onChange={handleChange}
                    placeholder="At least 6 characters"
                    autoComplete="new-password"
                    required
                    disabled={loading}
                  />
                  <button
                    type="button"
                    className="cv-auth-input-toggle"
                    onClick={() => setShowPassword((v) => !v)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>

                {form.password && (
                  <div className="cv-auth-strength-meter" title={`Strength: ${strength}/3`}>
                    <div className={`cv-auth-strength-seg ${strength >= 1 ? (strength === 1 ? "active-weak" : strength === 2 ? "active-medium" : "active-strong") : ""}`} />
                    <div className={`cv-auth-strength-seg ${strength >= 2 ? (strength === 2 ? "active-medium" : "active-strong") : ""}`} />
                    <div className={`cv-auth-strength-seg ${strength >= 3 ? "active-strong" : ""}`} />
                  </div>
                )}
              </div>

              <button
                type="submit"
                className="cv-auth-btn"
                disabled={loading}
              >
                {loading ? (
                  <>Creating Dossier...</>
                ) : (
                  <>
                    Create My Account <ArrowRight size={16} />
                  </>
                )}
              </button>
            </form>

            <p className="cv-auth-switch">
              Already have an account?
              <Link to="/login">Sign In</Link>
            </p>
          </div>

          <div className="cv-auth-trust-note">
            <ShieldCheck size={16} />
            <span>Encrypted credentials · Grounded without speculative hallucinations</span>
          </div>
        </div>
      </main>
    </div>
  );
}
