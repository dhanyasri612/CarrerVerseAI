import React, { useEffect } from "react";
import { X } from "lucide-react";
import { CVIconButton } from "./CVButton";

export function CVDrawer({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  width = "460px",
  position = "right", // 'right' | 'left'
  className = "",
}) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    if (isOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: "var(--cv-z-drawer)",
        display: "flex",
        justifyContent: position === "right" ? "flex-end" : "flex-start",
      }}
    >
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: "rgba(0, 0, 0, 0.4)",
          backdropFilter: "blur(4px)",
          animation: "cv-fade-in var(--cv-dur-micro) var(--cv-ease-out)",
        }}
      />

      {/* Drawer Panel */}
      <div
        className={`cv-drawer cv-animate-slide-right ${className}`}
        style={{
          position: "relative",
          width: "100%",
          maxWidth: width,
          height: "100%",
          backgroundColor: "var(--cv-surface)",
          borderLeft: position === "right" ? "1px solid var(--cv-border)" : "none",
          borderRight: position === "left" ? "1px solid var(--cv-border)" : "none",
          boxShadow: "var(--cv-shadow-popover)",
          display: "flex",
          flexDirection: "column",
          zIndex: 1,
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "var(--cv-space-5) var(--cv-space-6)",
            borderBottom: "1px solid var(--cv-border-subtle)",
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            gap: "1rem",
          }}
        >
          <div>
            <h3
              className="cv-headline"
              style={{ margin: 0, fontSize: "1.125rem", color: "var(--cv-text)" }}
            >
              {title}
            </h3>
            {subtitle && (
              <p
                className="cv-caption"
                style={{ margin: "0.25rem 0 0 0", color: "var(--cv-text-muted)" }}
              >
                {subtitle}
              </p>
            )}
          </div>
          <CVIconButton icon={X} label="Close drawer" onClick={onClose} size="sm" />
        </div>

        {/* Content Body */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "var(--cv-space-6)",
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
}

export function CVModal({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  maxWidth = "560px",
  className = "",
}) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    if (isOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: "var(--cv-z-modal)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "var(--cv-space-4)",
      }}
    >
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
      <div
        className={`cv-modal cv-animate-fade-scale ${className}`}
        style={{
          position: "relative",
          width: "100%",
          maxWidth,
          backgroundColor: "var(--cv-surface)",
          border: "1px solid var(--cv-border)",
          borderRadius: "var(--cv-radius-lg)",
          boxShadow: "var(--cv-shadow-popover)",
          display: "flex",
          flexDirection: "column",
          maxHeight: "90vh",
          zIndex: 1,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            padding: "var(--cv-space-5) var(--cv-space-6)",
            borderBottom: "1px solid var(--cv-border-subtle)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div>
            <h3
              className="cv-headline"
              style={{ margin: 0, fontSize: "1.125rem", color: "var(--cv-text)" }}
            >
              {title}
            </h3>
            {subtitle && (
              <p
                className="cv-caption"
                style={{ margin: "0.25rem 0 0 0", color: "var(--cv-text-muted)" }}
              >
                {subtitle}
              </p>
            )}
          </div>
          <CVIconButton icon={X} label="Close modal" onClick={onClose} size="sm" />
        </div>
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "var(--cv-space-6)",
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
}
