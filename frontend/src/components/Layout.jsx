import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const navItems = [
  { label: "Dashboard", to: "/dashboard" },
  { label: "Resume", to: "/resume" },
  { label: "Skill Gap", to: "/skill-gap" },
  { label: "Recommendations", to: "/recommendations" },
  { label: "Roadmap", to: "/career-roadmap" },
  { label: "GitHub", to: "/github" },
  { label: "Resume Analysis", to: "/resume-analysis" },
  { label: "Resume Improvement", to: "/resume-improvement" },
  { label: "Profile", to: "/profile" },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">CV</div>
          <div>
            <div className="brand-name">CareerVerse AI</div>
            <div className="brand-subtitle">Career Intelligence</div>
          </div>
        </div>

        <nav className="sidebar-nav" aria-label="Main navigation">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">AI-powered career intelligence</p>
            <h1>CareerVerse AI</h1>
          </div>

          <div className="topbar-actions">
            <button
              className="ghost-button"
              type="button"
              onClick={() => navigate("/profile")}
            >
              View profile
            </button>
            <span className="user-chip">
              {user?.name || user?.email || "Your account"}
            </span>
            <button
              className="primary-button"
              type="button"
              onClick={() => {
                logout();
                navigate("/login");
              }}
            >
              Logout
            </button>
          </div>
        </header>

        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
