import React from "react";

export function CVCard({
  children,
  variant = "flat", // 'flat' | 'raised' | 'outlined' | 'subtle' | 'ghost'
  padding = "md",   // 'none' | 'sm' | 'md' | 'lg' | 'xl'
  hover = false,
  interactive = false,
  className = "",
  onClick,
  style = {},
  ...props
}) {
  const paddingMap = {
    none: "0",
    sm: "var(--cv-space-3)",
    md: "var(--cv-space-5)",
    lg: "var(--cv-space-8)",
    xl: "var(--cv-space-10)",
  };

  const getVariantStyles = () => {
    switch (variant) {
      case "raised":
        return {
          backgroundColor: "var(--cv-surface-raised)",
          border: "1px solid var(--cv-border)",
          boxShadow: "var(--cv-shadow-md)",
        };
      case "outlined":
        return {
          backgroundColor: "transparent",
          border: "1px solid var(--cv-border)",
          boxShadow: "none",
        };
      case "subtle":
        return {
          backgroundColor: "var(--cv-bg-subtle)",
          border: "1px solid var(--cv-border-subtle)",
          boxShadow: "none",
        };
      case "ghost":
        return {
          backgroundColor: "transparent",
          border: "none",
          boxShadow: "none",
        };
      case "flat":
      default:
        return {
          backgroundColor: "var(--cv-surface)",
          border: "1px solid var(--cv-border)",
          boxShadow: "var(--cv-shadow-sm)",
        };
    }
  };

  return (
    <div
      onClick={onClick}
      className={`cv-card cv-card--${variant} ${hover ? "cv-card--hover" : ""} ${interactive ? "cv-card--interactive" : ""} ${className}`}
      style={{
        borderRadius: "var(--cv-radius-md)",
        padding: paddingMap[padding] || paddingMap.md,
        transition: "all var(--cv-dur-standard) var(--cv-ease-out)",
        cursor: onClick || interactive ? "pointer" : "default",
        position: "relative",
        ...getVariantStyles(),
        ...style,
      }}
      {...props}
    >
      {children}
    </div>
  );
}

export function CVSection({
  eyebrow,
  number,
  title,
  subtitle,
  action,
  children,
  className = "",
  style = {},
}) {
  return (
    <section
      className={`cv-section ${className}`}
      style={{
        marginBottom: "var(--cv-space-10)",
        ...style,
      }}
    >
      {(eyebrow || number || title || action) && (
        <div
          style={{
            display: "flex",
            alignItems: "flex-end",
            justifyContent: "space-between",
            marginBottom: "var(--cv-space-4)",
            gap: "var(--cv-space-4)",
            flexWrap: "wrap",
            borderBottom: "1px solid var(--cv-border-subtle)",
            paddingBottom: "var(--cv-space-3)",
          }}
        >
          <div>
            {(eyebrow || number) && (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  marginBottom: "0.25rem",
                }}
              >
                {number && <span className="cv-section-num">{number}</span>}
                {eyebrow && <span className="cv-eyebrow">{eyebrow}</span>}
              </div>
            )}
            {title && (
              <h2
                className="cv-headline"
                style={{ margin: 0, color: "var(--cv-text)" }}
              >
                {title}
              </h2>
            )}
            {subtitle && (
              <p
                className="cv-caption"
                style={{ margin: "0.25rem 0 0 0", color: "var(--cv-text-muted)" }}
              >
                {subtitle}
              </p>
            )}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div>{children}</div>
    </section>
  );
}

export function CVDivider({
  label,
  dashed = false,
  className = "",
  style = {},
}) {
  if (label) {
    return (
      <div
        className={`cv-divider cv-divider--labeled ${className}`}
        style={{
          display: "flex",
          alignItems: "center",
          gap: "1rem",
          margin: "var(--cv-space-6) 0",
          ...style,
        }}
      >
        <div style={{ flex: 1, height: "1px", backgroundColor: "var(--cv-border)" }} />
        <span
          style={{
            fontSize: "0.75rem",
            fontWeight: "600",
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            color: "var(--cv-text-muted)",
          }}
        >
          {label}
        </span>
        <div style={{ flex: 1, height: "1px", backgroundColor: "var(--cv-border)" }} />
      </div>
    );
  }

  return (
    <hr
      className={`cv-divider ${className}`}
      style={{
        border: "none",
        borderTop: dashed ? "1px dashed var(--cv-border)" : "1px solid var(--cv-border)",
        margin: "var(--cv-space-6) 0",
        ...style,
      }}
    />
  );
}
