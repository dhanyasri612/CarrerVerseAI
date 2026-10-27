import React, { forwardRef } from "react";
import { Loader2 } from "lucide-react";
import "./ThemeComponents.css";

/* ── 1. Page Header ───────────────────────────────────────────────────── */
export function PageHeader({
  eyebrow,
  title,
  accentWord,
  subtitle,
  actions,
  className = "",
  children,
}) {
  return (
    <header className={`cv-page-header ${className}`.trim()}>
      <div className="cv-page-header-top">
        <div className="cv-page-header-copy">
          {eyebrow && (
            <div className="cv-eyebrow">
              <span className="cv-eyebrow-rule" aria-hidden="true" />
              <span>{eyebrow}</span>
            </div>
          )}

          <h1 className="cv-page-title">
            {title}{" "}
            {accentWord && <span className="cv-title-accent">{accentWord}</span>}
          </h1>

          {subtitle && <p className="cv-page-subtitle">{subtitle}</p>}
        </div>

        {actions && <div className="cv-page-header-actions">{actions}</div>}
      </div>

      {children}
    </header>
  );
}

/* ── 2. Card & Panel Primitives ───────────────────────────────────────── */
export const Card = forwardRef(function Card(
  {
    children,
    variant = "default", // 'default' | 'raised' | 'ghost'
    padding = "md", // 'none' | 'sm' | 'md' | 'lg'
    interactive = false,
    selected = false,
    className = "",
    style,
    ...props
  },
  ref
) {
  const variantClass = `cv-card-${variant}`;
  const padClass = `cv-card-pad-${padding}`;
  const interactiveClass = interactive ? "cv-card-interactive" : "";
  const selectedClass = selected ? "cv-card-selected" : "";

  return (
    <div
      ref={ref}
      className={`cv-card ${variantClass} ${padClass} ${interactiveClass} ${selectedClass} ${className}`.trim()}
      style={style}
      {...props}
    >
      {children}
    </div>
  );
});

export const Panel = forwardRef(function Panel(
  {
    children,
    border = "all", // 'all' | 'top' | 'bottom' | 'left' | 'right' | 'none'
    className = "",
    style,
    ...props
  },
  ref
) {
  const borderClass = border !== "none" ? `cv-panel-border-${border}` : "";

  return (
    <div
      ref={ref}
      className={`cv-panel ${borderClass} ${className}`.trim()}
      style={style}
      {...props}
    >
      {children}
    </div>
  );
});

/* ── 3. Button Component ──────────────────────────────────────────────── */
export const Button = forwardRef(function Button(
  {
    children,
    variant = "primary", // 'primary' | 'secondary' | 'ghost' | 'danger'
    size = "md", // 'sm' | 'md' | 'lg'
    icon: Icon,
    iconPosition = "left", // 'left' | 'right'
    loading = false,
    disabled = false,
    fullWidth = false,
    className = "",
    style,
    type = "button",
    ...props
  },
  ref
) {
  const variantClass = `cv-btn-${variant}`;
  const sizeClass = `cv-btn-${size}`;
  const widthClass = fullWidth ? "cv-btn-full" : "";

  return (
    <button
      ref={ref}
      type={type}
      disabled={disabled || loading}
      aria-disabled={disabled || loading}
      className={`cv-btn ${variantClass} ${sizeClass} ${widthClass} ${className}`.trim()}
      style={style}
      {...props}
    >
      {loading ? (
        <Loader2 size={size === "sm" ? 13 : 16} className="spin-slow" aria-hidden="true" />
      ) : Icon && iconPosition === "left" ? (
        <Icon size={size === "sm" ? 13 : 16} aria-hidden="true" />
      ) : null}

      {children && <span>{children}</span>}

      {!loading && Icon && iconPosition === "right" ? (
        <Icon size={size === "sm" ? 13 : 16} aria-hidden="true" />
      ) : null}
    </button>
  );
});

/* ── 4. Form Field Wrapper ────────────────────────────────────────────── */
export function FormField({ label, optional = false, helperText, error, id, children }) {
  return (
    <div className="cv-form-field">
      {label && (
        <label htmlFor={id} className="cv-label">
          <span>{label}</span>
          {optional && <span className="cv-label-optional">(Optional)</span>}
        </label>
      )}

      {children}

      {error ? (
        <div className="cv-field-error" role="alert">
          {error}
        </div>
      ) : helperText ? (
        <div className="cv-field-helper">{helperText}</div>
      ) : null}
    </div>
  );
}

/* ── 5. Input Control ─────────────────────────────────────────────────── */
export const Input = forwardRef(function Input(
  {
    label,
    optional = false,
    helperText,
    error,
    id,
    className = "",
    style,
    ...props
  },
  ref
) {
  const inputEl = (
    <input
      ref={ref}
      id={id}
      aria-invalid={!!error}
      className={`cv-input ${error ? "cv-input-error" : ""} ${className}`.trim()}
      style={style}
      {...props}
    />
  );

  if (label || helperText || error) {
    return (
      <FormField label={label} optional={optional} helperText={helperText} error={error} id={id}>
        {inputEl}
      </FormField>
    );
  }

  return inputEl;
});

