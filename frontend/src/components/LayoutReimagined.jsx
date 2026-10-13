/**
 * CareerVerse — Reimagined Layout Shell
 * Ported from CareerVerse-Reimagined editorial aesthetic.
 *
 * - No sidebar. Compact sticky topbar.
 * - Chapter index popover (numbered, 01–08)
 * - Theme Studio (6 themes via data-theme on <html>)
 * - Profile & Settings Popover with User Initial Avatar Logo
 * - ⌘K command palette
 * - Mobile bottom nav
 */

import { useEffect, useMemo, useRef, useState } from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import {
  ArrowRight,
  BookOpen,
  Compass,
  Layers3,
  Menu,
  Orbit,
  Search,
  Settings2,
  X,
  Check,
  User,
  LogOut,
  FileText,
  Brain,
  ShieldCheck,
  ChevronRight,
  ExternalLink,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

/* ── Chapters (numbered exactly like the reimagined design) ──────────────── */
export const CHAPTERS = [
  { number: "01", label: "Your Story",      href: "/profile",          key: "story"    },
  { number: "02", label: "Your Work",       href: "/resume",           key: "work"     },
  { number: "03", label: "Your Options",    href: "/career-discovery", key: "options"  },
  { number: "04", label: "Your Gaps",       href: "/skill-gap",        key: "gaps"     },
  { number: "05", label: "Your Journey",    href: "/career-roadmap",   key: "journey"  },
  { number: "06", label: "Interview Room",  href: "/ai/interview",     key: "interview" },
  { number: "07", label: "AI Teaching Room",href: "/ai/teaching",      key: "teaching"  },
  { number: "08", label: "Career Mirror",   href: "/ai/intelligence",  key: "mirror"   },
];

const EXTRAS = [
  { number: "⚡", label: "DSA Practice",     href: "/dsa-practice", key: "dsa" },
  { number: "↗", label: "Dashboard",        href: "/dashboard",    key: "home"   },
  { number: "↗", label: "Career Navigator", href: "/career-discovery", key: "nav" },
  { number: "↗", label: "Career Compass",   href: "/career-quiz", key: "compass" },
];

/* ── Theme registry (matches reimagined exactly) ─────────────────────────── */
const THEMES = [
  { id: "paper",    name: "Paper / Ink",       desc: "Editorial, tactile, measured"  },
  { id: "black",    name: "Black / Cobalt",    desc: "Independent, hard-edged"       },
  { id: "clay",     name: "Clay / Poster",     desc: "Warm, expressive, graphic"     },
  { id: "botanical",name: "Botanical / Moss",  desc: "Organic, grounded, quiet"      },
  { id: "mono",     name: "Mono / Graphite",   desc: "Technical, precise, spare"     },
  { id: "cinema",   name: "Cinema / Night",    desc: "Atmospheric, reflective"       },
];

const THEME_KEY = "careerverse-theme-v3";

function useTheme() {
  const [theme, setThemeState] = useState(() => {
    try {
      const stored = localStorage.getItem(THEME_KEY);
      return stored || "paper";
    } catch {
      return "paper";
    }
  });

  const setTheme = (next) => {
    setThemeState(next);
    try {
      localStorage.setItem(THEME_KEY, next);
      document.documentElement.setAttribute("data-theme", next);
    } catch {}
  };

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  return { theme, setTheme };
}

/* ── Main Layout ─────────────────────────────────────────────────────────── */
export default function LayoutReimagined() {
  const { theme, setTheme } = useTheme();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [showIndex,   setShowIndex]   = useState(false);
  const [showThemes,  setShowThemes]  = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [showCmd,     setShowCmd]     = useState(false);
  const [showMore,    setShowMore]    = useState(false);
  const [search, setSearch] = useState("");
  const cmdInput = useRef(null);

  const userDisplayName = user?.name || user?.email?.split("@")[0] || "User";
  const userInitial = (user?.name || user?.email || "U").trim().charAt(0).toUpperCase();

  // Global ⌘K listener
  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setShowCmd((v) => !v);
      }
      if (e.key === "Escape") {
        setShowCmd(false);
        setShowThemes(false);
        setShowIndex(false);
        setShowProfile(false);
        setShowMore(false);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  // Focus command input when opened
  useEffect(() => {
    if (showCmd) {
      setSearch("");
      setTimeout(() => cmdInput.current?.focus(), 20);
    }
  }, [showCmd]);

  // Close popovers on route change
  useEffect(() => {
    setShowIndex(false);
    setShowThemes(false);
    setShowProfile(false);
    setShowCmd(false);
    setShowMore(false);
  }, [location.pathname]);

  const allChapters = [...CHAPTERS, ...EXTRAS];
  const filteredChapters = useMemo(() => {
    const q = search.trim().toLowerCase();
    return !q ? allChapters : allChapters.filter((c) =>
      `${c.label} ${c.href} ${c.number}`.toLowerCase().includes(q)
    );
  }, [search]);

  const currentChapter = allChapters.find((c) => c.href === location.pathname);
  const chapterLabel = currentChapter
    ? `${currentChapter.number} / ${currentChapter.label}`
    : "Navigate";

  return (
    <div className="cv2-app-shell">
      <a className="skip-link" href="#cv2-main">Skip to content</a>

      {/* ── Top bar ─────────────────────────────────────────────────────── */}
      <header className="cv2-topbar">
        {/* Brand */}
        <Link to="/dashboard" className="cv2-brand">
          <span className="cv2-brand-mark" aria-hidden="true">
            <Orbit size={13} />
          </span>
          <span>CareerVerse</span>
        </Link>

        <span className="cv2-masthead-meta">A personal career operating system</span>

        {/* Chapter trigger */}
        <button
          className="cv2-chapter-trigger"
          type="button"
          onClick={() => {
            setShowIndex((v) => !v);
            setShowThemes(false);
            setShowProfile(false);
          }}
          aria-expanded={showIndex}
          aria-label="Open chapter index"
        >
          <span>{chapterLabel}</span>
        </button>

        {/* Right actions */}
        <div className="cv2-topbar-actions">
          {/* Command search */}
          <button
            className="cv2-command-trigger"
            type="button"
            onClick={() => {
              setShowCmd(true);
              setShowThemes(false);
              setShowProfile(false);
            }}
            aria-label="Search CareerVerse (⌘K)"
          >
            <Search size={15} />
            <span>Find a chapter</span>
            <kbd>⌘ K</kbd>
          </button>

          {/* Theme studio */}
          <button
            className="cv2-top-icon"
            type="button"
            aria-label="Open Theme Studio"
            onClick={() => {
              setShowThemes((v) => !v);
              setShowIndex(false);
              setShowProfile(false);
            }}
          >
            <Settings2 size={15} />
          </button>

          {/* User Initial Avatar Button */}
          <button
            className="cv2-user-avatar-btn"
            type="button"
            aria-label={`Profile & Settings: ${userDisplayName}`}
            title={`${userDisplayName} — Profile & Settings`}
            onClick={() => {
              setShowProfile((v) => !v);
              setShowThemes(false);
              setShowIndex(false);
            }}
          >
            <span className="cv2-avatar-initial">{userInitial}</span>
          </button>
        </div>
      </header>

      {/* ── Page content ────────────────────────────────────────────────── */}
      <main
        className="cv2-main cv2-page-enter"
        id="cv2-main"
        key={location.pathname}
      >
        <Outlet />
      </main>

      {/* ── Mobile bottom nav ────────────────────────────────────────────── */}
      <nav className="cv2-mobile-nav" aria-label="Quick navigation">
        <NavLink to="/profile"          className={({ isActive }) => isActive ? "active" : ""}><BookOpen size={17} />Story</NavLink>
        <NavLink to="/resume"           className={({ isActive }) => isActive ? "active" : ""}><Layers3 size={17} />Work</NavLink>
        <NavLink to="/career-discovery" className={({ isActive }) => isActive ? "active" : ""}><Compass size={17} />Options</NavLink>
        <button type="button" onClick={() => setShowMore((v) => !v)} aria-expanded={showMore}>
          <Menu size={17} />More
        </button>
      </nav>

      {showMore && (
        <div className="cv2-mobile-more" role="dialog" aria-label="More chapters">
          {CHAPTERS.slice(3).concat(EXTRAS).map((c) => (
            <Link key={c.key} to={c.href}>
              {c.number}&nbsp;&nbsp;{c.label}
            </Link>
          ))}
          <button type="button" style={{ color: "var(--cv-danger)", marginTop: "8px" }} onClick={() => { logout(); navigate("/login"); }}>
            Sign out
          </button>
        </div>
      )}

      {/* ── Profile & Settings popover ───────────────────────────────────── */}
      {showProfile && (
        <section className="cv2-profile-popover" role="dialog" aria-label="Profile & Account Settings">
          {/* User Info Header */}
          <div className="cv2-profile-user-card">
            <div className="cv2-profile-avatar-lg">
              {userInitial}
            </div>
            <div className="cv2-profile-details">
              <div className="cv2-profile-name">{user?.name || userDisplayName}</div>
              <div className="cv2-profile-email">{user?.email || "candidate@careerverse.ai"}</div>
              <div className="cv2-profile-badge">
                <ShieldCheck size={12} /> Verified Dossier
              </div>
            </div>
            <button
              className="cv2-icon-btn"
              type="button"
              onClick={() => setShowProfile(false)}
              aria-label="Close Profile Settings"
            >
              <X size={15} />
            </button>
          </div>

          {/* Quick Profile Navigation */}
          <div className="cv2-profile-menu-group">
            <div className="cv2-profile-menu-label">Career Dossier & Evidence</div>
            <Link
              to="/profile"
              className="cv2-profile-menu-item"
              onClick={() => setShowProfile(false)}
            >
              <div className="cv2-profile-menu-left">
                <User size={15} color="var(--cv-accent)" />
                <span>Chapter 01 · Your Story & Profile</span>
              </div>
              <ChevronRight size={14} color="var(--cv-muted)" />
            </Link>

            <Link
              to="/resume"
              className="cv2-profile-menu-item"
              onClick={() => setShowProfile(false)}
            >
              <div className="cv2-profile-menu-left">
                <FileText size={15} color="var(--cv-accent)" />
                <span>Chapter 02 · Resume & Sources</span>
              </div>
              <ChevronRight size={14} color="var(--cv-muted)" />
            </Link>

            <Link
              to="/ai/intelligence"
              className="cv2-profile-menu-item"
              onClick={() => setShowProfile(false)}
            >
              <div className="cv2-profile-menu-left">
                <Brain size={15} color="var(--cv-accent)" />
                <span>Chapter 08 · Career Mirror Intelligence</span>
              </div>
              <ChevronRight size={14} color="var(--cv-muted)" />
            </Link>
          </div>

          {/* Appearance Quick Switcher */}
          <div className="cv2-profile-menu-group">
            <div className="cv2-profile-menu-label">Active Theme Palette</div>
            <div className="cv2-profile-theme-strip">
              <span style={{ color: "var(--cv-muted)", fontWeight: 500 }}>
                {THEMES.find((t) => t.id === theme)?.name || "Paper / Ink"}
              </span>
              <div style={{ display: "flex", gap: "6px" }}>
                {THEMES.map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => setTheme(t.id)}
                    title={t.name}
                    style={{
                      width: "18px",
                      height: "18px",
                      borderRadius: "50%",
                      border: theme === t.id ? "2px solid var(--cv-accent)" : "1px solid var(--cv-rule)",
                      background:
                        t.id === "paper" ? "#f1eee4" :
                        t.id === "black" ? "#11141c" :
                        t.id === "clay" ? "#eee3d5" :
                        t.id === "botanical" ? "#e9ebdf" :
                        t.id === "mono" ? "#e9e9e3" : "#1c1b18",
                      cursor: "pointer",
                      padding: 0,
                      boxShadow: theme === t.id ? "0 0 0 2px var(--cv-paper)" : "none",
                    }}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Sign Out Action */}
          <button
            type="button"
            className="cv2-profile-signout"
            onClick={() => {
              logout();
              navigate("/login");
            }}
          >
            <LogOut size={14} /> Sign Out of CareerVerse
          </button>
        </section>
      )}

      {/* ── Chapter index popover ────────────────────────────────────────── */}
      {showIndex && (
        <section className="cv2-popover" role="dialog" aria-label="Chapter index">
          <div className="cv2-popover-head">
            <div>
              <h2>Read the chapters</h2>
              <p>Move through your career story, one chapter at a time.</p>
            </div>
            <button className="cv2-icon-btn" type="button" onClick={() => setShowIndex(false)} aria-label="Close chapter index">
              <X size={15} />
            </button>
          </div>
          <div className="cv2-chapter-index-list">
            {CHAPTERS.map((c) => (
              <Link
                key={c.key}
                to={c.href}
                className="cv2-chapter-row"
                onClick={() => setShowIndex(false)}
              >
                <span className="cv2-row-number">{c.number}</span>
                <span className="cv2-row-label">{c.label}</span>
                <ArrowRight size={14} />
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* ── Theme Studio popover ─────────────────────────────────────────── */}
      {showThemes && (
        <section className="cv2-popover" role="dialog" aria-label="Theme Studio">
          <div className="cv2-popover-head">
            <div>
              <h2>Theme Studio</h2>
              <p>Six visual readings of one CareerVerse identity.</p>
            </div>
            <button className="cv2-icon-btn" type="button" onClick={() => setShowThemes(false)} aria-label="Close Theme Studio">
              <X size={15} />
            </button>
          </div>
          <div className="cv2-theme-grid">
            {THEMES.map((t) => (
              <button
                key={t.id}
                type="button"
                className={`cv2-theme-option ${theme === t.id ? "selected" : ""}`}
                data-preview={t.id}
                onClick={() => setTheme(t.id)}
                aria-pressed={theme === t.id}
              >
                <span className="cv2-theme-preview">
                  <strong>{t.name.split(" / ")[0]}</strong>
                </span>
                <span className="cv2-theme-name">
                  <span>{t.name}</span>
                  {theme === t.id && <Check size={13} aria-label="Selected" />}
                </span>
                <span className="sr-only">{t.desc}</span>
              </button>
            ))}
          </div>
        </section>
      )}

      {/* ── Command palette ──────────────────────────────────────────────── */}
      {showCmd && (
        <div
          className="cv2-modal-backdrop"
          onMouseDown={(e) => { if (e.target === e.currentTarget) setShowCmd(false); }}
          role="presentation"
        >
          <section className="cv2-command-modal" role="dialog" aria-modal="true" aria-label="CareerVerse chapter search">
            <div className="cv2-command-search">
              <Search size={17} />
              <input
                ref={cmdInput}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Find a chapter or destination"
                aria-label="Search chapters"
              />
              <kbd>ESC</kbd>
            </div>
            <div className="cv2-command-items">
              <p className="cv2-command-label">Go to</p>
              {filteredChapters.length ? (
                filteredChapters.map((c) => (
                  <Link
                    key={c.key}
                    to={c.href}
                    className="cv2-command-item"
                    onClick={() => setShowCmd(false)}
                  >
                    <span>{c.number}&nbsp;&nbsp;{c.label}</span>
                    <ArrowRight size={14} />
                  </Link>
                ))
              ) : (
                <p className="cv2-command-label">No chapter matches that phrase.</p>
              )}
              <p className="cv2-command-label" style={{ marginTop: "8px" }}>Appearance</p>
              <button
                className="cv2-command-item"
                type="button"
                onClick={() => { setShowCmd(false); setShowThemes(true); }}
              >
                <span>Open Theme Studio</span>
                <Settings2 size={14} />
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
