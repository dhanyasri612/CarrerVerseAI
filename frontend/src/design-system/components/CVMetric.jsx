import React from "react";

export function CVMetric({
  label,
  value,
  unit,
  trend,
  trendDirection = "up", // 'up' | 'down' | 'neutral'
  caption,
  icon: Icon,
  className = "",
}) {
  return (
    <div
      className={`cv-metric ${className}`}
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "0.25rem",
        padding: "var(--cv-space-4)",
        backgroundColor: "var(--cv-surface)",
        borderRadius: "var(--cv-radius-md)",
        border: "1px solid var(--cv-border-subtle)",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          color: "var(--cv-text-muted)",
          fontSize: "0.75rem",
          fontWeight: "600",
          letterSpacing: "0.04em",
          textTransform: "uppercase",
        }}
      >
        <span>{label}</span>
        {Icon && <Icon size={14} color="var(--cv-text-faint)" />}
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          gap: "0.375rem",
          marginTop: "0.125rem",
        }}
      >
        <span
          style={{
            fontFamily: "var(--cv-font-mono)",
            fontSize: "1.75rem",
            fontWeight: "700",
            color: "var(--cv-text)",
            lineHeight: "1.1",
            letterSpacing: "-0.03em",
          }}
        >
          {value}
        </span>
        {unit && (
          <span style={{ fontSize: "0.875rem", color: "var(--cv-text-muted)", fontWeight: "500" }}>
            {unit}
          </span>
        )}
      </div>

      {(caption || trend) && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
            fontSize: "0.75rem",
            color: "var(--cv-text-muted)",
            marginTop: "0.25rem",
          }}
        >
          {trend && (
            <span
              style={{
                color:
                  trendDirection === "up"
                    ? "var(--cv-success)"
                    : trendDirection === "down"
                    ? "var(--cv-danger)"
                    : "var(--cv-text-muted)",
                fontWeight: "600",
                fontFamily: "var(--cv-font-mono)",
              }}
            >
              {trend}
            </span>
          )}
          {caption && <span>{caption}</span>}
        </div>
      )}
    </div>
  );
}

export function CVEmptyState({
  icon: Icon,
  title,
  description,
  action,
  secondaryAction,
  className = "",
  compact = false,
}) {
  return (
    <div
      className={`cv-empty-state ${className}`}
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        padding: compact ? "var(--cv-space-6) var(--cv-space-4)" : "var(--cv-space-12) var(--cv-space-6)",
        borderRadius: "var(--cv-radius-lg)",
        backgroundColor: "var(--cv-bg-subtle)",
        border: "1px dashed var(--cv-border-strong)",
        maxWidth: "540px",
        margin: "0 auto",
      }}
    >
      {Icon && (
        <div
          style={{
            width: compact ? "40px" : "56px",
            height: compact ? "40px" : "56px",
            borderRadius: "50%",
            backgroundColor: "var(--cv-surface)",
            border: "1px solid var(--cv-border)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "var(--cv-accent)",
            marginBottom: "var(--cv-space-4)",
            boxShadow: "var(--cv-shadow-sm)",
          }}
        >
          <Icon size={compact ? 20 : 26} />
        </div>
      )}
      <h3
        className="cv-headline"
        style={{
          margin: "0 0 0.5rem 0",
          fontSize: compact ? "1rem" : "1.125rem",
          color: "var(--cv-text)",
        }}
      >
        {title}
      </h3>
      <p
        className="cv-caption"
        style={{
          margin: "0 0 var(--cv-space-6) 0",
          maxWidth: "420px",
          color: "var(--cv-text-muted)",
          lineHeight: "1.5",
        }}
      >
        {description}
      </p>
      {(action || secondaryAction) && (
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
          {action}
          {secondaryAction}
        </div>
      )}
    </div>
  );
}

export function CVSkeleton({
  width = "100%",
  height = "20px",
  borderRadius = "var(--cv-radius-sm)",
  className = "",
  style = {},
}) {
  return (
    <div
      className={`cv-skeleton cv-shimmer-bg ${className}`}
      style={{
        width,
        height,
        borderRadius,
        ...style,
      }}
    />
  );
}
