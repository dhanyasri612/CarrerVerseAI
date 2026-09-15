export default function FeaturePage({ eyebrow, title, description, children }) {
  return (
    <div className="feature-page">
      <div className="section-header compact">
        <p className="eyebrow">{eyebrow}</p>
        <h2>{title}</h2>
        {description ? <p className="page-description">{description}</p> : null}
      </div>
      {children}
    </div>
  );
}
