import { useState } from "react";

export default function EssayForm({ onSubmit, onReset, isStreaming }) {
  const [essay, setEssay] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (essay.trim()) {
      onSubmit(essay.trim());
    }
  };

  const handleReset = () => {
    setEssay("");
    onReset();
  };

  return (
    <form className="essay-form" onSubmit={handleSubmit}>
      <label htmlFor="essay-input" className="essay-label">
        Paste your essay below
      </label>
      <textarea
        id="essay-input"
        className="essay-textarea"
        value={essay}
        onChange={(e) => setEssay(e.target.value)}
        placeholder="Enter your essay here..."
        rows={12}
        disabled={isStreaming}
      />
      <div className="essay-actions">
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isStreaming || !essay.trim()}
        >
          {isStreaming ? "Processing..." : "Grade & Review"}
        </button>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={handleReset}
          disabled={isStreaming}
        >
          Reset
        </button>
      </div>
    </form>
  );
}
