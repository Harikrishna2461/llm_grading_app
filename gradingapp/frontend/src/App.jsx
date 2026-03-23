import "./App.css";
import EssayForm from "./components/EssayForm.jsx";
import GradingPanel from "./components/GradingPanel.jsx";
import ReviewPanel from "./components/ReviewPanel.jsx";
import { useEssayStream } from "./hooks/useEssayStream.js";

export default function App() {
  const { state, submit, reset } = useEssayStream();
  const { grading, review, isStreaming } = state;

  const hasResults =
    grading.status !== "idle" || review.status !== "idle";

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">Essay Grading &amp; Review Platform</h1>
        <p className="app-subtitle">
          AI-powered D.E.E.P grading and editorial refinement
        </p>
      </header>

      <main className="app-main">
        <section className="form-section">
          <EssayForm
            onSubmit={submit}
            onReset={reset}
            isStreaming={isStreaming}
          />
        </section>

        {hasResults && (
          <section className="results-section">
            <div className="panels">
              <GradingPanel grading={grading} />
              <ReviewPanel review={review} />
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
