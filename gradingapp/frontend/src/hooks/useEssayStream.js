import { useState, useCallback, useRef } from "react";
import { parseNdjsonStream } from "../utils/ndjsonParser.js";

const initialState = {
  grading: {
    status: "idle", // idle | streaming | done | error
    sections: {
      describe: "",
      evaluate: "",
      explain: "",
      plan: "",
    },
    activeSection: null,
    scores: null,
    error: null,
  },
  review: {
    status: "idle",
    sections: {
      review: "",
      refined_essay: "",
    },
    activeSection: null,
    error: null,
  },
  isStreaming: false,
};

export function useEssayStream() {
  const [state, setState] = useState(initialState);
  const abortRef = useRef(null);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setState(initialState);
  }, []);

  const submit = useCallback(async (essay) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setState({
      ...initialState,
      isStreaming: true,
      grading: { ...initialState.grading, status: "streaming" },
      review: { ...initialState.review, status: "streaming" },
    });

    try {
      const response = await fetch("/api/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ essay, submission_id: crypto.randomUUID() }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      let gradingDone = false;
      let reviewDone = false;

      await parseNdjsonStream(
        response,
        (event) => {
          const { source, event: evtType, component, text, scores, message } = event;

          const isGrading = source === "grading_agent";
          const agentKey = isGrading ? "grading" : "review";

          setState((prev) => {
            const agent = { ...prev[agentKey] };

            switch (evtType) {
              case "agent_start":
                agent.status = "streaming";
                break;

              case "section_start":
                agent.activeSection = component;
                break;

              case "text_delta":
                if (component && agent.sections[component] !== undefined) {
                  agent.sections = {
                    ...agent.sections,
                    [component]: agent.sections[component] + text,
                  };
                }
                break;

              case "section_end":
                agent.activeSection = null;
                break;

              case "agent_done":
                agent.status = isGrading ? agent.status : "done";
                if (!isGrading) reviewDone = true;
                break;

              case "scores":
                agent.scores = scores;
                agent.status = "done";
                gradingDone = true;
                break;

              case "error":
                agent.status = "error";
                agent.error = message;
                break;
            }

            const bothDone = gradingDone && reviewDone;
            return {
              ...prev,
              [agentKey]: agent,
              isStreaming: !bothDone,
            };
          });
        },
        () => {
          setState((prev) => ({ ...prev, isStreaming: false }));
        }
      );
    } catch (err) {
      if (err.name === "AbortError") return;
      setState((prev) => ({
        ...prev,
        isStreaming: false,
        grading: { ...prev.grading, status: "error", error: err.message },
        review: { ...prev.review, status: "error", error: err.message },
      }));
    }
  }, []);

  return { state, submit, reset };
}
