import ScoreCard from "./ScoreCard.jsx";

const SECTION_LABELS = {
  describe: "Describe",
  evaluate: "Evaluate",
  explain: "Explain",
  plan: "Plan",
};

function SectionBlock({ name, content, isActive }) {
  if (!content && !isActive) return null;
  return (
    <div className={`section-block ${isActive ? "section-active" : ""}`}>
      <h4 className="section-heading">{SECTION_LABELS[name] ?? name}</h4>
      <p className="section-content">
        {content}
        {isActive && <span className="cursor-blink">|</span>}
      </p>
    </div>
  );
}

export default function GradingPanel({ grading }) {
  const { status, sections, activeSection, scores, error } = grading;

  const hasContent = Object.values(sections).some((v) => v.length > 0);

  return (
    <div className="panel grading-panel">
      <div className="panel-header">
        <h2 className="panel-title">Grading</h2>
        <span className={`status-badge status-${status}`}>{status}</span>
      </div>

      {error && <div className="error-box">{error}</div>}

      {scores && <ScoreCard scores={scores} />}

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
        <p className="panel-placeholder">Grading results will appear here.</p>
      )}
    </div>
  );
}
