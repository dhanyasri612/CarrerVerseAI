import { AlertCircle, Inbox, RotateCcw } from "lucide-react";

export function LoadingState({
  label = "Loading your career intelligence...",
}) {
  return (
    <div className="loading-state-container" role="status" aria-live="polite">
      <div className="spinner" aria-hidden="true" />
      <p className="section-description">{label}</p>
    </div>
  );
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="error-state-card" role="alert">
      <AlertCircle size={20} aria-hidden="true" />
      <div className="error-state-content">
        <div className="error-state-title">Something needs attention</div>
        <div className="error-state-text">
          {message || "Unable to load this view right now."}
        </div>
      </div>
      {onRetry ? (
        <button className="ghost-button" type="button" onClick={onRetry}>
          <RotateCcw size={14} aria-hidden="true" />
          Try again
        </button>
      ) : null}
    </div>
  );
}

export function EmptyState({ title, children, action }) {
  return (
    <div className="empty-state-card">
      <div className="empty-state-icon" aria-hidden="true">
        <Inbox size={22} />
      </div>
      <div className="empty-state-title">{title}</div>
      {children ? <div className="empty-state-text">{children}</div> : null}
      {action ? <div style={{ marginTop: 8 }}>{action}</div> : null}
    </div>
  );
}
