import React, { useState, useRef, useEffect } from "react";
import { Palette, Check, Sun, Moon, Sparkles, Sliders, Droplets } from "lucide-react";
import { useTheme } from "../context/ThemeContext";

const THEME_ICONS = {
  editorial: Sun,
  midnight: Moon,
  lavender: Sparkles,
  graphite: Sliders,
  ocean: Droplets,
};

export default function ThemeSelector({ compact = false }) {
  const { theme, setTheme, themes } = useTheme();
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);

  const currentTheme = themes.find((t) => t.id === theme) || themes[0];
  const CurrentIcon = THEME_ICONS[theme] || Palette;

  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    }
    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [open]);

  return (
    <div className="theme-selector-wrap" ref={dropdownRef} style={{ position: "relative" }}>
      <button
        type="button"
        className={`ghost-button theme-toggle-btn ${compact ? "compact" : ""}`}
        onClick={() => setOpen((prev) => !prev)}
        aria-label={`Appearance theme: ${currentTheme.name}. Click to change.`}
        aria-expanded={open}
        aria-haspopup="listbox"
        title={`Theme: ${currentTheme.name}`}
      >
        <CurrentIcon size={15} aria-hidden="true" />
        {!compact && <span>{currentTheme.name}</span>}
      </button>

      {open && (
        <div
          className="theme-dropdown-menu panel-card"
          role="listbox"
          aria-label="Select appearance theme"
          style={{
            position: "absolute",
            right: 0,
            top: "calc(100% + 6px)",
            minWidth: 220,
            padding: "0.5rem",
            zIndex: 1000,
            boxShadow: "var(--shadow-lg)",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border)",
            background: "var(--surface)",
          }}
        >
          <div
            style={{
              padding: "0.35rem 0.5rem 0.5rem",
              fontSize: "0.75rem",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              color: "var(--text-muted)",
              borderBottom: "1px solid var(--border-subtle)",
              marginBottom: "0.35rem",
            }}
          >
            Appearance Theme
          </div>
          {themes.map((t) => {
            const isSelected = t.id === theme;
            const Icon = THEME_ICONS[t.id] || Palette;
            return (
              <button
                key={t.id}
                type="button"
                role="option"
                aria-selected={isSelected}
                onClick={() => {
                  setTheme(t.id);
                  setOpen(false);
                }}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  width: "100%",
                  padding: "0.5rem 0.6rem",
                  fontSize: "0.85rem",
                  borderRadius: "var(--radius-sm)",
                  border: "none",
                  background: isSelected ? "var(--accent-soft)" : "transparent",
                  color: isSelected ? "var(--primary-text)" : "var(--text-primary)",
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "background var(--transition-fast)",
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) e.currentTarget.style.background = "var(--bg-surface-hover)";
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) e.currentTarget.style.background = "transparent";
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <Icon size={14} style={{ color: isSelected ? "var(--primary)" : "var(--text-muted)" }} />
                  <div>
                    <div style={{ fontWeight: isSelected ? 600 : 400 }}>{t.name}</div>
                    <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", lineHeight: 1.2 }}>
                      {t.description.split(",")[0]}
                    </div>
                  </div>
                </div>
                {isSelected && <Check size={14} style={{ color: "var(--primary)" }} />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
