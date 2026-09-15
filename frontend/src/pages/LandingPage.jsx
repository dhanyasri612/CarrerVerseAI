import { useState } from "react";
import { Link } from "react-router-dom";
import {
  landingHighlights,
  dashboardStats,
  recommendedRoles,
  skillSummary,
  roadmapSteps,
  activityFeed,
} from "../data/mockData";

export default function LandingPage() {
  const [menuOpen, setMenuOpen] = useState(false);

  const closeMenu = () => setMenuOpen(false);

  return (
    <div className="landing-page">
      <header className="landing-nav">
        <Link to="/" className="landing-brand" onClick={closeMenu}>
          <span className="brand-mark">CV</span>
          <span>
            <strong>CareerVerse AI</strong>
            <small>Career intelligence</small>
          </span>
        </Link>

        <button
          className="menu-toggle"
          type="button"
          aria-expanded={menuOpen}
          aria-controls="landing-navigation"
          onClick={() => setMenuOpen((current) => !current)}
        >
          <span />
          <span />
          <span />
          <span className="sr-only">Toggle navigation</span>
        </button>

        <nav
          id="landing-navigation"
          className={`landing-navigation ${menuOpen ? "open" : ""}`}
          aria-label="Landing page navigation"
        >
          <div className="landing-links">
            <a href="#top" onClick={closeMenu}>
              Home
            </a>
            <a href="#features" onClick={closeMenu}>
              Features
            </a>
            <a href="#about" onClick={closeMenu}>
              About
            </a>
          </div>
          <div className="landing-actions">
            <Link to="/login" className="landing-login" onClick={closeMenu}>
              Login
            </Link>
            <Link
              to="/register"
              className="primary-button landing-register"
              onClick={closeMenu}
            >
              Get Started
            </Link>
          </div>
        </nav>
      </header>

      <section className="hero-section" id="top">
        <div className="hero-copy">
          <p className="eyebrow">AI-Powered Career Intelligence Platform</p>
          <h1>Your AI-powered career intelligence platform</h1>
          <p className="hero-text">
            CareerVerse AI understands your resume, GitHub activity, skills, and
            career goals to deliver personalized guidance for your next move.
          </p>
          <div className="hero-actions">
            <Link to="/login" className="primary-button">
              Analyze My Career
            </Link>
            <a href="#features" className="ghost-button">
              Explore Features
            </a>
          </div>
          <div className="mini-stats">
            {dashboardStats.slice(0, 3).map((stat) => (
              <div key={stat.label} className="mini-stat-card">
                <span>{stat.label}</span>
                <strong>{stat.value}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="hero-panel">
          <div className="panel-card">
            <div className="panel-header">
              <span className="dot dot-purple" />
              <span className="dot dot-blue" />
              <span className="dot dot-teal" />
            </div>

            <div className="flow-diagram">
              <div>Resume</div>
              <div className="arrow">→</div>
              <div>AI Understanding</div>
              <div className="arrow">→</div>
              <div>Knowledge Graph</div>
              <div className="arrow">→</div>
              <div>Semantic Intelligence</div>
              <div className="arrow">→</div>
              <div>Multi-Agent AI</div>
              <div className="arrow">→</div>
              <div>Recommendations</div>
            </div>
          </div>
        </div>
      </section>

      <section className="content-section" id="about">
        <div className="section-header">
          <p className="eyebrow">Why CareerVerse AI</p>
          <h2>Career intelligence beyond resume parsing</h2>
        </div>

        <div className="grid-3">
          {landingHighlights.map((item) => (
            <div key={item.title} className="info-card">
              <h3>{item.title}</h3>
              <p>{item.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="content-section alt-bg" id="features">
        <div className="section-header">
          <p className="eyebrow">Data Sources</p>
          <h2>Connected signals that shape smarter decisions</h2>
        </div>

        <div className="data-source-grid">
          {["Resume", "GitHub", "LinkedIn", "LeetCode", "Certifications"].map(
            (source) => (
              <div key={source} className="source-pill">
                {source}
              </div>
            ),
          )}
        </div>
      </section>

      <section className="content-section">
        <div className="section-header">
          <p className="eyebrow">AI Intelligence</p>
          <h2>How the system works</h2>
        </div>

        <div className="stack-steps">
          {[
            "Resume Parsing + NLP + NER",
            "Skill Extraction",
            "Knowledge Graph",
            "RAG",
            "Multi-Agent AI",
            "Personalized Career Intelligence",
          ].map((step, index) => (
            <div key={step} className="stack-step">
              <span>{index + 1}</span>
              <strong>{step}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="content-section alt-bg">
        <div className="section-header">
          <p className="eyebrow">Core Features</p>
          <h2>Built for modern career growth</h2>
        </div>

        <div className="feature-layout">
          <div className="feature-card">
            <h3>Recommended roles</h3>
            <ul>
              {recommendedRoles.map((role) => (
                <li key={role}>{role}</li>
              ))}
            </ul>
          </div>

          <div className="feature-card">
            <h3>Skill overview</h3>
            {skillSummary.map((skill) => (
              <div key={skill.label} className="skill-row">
                <div className="skill-label-row">
                  <span>{skill.label}</span>
                  <span>{skill.level}%</span>
                </div>
                <div className="progress-track">
                  <span style={{ width: `${skill.level}%` }} />
                </div>
              </div>
            ))}
          </div>

          <div className="feature-card">
            <h3>Roadmap preview</h3>
            <ul className="timeline-list">
              {roadmapSteps.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="content-section">
        <div className="section-header">
          <p className="eyebrow">Recent Activity</p>
          <h2>What the platform tracks</h2>
        </div>

        <div className="activity-box">
          {activityFeed.map((item) => (
            <div key={item} className="activity-item">
              {item}
            </div>
          ))}
        </div>
      </section>

      <footer className="landing-footer">
        <div>
          <strong>CareerVerse AI</strong>
          <p>Personalized career intelligence for ambitious professionals.</p>
        </div>
      </footer>
    </div>
  );
}
