import React, { useState, useEffect, useRef } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import {
  Orbit, Search, Settings2, ChevronDown, X, ArrowRight,
  BookOpen, Compass, Zap, Video, Menu,
  LogOut, User, Check, Activity,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

/* ─── CHAPTER MAP ─────────────────────────────────────────────────────────── */
const CHAPTERS = [
  { key: "story",        number: "01", label: "Your Story",       to: "/profile",           title: "A career is more than a list of titles." },
  { key: "options",      number: "02", label: "Your Options",     to: "/career-discovery",  title: "Where could your current profile take you?" },
  { key: "gaps",         number: "03", label: "Your Gaps",        to: "/skill-gap",         title: "A useful gap is a distance with context." },
  { key: "journey",      number: "04", label: "Your Journey",     to: "/career-roadmap",    title: "Turn skills and priority gaps into a path." },
  { key: "alex",         number: "05", label: "Cyra Vance",      to: "/ai/interview",      title: "Practice should meet you where you are." },
  { key: "mirror",       number: "06", label: "Career Mirror",    to: "/ai/intelligence",   title: "Here is what your career signals say." },
];

const EXTRAS = [
  { key: "quiz",   number: "↗", label: "Career Compass",   to: "/career-quiz", title: "Reflective career assessment" },
  { key: "resume", number: "↗", label: "Resume & Sources", to: "/resume",      title: "Resume, GitHub, coding profiles" },
];

const ALL_CHAPTERS = [...CHAPTERS, ...EXTRAS];

const THEME_OPTIONS = [
  { id: "paper",     name: "Paper / Ink",       desc: "Editorial, tactile, measured" },
  { id: "black",     name: "Black / Cobalt",     desc: "Independent, hard-edged" },
  { id: "clay",      name: "Clay / Poster",      desc: "Warm, expressive, graphic" },
  { id: "botanical", name: "Botanical / Moss",   desc: "Organic, grounded, quiet" },
  { id: "mono",      name: "Mono / Graphite",    desc: "Technical, precise, spare" },
  { id: "cinema",    name: "Cinema / Night",     desc: "Atmospheric, reflective" },
];

/* ─── LAYOUT SHELL ────────────────────────────────────────────────────────── */
export default function Layout() {
  const { user, logout }       = useAuth();
  const { theme, setTheme }    = useTheme();
  const navigate               = useNavigate();
  const location               = useLocation();
  const [showIndex,    setShowIndex]    = useState(false);
  const [showThemes,   setShowThemes]   = useState(false);
  const [showCommand,  setShowCommand]  = useState(false);
  const [showMore,     setShowMore]     = useState(false);
  const [search,       setSearch]       = useState("");
  const commandInputRef = useRef(null);

  /* ⌘K handler */
  useEffect(() => {
    const handleKeys = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setShowCommand((v) => !v);
      }
      if (e.key === "Escape") {
        setShowCommand(false);
        setShowThemes(false);
        setShowIndex(false);
        setShowMore(false);
      }
    };
    window.addEventListener("keydown", handleKeys);
    return () => window.removeEventListener("keydown", handleKeys);
  }, []);

  /* focus command input when opened */
  useEffect(() => {
    if (showCommand) {
      setSearch("");
      setTimeout(() => commandInputRef.current?.focus(), 20);
    }
  }, [showCommand]);

  const currentChapter = ALL_CHAPTERS.find(
    (c) => location.pathname === c.to || (c.to !== "/dashboard" && location.pathname.startsWith(c.to))
  );

  const filteredChapters = ALL_CHAPTERS.filter((c) => {
    const q = search.trim().toLowerCase();
    return !q || `${c.label} ${c.to} ${c.number}`.toLowerCase().includes(q);
  });

  const handleLogout = () => { logout(); navigate("/login"); };

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">Skip to content</a>

      {/* ═══════════════════════════════════════════════════════════════════
          TOPBAR — Editorial Masthead
          ═══════════════════════════════════════════════════════════════════ */}
      <header className="cv-topbar">
        {/* Brand */}
        <div className="cv-brand" onClick={() => navigate("/dashboard")} role="link" tabIndex={0}>
          <span className="cv-brand-mark"><Orbit size={13} /></span>
          <span>CareerVerse</span>
        </div>

        <span className="cv-masthead-meta">A personal career operating system</span>

        {/* Chapter Index Trigger */}
        <button
          className="cv-chapter-trigger"
          onClick={() => setShowIndex((v) => !v)}
          aria-expanded={showIndex}
          aria-label="Open chapter index"
        >
          {currentChapter
            ? <><span>{currentChapter.number}</span><span style={{ color: "var(--cv-muted)" }}>/ 06</span></>
            : <><span>Read the story</span><ChevronDown size={12} /></>
          }
        </button>

        {/* Right actions */}
        <div className="cv-topbar-actions">
          <button
            className="cv-command-trigger"
            onClick={() => setShowCommand(true)}
            aria-label="Search and quick commands"
          >
            <Search size={14} />
            <span>Find a chapter</span>
            <kbd>⌘ K</kbd>
          </button>

          {/* Theme Studio */}
          <button
            className="cv-top-icon"
            aria-label="Open Theme Studio"
            onClick={() => setShowThemes((v) => !v)}
          >
            <Settings2 size={14} />
          </button>

          {/* User avatar */}
          <button
            className="cv-top-icon"
            style={{ width: "auto", padding: "0 8px", gap: "6px", display: "flex", alignItems: "center" }}
            onClick={() => navigate("/profile")}
            aria-label="Open profile"
          >
            <div style={{
              width: 22, height: 22, borderRadius: "50%",
              background: "var(--cv-accent)", color: "var(--cv-paper)",
              fontSize: "0.6rem", fontWeight: 700,
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              {(user?.name || user?.email || "C").charAt(0).toUpperCase()}
            </div>
            <span style={{ fontSize: "var(--cv-text-body-sm)", fontWeight: 600, color: "var(--cv-text)" }}>
              {user?.name?.split(" ")[0] || "Profile"}
            </span>
          </button>

          {/* Sign out */}
          <button className="cv-top-icon" onClick={handleLogout} aria-label="Sign out">
            <LogOut size={14} />
          </button>
        </div>
      </header>

      {/* ═══════════════════════════════════════════════════════════════════
          MAIN CONTENT
          ═══════════════════════════════════════════════════════════════════ */}
      <main className="cv-main-content cv-page-enter" key={location.pathname} id="main-content">
        <div className="cv-chapter-page">
          <Outlet />
        </div>
      </main>

      {/* ═══════════════════════════════════════════════════════════════════
          MOBILE BOTTOM NAV
          ═══════════════════════════════════════════════════════════════════ */}
      <nav className="cv-mobile-nav" aria-label="Quick navigation">
        <NavLink to="/profile"          className={({ isActive }) => isActive ? "active" : ""}><BookOpen size={17} />Story</NavLink>
        <NavLink to="/career-discovery" className={({ isActive }) => isActive ? "active" : ""}><Compass size={17} />Options</NavLink>
        <NavLink to="/career-roadmap"   className={({ isActive }) => isActive ? "active" : ""}><Zap size={17} />Journey</NavLink>
        <NavLink to="/ai/interview"     className={({ isActive }) => isActive ? "active" : ""}><Video size={17} />Interview</NavLink>
        <button onClick={() => setShowMore((v) => !v)} aria-expanded={showMore}><Menu size={17} />More</button>
      </nav>

      {showMore && (
        <div className="cv-mobile-more-menu" role="dialog" aria-label="More chapters">
          {CHAPTERS.slice(4).concat(EXTRAS).map((c) => (
            <NavLink key={c.key} to={c.to} onClick={() => setShowMore(false)}>
              {c.number}&nbsp;&nbsp;{c.label}
            </NavLink>
          ))}
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════════
          CHAPTER INDEX POPOVER
          ═══════════════════════════════════════════════════════════════════ */}
      {showIndex && (
        <section className="cv-chapter-popover" role="dialog" aria-label="Chapter index">
          <div className="cv-popover-head">
            <div>
              <h2>Read the chapters</h2>
              <p>Move through your career story, one question at a time.</p>
            </div>
            <button className="cv-icon-button" onClick={() => setShowIndex(false)} aria-label="Close chapter index">
              <X size={14} />
            </button>
          </div>
          <div className="cv-chapter-index-list">
            {CHAPTERS.map((c) => (
              <NavLink
                key={c.key} to={c.to}
                className="cv-chapter-index-row"
                onClick={() => setShowIndex(false)}
              >
                <span className="row-number">{c.number}</span>
                <span className="row-label">{c.label}</span>
                <ArrowRight size={13} />
              </NavLink>
            ))}
            {EXTRAS.map((c) => (
              <NavLink
                key={c.key} to={c.to}
                className="cv-chapter-index-row"
                onClick={() => setShowIndex(false)}
              >
                <span className="row-number">{c.number}</span>
                <span className="row-label">{c.label}</span>
                <ArrowRight size={13} />
              </NavLink>
            ))}
          </div>
        </section>
      )}

      {/* ═══════════════════════════════════════════════════════════════════
          THEME STUDIO POPOVER
          ═══════════════════════════════════════════════════════════════════ */}
      {showThemes && (
        <section className="cv-theme-popover" role="dialog" aria-label="Theme Studio">
          <div className="cv-popover-head">
            <div>
              <h2>Theme Studio</h2>
              <p>Six visual readings. One CareerVerse type identity.</p>
            </div>
            <button className="cv-icon-button" onClick={() => setShowThemes(false)} aria-label="Close Theme Studio">
              <X size={14} />
            </button>
          </div>
          <div className="cv-theme-grid">
            {THEME_OPTIONS.map((opt) => (
              <button
                key={opt.id}
                className={`cv-theme-option${theme === opt.id || theme?.startsWith(opt.id) ? " selected" : ""}`}
                data-t={opt.id}
                onClick={() => { setTheme(opt.id); }}
                aria-pressed={theme === opt.id || theme?.startsWith(opt.id)}
              >
                <span className="cv-theme-preview">
                  <strong>{opt.name.split(" / ")[0]}</strong>
                </span>
                <span className="cv-theme-name">
                  <span>{opt.name}</span>
                  {(theme === opt.id || theme?.startsWith(opt.id)) && <Check size={12} aria-label="Selected" />}
                </span>
                <span className="cv-sr-only">{opt.desc}</span>
              </button>
            ))}
          </div>
        </section>
      )}

      {/* ═══════════════════════════════════════════════════════════════════
          COMMAND PALETTE
          ═══════════════════════════════════════════════════════════════════ */}
      {showCommand && (
        <div
          className="cv-modal-backdrop"
          onMouseDown={(e) => { if (e.target === e.currentTarget) setShowCommand(false); }}
        >
          <section className="cv-command-modal" role="dialog" aria-modal="true" aria-label="CareerVerse command search">
            <div className="cv-command-search">
              <Search size={16} />
              <input
                ref={commandInputRef}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Find a chapter or destination"
                aria-label="Search chapters"
              />
              <kbd>ESC</kbd>
            </div>
            <div className="cv-command-items">
              <div className="cv-command-label">Go to</div>
              {filteredChapters.length
                ? filteredChapters.map((c) => (
                    <NavLink
                      key={c.key} to={c.to}
                      className="cv-command-item"
                      onClick={() => setShowCommand(false)}
                    >
                      <span>{c.number}&nbsp;&nbsp;{c.label}</span>
                      <ArrowRight size={13} />
                    </NavLink>
                  ))
                : <p className="cv-command-label">No chapter matches that phrase.</p>
              }
              <div className="cv-command-label">Appearance</div>
              <button
                className="cv-command-item"
                onClick={() => { setShowCommand(false); setShowThemes(true); }}
              >
                <span>Open Theme Studio</span>
                <Settings2 size={13} />
              </button>
            </div>
          </section>
        </div>
      )}

      <span className="cv-sr-only" aria-live="polite">
        {currentChapter?.label ?? "Opening"} page
      </span>
    </div>
  );
}
