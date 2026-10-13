import { ArrowUpRight } from "lucide-react";

export function PageShell({ children, className = "" }) {
  return <div className={`page-shell ${className}`.trim()}>{children}</div>;
}

export function PageHeader({ eyebrow, title, description, actions }) {
  return (
    <div className="page-header">
      <div className="page-header-copy">
        {eyebrow ? <span className="page-header-eyebrow">{eyebrow}</span> : null}
        <h1>{title}</h1>
        {description ? <p>{description}</p> : null}
      </div>
      {actions ? <div className="page-header-actions">{actions}</div> : null}
    </div>
  );
}

export function SectionHeader({ eyebrow, title, description, actions }) {
  return (
    <div className="ui-section-header">
      <div>
        {eyebrow ? <span className="ui-section-eyebrow">{eyebrow}</span> : null}
        <h2>{title}</h2>
        {description ? <p>{description}</p> : null}
      </div>
      {actions ? <div className="ui-section-actions">{actions}</div> : null}
    </div>
  );
}

export function InsightCard({ title, description, icon: Icon, children, className = "" }) {
  return (
    <article className={`insight-card ${className}`.trim()}>
      {Icon ? (
        <div className="insight-card-icon" aria-hidden="true">
          <Icon size={18} />
        </div>
      ) : null}
      <div className="insight-card-copy">
        {title ? <h3>{title}</h3> : null}
        {description ? <p>{description}</p> : null}
        {children}
      </div>
    </article>
  );
}

export function EvidenceBadge({ children, verified = false }) {
  return (
    <span className={`evidence-badge ${verified ? "verified" : ""}`.trim()}>
      <span className="evidence-badge-dot" aria-hidden="true" />
      {children}
    </span>
  );
}

export function SkillChip({ children, tone = "default" }) {
  return <span className={`skill-chip skill-chip-${tone}`}>{children}</span>;
}

export function PriorityBadge({ children, level = "medium" }) {
  return <span className={`priority-badge priority-${level}`}>{children}</span>;
}

export function ActionButton({ children, href, onClick, variant = "primary", icon = true, ...props }) {
  const content = (
    <>
      <span>{children}</span>
      {icon ? <ArrowUpRight size={15} aria-hidden="true" /> : null}
    </>
  );

  if (href) {
    return <a className={`action-button action-button-${variant}`} href={href} {...props}>{content}</a>;
  }

  return <button className={`action-button action-button-${variant}`} type="button" onClick={onClick} {...props}>{content}</button>;
}
