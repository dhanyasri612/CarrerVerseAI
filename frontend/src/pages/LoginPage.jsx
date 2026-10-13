import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import {
  Orbit, Mail, Lock, Eye, EyeOff,
  ArrowRight, ShieldCheck, Sparkles, AlertCircle, CheckCircle2
} from "lucide-react";
import { loginUser } from "../services/authService";
import { useAuth } from "../context/AuthContext";
import { getApiError } from "../services/api";
import { useTheme } from "../context/ThemeContext";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const { theme, setTheme } = useTheme?.() || { theme: "paper", setTheme: () => {} };

  const [form, setForm] = useState({
    email: location.state?.registeredEmail || "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    if (!form.email.trim()) {
      setError("Please provide your email address.");
      return;
    }
    if (!form.password) {
      setError("Please enter your password.");
      return;
    }

    setLoading(true);

    try {
      const response = await loginUser(form);
      login(response, { email: form.email });
      navigate("/dashboard");
    } catch (err) {
      setError(getApiError(err, "Authentication failed. Please verify your email and password."));
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
            <Sparkles size={14} /> Chapter 00 · Candidate Access
          </div>
          <h1 className="cv-auth-headline">
            Return to your <span className="serif">verified strategy.</span>
          </h1>

          <div className="cv-auth-feature-list">
            <div className="cv-auth-feature-item">
              <span className="cv-auth-feature-num">01</span>
              <div className="cv-auth-feature-text">
                <h4>Continuous Trajectory Mapping</h4>
                <p>Pick up right where your skills, gap analyses, and roadmaps left off.</p>
              </div>
            </div>

            <div className="cv-auth-feature-item">
              <span className="cv-auth-feature-num">02</span>
              <div className="cv-auth-feature-text">
                <h4>Multi-Agent Career Mirror</h4>
                <p>Access your synthesized intelligence dossier with live recommendations.</p>
              </div>
            </div>

            <div className="cv-auth-feature-item">
              <span className="cv-auth-feature-num">03</span>
              <div className="cv-auth-feature-text">
                <h4>Interview Simulation Analytics</h4>
                <p>Track your score progression and feedback over multiple practice rounds.</p>
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
              <span className="cv-auth-card-kicker">01 / Sign In</span>
              <h2 className="cv-auth-card-title">Welcome back.</h2>
              <p className="cv-auth-card-subtitle">
                Enter your credentials to access your CareerVerse intelligence dossier.
              </p>
            </div>

            {location.state?.registeredEmail && !error && (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  padding: "10px 14px",
                  marginBottom: "18px",
                  borderRadius: "4px",
                  background: "color-mix(in srgb, var(--cv-success) 12%, var(--cv-paper))",
                  border: "1px solid color-mix(in srgb, var(--cv-success) 35%, transparent)",
                  color: "var(--cv-success)",
                  fontSize: "0.82rem",
                }}
              >
                <CheckCircle2 size={16} />
                <span>Account created successfully! Please sign in.</span>
              </div>
            )}

            {error && (
              <div className="cv-auth-error-banner" role="alert" style={{ marginBottom: "18px" }}>
                <AlertCircle size={18} style={{ flexShrink: 0, marginTop: "2px" }} />
                <div>{error}</div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="cv-auth-form">
              <div className="cv-auth-field">
                <label className="cv-auth-label" htmlFor="login-email">
                  Email Address
                </label>
                <div className="cv-auth-input-wrap">
                  <span className="cv-auth-input-icon">
                    <Mail size={16} />
                  </span>
                  <input
                    id="login-email"
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
                <label className="cv-auth-label" htmlFor="login-password">
                  Password
                </label>
                <div className="cv-auth-input-wrap">
                  <span className="cv-auth-input-icon">
                    <Lock size={16} />
                  </span>
                  <input
                    id="login-password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    className="cv-auth-input"
                    style={{ paddingLeft: "44px", paddingRight: "42px" }}
                    value={form.password}
                    onChange={handleChange}
                    placeholder="••••••••"
                    autoComplete="current-password"
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
              </div>

              <button
                type="submit"
                className="cv-auth-btn"
                disabled={loading}
              >
                {loading ? (
                  <>Signing In...</>
                ) : (
                  <>
                    Sign In <ArrowRight size={16} />
                  </>
                )}
              </button>
            </form>

            <p className="cv-auth-switch">
              Don’t have an account yet?
              <Link to="/register">Create one</Link>
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
