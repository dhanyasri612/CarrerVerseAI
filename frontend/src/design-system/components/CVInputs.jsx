import React from "react";

export function CVInput({
  label,
  error,
  hint,
  icon: Icon,
  className = "",
  style = {},
  id,
  ...props
}) {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

  return (
    <div className={`cv-field ${className}`} style={{ display: "flex", flexDirection: "column", gap: "0.375rem" }}>
      {label && (
        <label
          htmlFor={inputId}
          style={{
            fontSize: "0.8125rem",
            fontWeight: "600",
            color: "var(--cv-text)",
            letterSpacing: "0.01em",
          }}
        >
          {label}
        </label>
      )}
      <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
        {Icon && (
          <div
            style={{
              position: "absolute",
              left: "0.875rem",
              color: "var(--cv-text-muted)",
              pointerEvents: "none",
              display: "flex",
              alignItems: "center",
            }}
          >
            <Icon size={16} />
          </div>
        )}
        <input
          id={inputId}
          style={{
            width: "100%",
            height: "42px",
            padding: Icon ? "0.5rem 0.875rem 0.5rem 2.5rem" : "0.5rem 0.875rem",
            fontSize: "0.875rem",
            fontFamily: "var(--cv-font-sans)",
            backgroundColor: "var(--cv-surface)",
            color: "var(--cv-text)",
            border: error ? "1px solid var(--cv-danger)" : "1px solid var(--cv-border)",
            borderRadius: "var(--cv-radius-sm)",
            outline: "none",
            transition: "all var(--cv-dur-micro) var(--cv-ease-out)",
            ...style,
          }}
          {...props}
        />
      </div>
      {hint && !error && (
        <span style={{ fontSize: "0.75rem", color: "var(--cv-text-muted)" }}>{hint}</span>
      )}
      {error && (
        <span style={{ fontSize: "0.75rem", color: "var(--cv-danger)", fontWeight: "500" }}>
          {error}
        </span>
      )}
    </div>
  );
}

export function CVTextarea({
  label,
  error,
  hint,
  rows = 3,
  className = "",
  style = {},
  id,
  ...props
}) {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

  return (
    <div className={`cv-field ${className}`} style={{ display: "flex", flexDirection: "column", gap: "0.375rem" }}>
      {label && (
        <label
          htmlFor={inputId}
          style={{
            fontSize: "0.8125rem",
            fontWeight: "600",
            color: "var(--cv-text)",
          }}
        >
          {label}
        </label>
      )}
      <textarea
        id={inputId}
        rows={rows}
        style={{
          width: "100%",
          padding: "0.625rem 0.875rem",
          fontSize: "0.875rem",
          fontFamily: "var(--cv-font-sans)",
          backgroundColor: "var(--cv-surface)",
          color: "var(--cv-text)",
          border: error ? "1px solid var(--cv-danger)" : "1px solid var(--cv-border)",
          borderRadius: "var(--cv-radius-sm)",
          outline: "none",
          resize: "vertical",
          lineHeight: "1.5",
          transition: "all var(--cv-dur-micro) var(--cv-ease-out)",
          ...style,
        }}
        {...props}
      />
      {hint && !error && (
        <span style={{ fontSize: "0.75rem", color: "var(--cv-text-muted)" }}>{hint}</span>
      )}
      {error && (
        <span style={{ fontSize: "0.75rem", color: "var(--cv-danger)", fontWeight: "500" }}>
          {error}
        </span>
      )}
    </div>
  );
}

export function CVSelect({
  label,
  options = [],
  value,
  onChange,
  error,
  className = "",
  style = {},
  id,
  ...props
}) {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

  return (
    <div className={`cv-field ${className}`} style={{ display: "flex", flexDirection: "column", gap: "0.375rem" }}>
      {label && (
        <label
          htmlFor={inputId}
          style={{
            fontSize: "0.8125rem",
            fontWeight: "600",
            color: "var(--cv-text)",
          }}
        >
          {label}
        </label>
      )}
      <select
        id={inputId}
        value={value}
        onChange={onChange}
        style={{
          width: "100%",
          height: "42px",
          padding: "0.5rem 0.875rem",
          fontSize: "0.875rem",
          fontFamily: "var(--cv-font-sans)",
          backgroundColor: "var(--cv-surface)",
          color: "var(--cv-text)",
          border: error ? "1px solid var(--cv-danger)" : "1px solid var(--cv-border)",
          borderRadius: "var(--cv-radius-sm)",
          outline: "none",
          cursor: "pointer",
          ...style,
        }}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label || opt.value}
          </option>
        ))}
      </select>
      {error && (
        <span style={{ fontSize: "0.75rem", color: "var(--cv-danger)", fontWeight: "500" }}>
          {error}
        </span>
      )}
    </div>
  );
}

export function CVSegmentedControl({
  options = [],
  value,
  onChange,
  size = "md",
  className = "",
}) {
  return (
    <div
      className={`cv-segmented-control ${className}`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        backgroundColor: "var(--cv-bg-subtle)",
        border: "1px solid var(--cv-border)",
        borderRadius: "var(--cv-radius-sm)",
        padding: "3px",
        gap: "2px",
      }}
    >
      {options.map((opt) => {
        const isSelected = value === opt.value;
        return (
          <button
            key={opt.value}
            type="button"
            onClick={() => onChange(opt.value)}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.375rem",
              padding: size === "sm" ? "0.25rem 0.625rem" : "0.375rem 0.875rem",
              fontSize: size === "sm" ? "0.75rem" : "0.8125rem",
              fontWeight: isSelected ? "600" : "500",
              color: isSelected ? "var(--cv-text)" : "var(--cv-text-muted)",
              backgroundColor: isSelected ? "var(--cv-surface)" : "transparent",
              border: "none",
              borderRadius: "calc(var(--cv-radius-sm) - 2px)",
              boxShadow: isSelected ? "var(--cv-shadow-sm)" : "none",
              cursor: "pointer",
              transition: "all var(--cv-dur-micro) var(--cv-ease-out)",
              whiteSpace: "nowrap",
            }}
          >
            {opt.icon && <opt.icon size={14} />}
            <span>{opt.label}</span>
          </button>
        );
      })}
    </div>
  );
}
