import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../services/authService";
import { getApiError } from "../services/api";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
    //role_id: 2,
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await registerUser(form);
      navigate("/login");
    } catch (err) {
      setError(getApiError(err, "Registration failed."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <p className="eyebrow">Create account</p>
          <h2>Join CareerVerse AI</h2>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <label>
            Full name
            <input
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="Jane Doe"
              required
            />
          </label>

          <label>
            Email
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="you@example.com"
              required
            />
          </label>

          <label>
            Phone
            <input
              name="phone"
              value={form.phone}
              onChange={handleChange}
              placeholder="(555) 123-4567"
            />
          </label>

          <label>
            Password
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="Create a strong password"
              required
            />
          </label>

          {error ? <div className="form-message error">{error}</div> : null}

          <button
            className="primary-button full-width"
            type="submit"
            disabled={loading}
          >
            {loading ? "Creating account..." : "Register"}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Login here</Link>
        </p>
      </div>
    </div>
  );
}
