import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  Compass,
  MapPin,
  TrendingUp,
  Brain,
  Video,
  FileText,
  User,
  Palette,
  GitBranch,
  Zap,
  ArrowRight,
  X,
} from "lucide-react";
import { useTheme } from "../../context/ThemeContext";

export function CVCommandPalette({ isOpen, onClose }) {
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);
  const navigate = useNavigate();
  const { setTheme } = useTheme();

  const commands = [
    {
      id: "overview",
      title: "Career OS Overview",
      category: "Navigation",
      icon: Compass,
      shortcut: "G O",
      action: () => navigate("/dashboard"),
    },
    {
      id: "discover",
      title: "Career Navigator (Explore Directions)",
      category: "Navigation",
      icon: MapPin,
      shortcut: "G D",
      action: () => navigate("/career-discovery"),
    },
    {
      id: "skill-gap",
      title: "Skill Gap Matrix & Taxonomy",
      category: "AI Tools",
      icon: TrendingUp,
      shortcut: "G S",
      action: () => navigate("/skill-gap"),
    },
    {
      id: "roadmap",
      title: "Career Pathfinder Journey",
      category: "AI Tools",
      icon: Zap,
      shortcut: "G R",
      action: () => navigate("/career-roadmap"),
    },
    {
      id: "interview",
      title: "Interview with Dr. Cyra Vance (AI Room)",
      category: "Practice",
      icon: Video,
      shortcut: "G I",
      action: () => navigate("/ai/interview"),
    },
    {
      id: "intelligence",
      title: "Career Intelligence Report",
      category: "Analysis",
      icon: Brain,
      shortcut: "G C",
      action: () => navigate("/ai/intelligence"),
    },
    {
      id: "quiz",
      title: "Career Compass Quiz",
      category: "Assessment",
      icon: Compass,
      shortcut: "G Q",
      action: () => navigate("/career-quiz"),
    },
    {
      id: "profile",
      title: "Career Identity & Evidence",
      category: "Profile",
      icon: User,
      shortcut: "G P",
      action: () => navigate("/profile"),
    },
    {
      id: "resume",
      title: "Resume Signals & Upload",
      category: "Sources",
      icon: FileText,
      shortcut: "G U",
      action: () => navigate("/resume"),
    },
    {
      id: "theme-paper",
      title: "Switch Theme: Paper / Iris",
      category: "Appearance",
      icon: Palette,
      action: () => setTheme("paper-iris"),
    },
    {
      id: "theme-midnight",
      title: "Switch Theme: Midnight / Nebula",
      category: "Appearance",
      icon: Palette,
      action: () => setTheme("midnight-nebula"),
    },
    {
      id: "theme-clay",
      title: "Switch Theme: Clay / Sunrise",
      category: "Appearance",
      icon: Palette,
      action: () => setTheme("clay-sunrise"),
    },
    {
      id: "theme-moss",
      title: "Switch Theme: Moss / Graphite",
      category: "Appearance",
      icon: Palette,
      action: () => setTheme("moss-graphite"),
    },
    {
      id: "theme-ocean",
      title: "Switch Theme: Ocean / Mist",
      category: "Appearance",
      icon: Palette,
      action: () => setTheme("ocean-mist"),
    },
  ];

  const filtered = commands.filter((cmd) =>
    cmd.title.toLowerCase().includes(query.toLowerCase()) ||
    cmd.category.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  useEffect(() => {
    if (isOpen) {
      setQuery("");
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return;
      if (e.key === "Escape") {
        onClose();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % (filtered.length || 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filtered.length) % (filtered.length || 1));
      } else if (e.key === "Enter" && filtered[selectedIndex]) {
        e.preventDefault();
        filtered[selectedIndex].action();
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, filtered, selectedIndex, onClose]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: "var(--cv-z-command)",
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "center",
        paddingTop: "12vh",
      }}
    >
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: "rgba(0, 0, 0, 0.45)",
          backdropFilter: "blur(4px)",
          animation: "cv-fade-in var(--cv-dur-micro) var(--cv-ease-out)",
        }}
      />

      {/* Palette Modal */}
      <div
        className="cv-command-palette cv-animate-fade-scale"
        style={{
          position: "relative",
          width: "100%",
          maxWidth: "580px",
          backgroundColor: "var(--cv-surface)",
          borderRadius: "var(--cv-radius-lg)",
          border: "1px solid var(--cv-border)",
          boxShadow: "var(--cv-shadow-popover)",
          overflow: "hidden",
          zIndex: 1,
        }}
      >
        {/* Search Input */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            padding: "0.875rem 1rem",
            borderBottom: "1px solid var(--cv-border-subtle)",
            gap: "0.75rem",
          }}
        >
          <Search size={18} color="var(--cv-accent)" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Type a command or search actions..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{
              flex: 1,
              backgroundColor: "transparent",
              border: "none",
              outline: "none",
              fontSize: "0.9375rem",
              fontFamily: "var(--cv-font-sans)",
              color: "var(--cv-text)",
            }}
          />
          <kbd
            style={{
              padding: "0.15rem 0.4rem",
              fontSize: "0.6875rem",
              fontFamily: "var(--cv-font-mono)",
              backgroundColor: "var(--cv-surface-active)",
              borderRadius: "4px",
              border: "1px solid var(--cv-border)",
              color: "var(--cv-text-muted)",
            }}
          >
            ESC
          </kbd>
        </div>

        {/* Results List */}
        <div
          style={{
            maxHeight: "340px",
            overflowY: "auto",
            padding: "0.5rem",
          }}
        >
          {filtered.length === 0 ? (
            <div
              style={{
                padding: "2rem",
                textAlign: "center",
                color: "var(--cv-text-muted)",
                fontSize: "0.875rem",
              }}
            >
              No commands found for "{query}"
            </div>
          ) : (
            filtered.map((cmd, idx) => {
              const isSelected = idx === selectedIndex;
              const Icon = cmd.icon;
              return (
                <div
                  key={cmd.id}
                  onClick={() => {
                    cmd.action();
                    onClose();
                  }}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "0.625rem 0.875rem",
                    borderRadius: "var(--cv-radius-sm)",
                    backgroundColor: isSelected ? "var(--cv-surface-active)" : "transparent",
                    cursor: "pointer",
                    transition: "all var(--cv-dur-micro) var(--cv-ease-out)",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                    <div
                      style={{
                        width: "28px",
                        height: "28px",
                        borderRadius: "var(--cv-radius-sm)",
                        backgroundColor: isSelected ? "var(--cv-accent-soft)" : "var(--cv-bg-subtle)",
                        color: isSelected ? "var(--cv-accent)" : "var(--cv-text-muted)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <Icon size={14} />
                    </div>
                    <div>
                      <div
                        style={{
                          fontSize: "0.875rem",
                          fontWeight: isSelected ? "600" : "500",
                          color: "var(--cv-text)",
                        }}
                      >
                        {cmd.title}
                      </div>
                      <div
                        style={{
                          fontSize: "0.6875rem",
                          color: "var(--cv-text-muted)",
                        }}
                      >
                        {cmd.category}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    {cmd.shortcut && (
                      <span
                        style={{
                          fontFamily: "var(--cv-font-mono)",
                          fontSize: "0.6875rem",
                          color: "var(--cv-text-faint)",
                        }}
                      >
                        {cmd.shortcut}
                      </span>
                    )}
                    {isSelected && <ArrowRight size={14} color="var(--cv-accent)" />}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div
          style={{
            padding: "0.5rem 1rem",
            backgroundColor: "var(--cv-bg-subtle)",
            borderTop: "1px solid var(--cv-border-subtle)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            fontSize: "0.6875rem",
            color: "var(--cv-text-muted)",
          }}
        >
          <span>Use ↑ ↓ to navigate, Enter to select</span>
          <span style={{ fontFamily: "var(--cv-font-mono)" }}>CareerVerse Command OS</span>
        </div>
      </div>
    </div>
  );
}
