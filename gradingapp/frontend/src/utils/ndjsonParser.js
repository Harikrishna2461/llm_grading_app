/**
 * Parse a ReadableStream of NDJSON lines and call onEvent for each parsed object.
 * Calls onDone when the stream ends.
 */
export async function parseNdjsonStream(response, onEvent, onDone) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      // Keep last (potentially incomplete) line in buffer
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        try {
          const event = JSON.parse(trimmed);
          onEvent(event);
        } catch {
          // skip malformed lines
        }
      }
    }

    // Handle any remaining buffer content
    if (buffer.trim()) {
      try {
        const event = JSON.parse(buffer.trim());
        onEvent(event);
      } catch {
        // skip
      }
    }
  } finally {
    reader.releaseLock();
    onDone?.();
  }
}
