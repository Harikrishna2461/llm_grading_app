export default function ScoreCard({ scores }) {
  if (!scores) return null;

  const sections = ["describe", "evaluate", "explain", "plan"];

  return (
    <div className="score-card">
      <h3 className="score-card-title">D.E.E.P Score</h3>
      <div className="score-grid">
        {sections.map((key) => {
          const s = scores[key];
          if (!s) return null;
          const pct = Math.round((s.score / s.max) * 100);
          return (
            <div key={key} className="score-item">
              <div className="score-label">{key.charAt(0).toUpperCase() + key.slice(1)}</div>
              <div className="score-bar-wrap">
                <div
                  className="score-bar"
                  style={{ width: `${pct}%` }}
                  title={`${s.score}/${s.max}`}
                />
              </div>
              <div className="score-value">
                {s.score}/{s.max}
              </div>
            </div>
          );
        })}
      </div>
      {scores.total && (
        <div className="score-total">
          Total: <strong>{scores.total.score}</strong> / {scores.total.max}
        </div>
      )}
    </div>
  );
}
