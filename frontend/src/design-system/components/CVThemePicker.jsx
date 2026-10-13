import React, { useState, useRef, useEffect } from "react";
import { Palette, Check, Sparkles } from "lucide-react";
import { useTheme } from "../../context/ThemeContext";

export function CVThemePicker({ variant = "popover" }) {
  const { theme, setTheme, themes, currentThemeMeta } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const popoverRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div style={{ position: "relative" }} ref={popoverRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Theme Studio"
        title={`Theme Studio: ${currentThemeMeta.name}`}
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "0.5rem",
          padding: "0.375rem 0.75rem",
          borderRadius: "var(--cv-radius-full)",
          backgroundColor: "var(--cv-surface-active)",
          border: "1px solid var(--cv-border)",
          color: "var(--cv-text)",
          fontSize: "0.8125rem",
          fontWeight: "600",
          cursor: "pointer",
          transition: "all var(--cv-dur-micro) var(--cv-ease-out)",
        }}
      >
        <span
          style={{
            width: "12px",
            height: "12px",
            borderRadius: "50%",
            backgroundColor: currentThemeMeta.preview.accent,
            border: "1.5px solid var(--cv-border)",
            display: "inline-block",
          }}
        />
        <span style={{ display: "inline-block" }}>{currentThemeMeta.name}</span>
      </button>

      {isOpen && (
        <div
          className="cv-theme-studio cv-animate-fade-scale"
          style={{
            position: "absolute",
            top: "calc(100% + 8px)",
            right: 0,
            width: "320px",
            backgroundColor: "var(--cv-surface)",
            border: "1px solid var(--cv-border)",
            borderRadius: "var(--cv-radius-lg)",
            boxShadow: "var(--cv-shadow-popover)",
            zIndex: "var(--cv-z-popover)",
            padding: "var(--cv-space-4)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "var(--cv-space-3)",
              paddingBottom: "var(--cv-space-2)",
              borderBottom: "1px solid var(--cv-border-subtle)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "0.375rem" }}>
              <Palette size={14} color="var(--cv-accent)" />
              <span style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--cv-text)" }}>
                Theme Studio
              </span>
            </div>
            <span style={{ fontSize: "0.6875rem", color: "var(--cv-text-muted)" }}>
              5 Curated Palettes
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {themes.map((t) => {
              const isSelected = theme === t.id;
              return (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => {
                    setTheme(t.id);
                    setIsOpen(false);
                  }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "0.5rem 0.625rem",
                    borderRadius: "var(--cv-radius-sm)",
                    backgroundColor: isSelected ? "var(--cv-surface-active)" : "transparent",
                    border: isSelected ? "1px solid var(--cv-accent)" : "1px solid transparent",
                    cursor: "pointer",
                    textAlign: "left",
                    transition: "all var(--cv-dur-micro) var(--cv-ease-out)",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "0.625rem" }}>
                    {/* Swatch Pill */}
                    <div
                      style={{
                        width: "28px",
                        height: "28px",
                        borderRadius: "var(--cv-radius-sm)",
                        backgroundColor: t.preview.bg,
                        border: "1px solid var(--cv-border)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        position: "relative",
                        overflow: "hidden",
                      }}
                    >
                      <span
                        style={{
                          position: "absolute",
                          bottom: "-4px",
                          right: "-4px",
                          width: "14px",
                          height: "14px",
                          borderRadius: "50%",
                          backgroundColor: t.preview.accent,
                        }}
                      />
                    </div>
                    <div>
                      <div style={{ fontSize: "0.8125rem", fontWeight: "600", color: "var(--cv-text)" }}>
                        {t.name}
                      </div>
                      <div style={{ fontSize: "0.6875rem", color: "var(--cv-text-muted)" }}>
                        {t.personality}
                      </div>
                    </div>
                  </div>
                  {isSelected && <Check size={14} color="var(--cv-accent)" />}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
