import React from "react";

export function CVBadge({
  children,
  variant = "neutral", // 'accent' | 'success' | 'warning' | 'danger' | 'info' | 'neutral' | 'outline'
  size = "md",          // 'sm' | 'md'
  icon: Icon,
  className = "",
  style = {},
}) {
  const getColors = () => {
    switch (variant) {
      case "accent":
        return { bg: "var(--cv-accent-soft)", text: "var(--cv-accent)", border: "var(--cv-accent-border)" };
      case "success":
        return { bg: "var(--cv-success-soft)", text: "var(--cv-success)", border: "transparent" };
      case "warning":
        return { bg: "var(--cv-warning-soft)", text: "var(--cv-warning)", border: "transparent" };
      case "danger":
        return { bg: "var(--cv-danger-soft)", text: "var(--cv-danger)", border: "transparent" };
      case "info":
        return { bg: "var(--cv-info-soft)", text: "var(--cv-info)", border: "transparent" };
      case "outline":
        return { bg: "transparent", text: "var(--cv-text-muted)", border: "var(--cv-border)" };
      case "neutral":
      default:
        return { bg: "var(--cv-surface-active)", text: "var(--cv-text)", border: "var(--cv-border-subtle)" };
    }
  };

  const { bg, text, border } = getColors();

  return (
    <span
      className={`cv-badge cv-badge--${variant} ${className}`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "0.3125rem",
        fontSize: size === "sm" ? "0.6875rem" : "0.75rem",
        fontWeight: "600",
        fontFamily: "var(--cv-font-sans)",
        letterSpacing: "0.02em",
        padding: size === "sm" ? "0.15rem 0.45rem" : "0.25rem 0.625rem",
        borderRadius: "var(--cv-radius-full)",
        backgroundColor: bg,
        color: text,
        border: `1px solid ${border}`,
        lineHeight: "1.2",
        ...style,
      }}
    >
      {Icon && <Icon size={size === "sm" ? 10 : 12} />}
      {children}
    </span>
  );
}

export function CVPill({
  label,
  value,
  variant = "neutral",
  size = "md",
  className = "",
  onClick,
}) {
  return (
    <div
      onClick={onClick}
      className={`cv-pill ${onClick ? "cv-pill--interactive" : ""} ${className}`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "0.375rem",
        padding: size === "sm" ? "0.2rem 0.5rem" : "0.3125rem 0.75rem",
        borderRadius: "var(--cv-radius-full)",
        backgroundColor: "var(--cv-surface-active)",
        border: "1px solid var(--cv-border)",
        fontSize: size === "sm" ? "0.75rem" : "0.8125rem",
        color: "var(--cv-text)",
        cursor: onClick ? "pointer" : "default",
        transition: "all var(--cv-dur-micro) var(--cv-ease-out)",
      }}
    >
      <span style={{ fontWeight: "500" }}>{label}</span>
      {value !== undefined && (
        <span
          style={{
            fontFamily: "var(--cv-font-mono)",
            fontSize: "0.6875rem",
            fontWeight: "700",
            backgroundColor: "var(--cv-bg)",
            color: "var(--cv-accent)",
            padding: "0.05rem 0.35rem",
            borderRadius: "var(--cv-radius-full)",
          }}
        >
          {value}
        </span>
      )}
    </div>
  );
}

export function CVSignalDot({
  status = "ready", // 'ready' | 'running' | 'warning' | 'error' | 'idle'
  size = 8,
  pulse = false,
}) {
  const getColor = () => {
    switch (status) {
      case "ready":
      case "success":
        return "var(--cv-success)";
      case "running":
        return "var(--cv-accent)";
      case "warning":
        return "var(--cv-warning)";
      case "error":
        return "var(--cv-danger)";
      case "idle":
      default:
        return "var(--cv-text-faint)";
    }
  };

  const color = getColor();

  return (
    <span
      style={{
        display: "inline-block",
        width: `${size}px`,
        height: `${size}px`,
        borderRadius: "50%",
        backgroundColor: color,
        boxShadow: pulse ? `0 0 0 0 ${color}` : "none",
        animation: pulse ? "cv-pulse-glow 1.8s infinite" : "none",
        flexShrink: 0,
      }}
    />
  );
}