/* ── 6. Select Control ────────────────────────────────────────────────── */
export const Select = forwardRef(function Select(
  {
    label,
    optional = false,
    helperText,
    error,
    id,
    options = [],
    children,
    className = "",
    style,
    ...props
  },
  ref
) {
  const selectEl = (
    <select
      ref={ref}
      id={id}
      aria-invalid={!!error}
      className={`cv-select ${error ? "cv-select-error" : ""} ${className}`.trim()}
      style={style}
      {...props}
    >
      {options.length > 0
        ? options.map((opt) => (
            <option key={opt.value ?? opt} value={opt.value ?? opt}>
              {opt.label ?? opt}
            </option>
          ))
        : children}
    </select>
  );

  if (label || helperText || error) {
    return (
      <FormField label={label} optional={optional} helperText={helperText} error={error} id={id}>
        {selectEl}
      </FormField>
    );
  }

  return selectEl;
});

/* ── 7. Textarea Control ──────────────────────────────────────────────── */
export const Textarea = forwardRef(function Textarea(
  {
    label,
    optional = false,
    helperText,
    error,
    id,
    rows = 4,
    className = "",
    style,
    ...props
  },
  ref
) {
  const textareaEl = (
    <textarea
      ref={ref}
      id={id}
      rows={rows}
      aria-invalid={!!error}
      className={`cv-textarea ${error ? "cv-textarea-error" : ""} ${className}`.trim()}
      style={style}
      {...props}
    />
  );

  if (label || helperText || error) {
    return (
      <FormField label={label} optional={optional} helperText={helperText} error={error} id={id}>
        {textareaEl}
      </FormField>
    );
  }

  return textareaEl;
});

/* ── 8. Tabs (Underlined Style) ───────────────────────────────────────── */
export function Tabs({ tabs = [], activeTab, onChange, className = "", style }) {
  return (
    <nav className={`cv-tabs ${className}`.trim()} style={style} aria-label="Tabs">
      {tabs.map((tab) => {
        const id = tab.id ?? tab.value ?? tab;
        const label = tab.label ?? tab;
        const Icon = tab.icon;
        const isActive = activeTab === id;

        return (
          <button
            key={id}
            type="button"
            role="tab"
            aria-selected={isActive}
            className={`cv-tab-item ${isActive ? "cv-tab-active" : ""}`}
            onClick={() => onChange && onChange(id)}
          >
            {Icon && <Icon size={14} aria-hidden="true" />}
            <span>{label}</span>
            {tab.count !== undefined && (
              <span className="cv-badge cv-badge-neutral" style={{ padding: "1px 6px", fontSize: "0.68rem" }}>
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </nav>
  );
}

/* ── 9. Segmented Control (Pill Switch Style) ─────────────────────────── */
export function SegmentedControl({ options = [], value, onChange, className = "", style }) {
  return (
    <div className={`cv-segmented-control ${className}`.trim()} style={style} role="tablist">
      {options.map((opt) => {
        const optVal = opt.value ?? opt.id ?? opt;
        const optLabel = opt.label ?? opt;
        const Icon = opt.icon;
        const isSelected = value === optVal;

        return (
          <button
            key={optVal}
            type="button"
            role="tab"
            aria-selected={isSelected}
            className={`cv-segmented-btn ${isSelected ? "cv-segmented-active" : ""}`}
            onClick={() => onChange && onChange(optVal)}
          >
            {Icon && <Icon size={14} aria-hidden="true" />}
            <span>{optLabel}</span>
          </button>
        );
      })}
    </div>
  );
}

/* ── 10. Badges & Chips ───────────────────────────────────────────────── */
export function Badge({
  children,
  variant = "neutral", // 'primary' | 'success' | 'warning' | 'danger' | 'neutral'
  dot = false,
  className = "",
  style,
}) {
  return (
    <span className={`cv-badge cv-badge-${variant} ${className}`.trim()} style={style}>
      {dot && <span className="cv-badge-dot" aria-hidden="true" />}
      {children}
    </span>
  );
}

export function Chip({
  children,
  icon: Icon,
  interactive = false,
  selected = false,
  onClick,
  className = "",
  style,
  ...props
}) {
  const interactiveClass = interactive || onClick ? "cv-chip-interactive" : "";
  const selectedClass = selected ? "cv-chip-selected" : "";

  return (
    <span
      className={`cv-chip ${interactiveClass} ${selectedClass} ${className}`.trim()}
      onClick={onClick}
      style={style}
      {...props}
    >
      {Icon && <Icon size={12} aria-hidden="true" />}
      <span>{children}</span>
    </span>
  );
}

/* ── 11. Empty State ──────────────────────────────────────────────────── */
export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  className = "",
  style,
}) {
  return (
    <div className={`cv-empty-state ${className}`.trim()} style={style}>
      {Icon && (
        <div className="cv-empty-icon" aria-hidden="true">
          <Icon size={24} />
        </div>
      )}
      {title && <h3 className="cv-empty-title">{title}</h3>}
      {description && <p className="cv-empty-desc">{description}</p>}
      {action && <div>{action}</div>}
    </div>
  );
}

/* ── 12. Progress Bar ─────────────────────────────────────────────────── */
export function ProgressBar({
  value = 0,
  max = 100,
  size = "md", // 'sm' | 'md' | 'lg'
  variant = "accent", // 'accent' | 'success'
  className = "",
  style,
}) {
  const percent = Math.min(100, Math.max(0, Math.round((value / max) * 100)));
  const sizeClass = `cv-progress-track-${size}`;
  const fillVariantClass = variant === "success" ? "cv-progress-fill-success" : "";

  return (
    <div
      className={`cv-progress-track ${sizeClass} ${className}`.trim()}
      style={style}
      role="progressbar"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={max}
    >
      <div
        className={`cv-progress-fill ${fillVariantClass}`}
        style={{ width: `${percent}%` }}
      />
    </div>
  );
}
