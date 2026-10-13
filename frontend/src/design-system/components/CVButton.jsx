import React from "react";

export function CVButton({
  children,
  variant = "primary", // 'primary' | 'secondary' | 'subtle' | 'outline' | 'ghost' | 'danger'
  size = "md",          // 'sm' | 'md' | 'lg'
  icon: Icon,
  iconPosition = "left",
  loading = false,
  disabled = false,
  className = "",
  onClick,
  type = "button",
  ...props
}) {
  const baseStyles = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: size === "sm" ? "0.375rem" : "0.5rem",
    fontWeight: "600",
    fontFamily: "var(--cv-font-sans)",
    borderRadius: "var(--cv-radius-sm)",
    transition: "all var(--cv-dur-micro) var(--cv-ease-out)",
    cursor: disabled || loading ? "not-allowed" : "pointer",
    opacity: disabled ? 0.5 : 1,
    border: "1px solid transparent",
    outline: "none",
    textDecoration: "none",
    whiteSpace: "nowrap",
  };

  const sizeStyles = {
    sm: { padding: "0.375rem 0.75rem", fontSize: "0.8125rem", height: "32px" },
    md: { padding: "0.5rem 1.125rem", fontSize: "0.875rem", height: "40px" },
    lg: { padding: "0.75rem 1.5rem", fontSize: "1rem", height: "48px" },
  }[size] || { padding: "0.5rem 1.125rem", fontSize: "0.875rem", height: "40px" };

  const getVariantStyles = () => {
    switch (variant) {
      case "primary":
        return {
          backgroundColor: "var(--cv-accent)",
          color: "var(--cv-accent-contrast)",
          borderColor: "var(--cv-accent)",
          boxShadow: "var(--cv-shadow-sm)",
        };
      case "secondary":
        return {
          backgroundColor: "var(--cv-surface-active)",
          color: "var(--cv-text)",
          borderColor: "var(--cv-border)",
        };
      case "subtle":
        return {
          backgroundColor: "var(--cv-accent-soft)",
          color: "var(--cv-accent)",
          borderColor: "transparent",
        };
      case "outline":
        return {
          backgroundColor: "transparent",
          color: "var(--cv-text)",
          borderColor: "var(--cv-border-strong)",
        };
      case "ghost":
        return {
          backgroundColor: "transparent",
          color: "var(--cv-text-muted)",
          borderColor: "transparent",
        };
      case "danger":
        return {
          backgroundColor: "var(--cv-danger)",
          color: "#FFFFFF",
          borderColor: "var(--cv-danger)",
        };
      default:
        return {};
    }
  };

  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={`cv-button cv-button--${variant} cv-button--${size} ${className}`}
      style={{ ...baseStyles, ...sizeStyles, ...getVariantStyles() }}
      {...props}
    >
      {loading ? (
        <span
          style={{
            width: "14px",
            height: "14px",
            border: "2px solid currentColor",
            borderRightColor: "transparent",
            borderRadius: "50%",
            animation: "cv-orbit-slow 0.6s linear infinite",
            display: "inline-block",
          }}
        />
      ) : Icon && iconPosition === "left" ? (
        <Icon size={size === "sm" ? 14 : size === "lg" ? 18 : 16} />
      ) : null}
      <span>{children}</span>
      {!loading && Icon && iconPosition === "right" ? (
        <Icon size={size === "sm" ? 14 : size === "lg" ? 18 : 16} />
      ) : null}
    </button>
  );
}

export function CVIconButton({
  icon: Icon,
  label,
  variant = "ghost",
  size = "md",
  disabled = false,
  className = "",
  onClick,
  ...props
}) {
  const sizeMap = {
    sm: { width: "32px", height: "32px", iconSize: 14 },
    md: { width: "38px", height: "38px", iconSize: 16 },
    lg: { width: "44px", height: "44px", iconSize: 20 },
  };

  const { width, height, iconSize } = sizeMap[size] || sizeMap.md;

  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      disabled={disabled}
      onClick={onClick}
      className={`cv-icon-button ${className}`}
      style={{
        width,
        height,
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        borderRadius: "var(--cv-radius-sm)",
        border: variant === "outline" ? "1px solid var(--cv-border)" : "1px solid transparent",
        backgroundColor: variant === "secondary" ? "var(--cv-surface-active)" : variant === "subtle" ? "var(--cv-accent-soft)" : "transparent",
        color: variant === "subtle" ? "var(--cv-accent)" : "var(--cv-text)",
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.5 : 1,
        transition: "all var(--cv-dur-micro) var(--cv-ease-out)",
      }}
      {...props}
    >
      {Icon && <Icon size={iconSize} />}
    </button>
  );
}
