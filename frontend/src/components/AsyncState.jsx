export function LoadingState({
  label = "Loading your career intelligence...",
}) {
  return (
    <div className="state-card loading-state">
      <span className="spinner" />
      {label}
    </div>
  );
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="state-card error-state">
      <strong>Something needs attention</strong>
      <span>{message || "Unable to load this view right now."}</span>
      {onRetry ? (
        <button className="ghost-button" type="button" onClick={onRetry}>
          Try again
        </button>
      ) : null}
    </div>
  );
}

export function EmptyState({ title, children, action }) {
  return (
    <div className="state-card empty-state-card">
      <strong>{title}</strong>
      {children ? <span>{children}</span> : null}
      {action}
    </div>
  );
}
