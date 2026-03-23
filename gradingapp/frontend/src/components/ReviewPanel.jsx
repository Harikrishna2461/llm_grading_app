const SECTION_LABELS = {
  review: "Editorial Review",
  refined_essay: "Refined Essay",
};

function SectionBlock({ name, content, isActive }) {
  if (!content && !isActive) return null;
  return (
    <div className={`section-block ${isActive ? "section-active" : ""}`}>
      <h4 className="section-heading">{SECTION_LABELS[name] ?? name}</h4>
      {name === "refined_essay" ? (
        <pre className="section-content refined-essay">
          {content}
          {isActive && <span className="cursor-blink">|</span>}
        </pre>
      ) : (
        <p className="section-content">
          {content}
          {isActive && <span className="cursor-blink">|</span>}
        </p>
      )}
    </div>
  );
}

export default function ReviewPanel({ review }) {
  const { status, sections, activeSection, error } = review;

  const hasContent = Object.values(sections).some((v) => v.length > 0);

  return (
    <div className="panel review-panel">
      <div className="panel-header">
        <h2 className="panel-title">Review & Refine</h2>
        <span className={`status-badge status-${status}`}>{status}</span>
      </div>

      {error && <div className="error-box">{error}</div>}

      {(hasContent || status === "streaming") && (
        <div className="sections">
          {Object.entries(sections).map(([key, content]) => (
            <SectionBlock
              key={key}
              name={key}
              content={content}
              isActive={activeSection === key}
            />
          ))}
        </div>
      )}

      {status === "idle" && (
        <p className="panel-placeholder">Review and refinement will appear here.</p>
      )}
    </div>
  );
}
