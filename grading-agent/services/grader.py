import json
import re
import os
from pathlib import Path
from datetime import datetime, timezone
import anthropic
from dotenv import load_dotenv

# Load .env from this dir, parent dir, or grandparent dir (covers running from service dir or project root)
_here = Path(__file__).resolve().parent
for _d in [_here, _here.parent, _here.parent.parent]:
    _env = _d / ".env"
    if _env.is_file():
        load_dotenv(_env)
        break

client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an expert essay grader using the D.E.E.P framework.
Grade the essay by producing exactly four XML-delimited sections in this order:
describe, evaluate, explain, plan.

Each section must end with a score line in this exact format: SCORE: [n]
Scores are out of 25 points each (100 total).

Output format:
<section name="describe">
Describe the essay's main argument, structure, and key points.
SCORE: [0-25]
</section>
<section name="evaluate">
Evaluate the quality of evidence, reasoning, and argumentation.
SCORE: [0-25]
</section>
<section name="explain">
Explain the strengths and weaknesses in depth.
SCORE: [0-25]
</section>
<section name="plan">
Plan specific improvements the author should make.
SCORE: [0-25]
</section>

Be thorough, fair, and constructive in your feedback."""

SECTION_ORDER = ["describe", "evaluate", "explain", "plan"]
MAX_SCORES = {"describe": 25, "evaluate": 25, "explain": 25, "plan": 25}


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _event(source: str, **kwargs) -> str:
    return json.dumps({"source": source, "timestamp": _ts(), **kwargs}) + "\n"


async def stream_grading(essay: str):
    source = "grading_agent"
    yield _event(source, event="agent_start")

    scores: dict = {}
    current_section = None
    buffer = ""
    section_open_re = re.compile(r'<section name="([^"]+)">')
    section_close_re = re.compile(r"</section>")
    score_re = re.compile(r"SCORE:\s*(\d+)")

    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Please grade the following essay:\n\n{essay}"}],
    ) as stream:
        async for text in stream.text_stream:
            buffer += text

            while buffer:
                if current_section is None:
                    # Look for section open tag
                    m = section_open_re.search(buffer)
                    if m:
                        section_name = m.group(1)
                        if section_name in SECTION_ORDER:
                            current_section = section_name
                            yield _event(source, event="section_start", component=current_section)
                            buffer = buffer[m.end():]
                        else:
                            buffer = buffer[m.end():]
                    else:
                        # No open tag yet, keep buffering (but don't lose >32 chars of non-tag text)
                        if len(buffer) > 64:
                            buffer = buffer[-32:]
                        break
                else:
                    # Inside a section — look for close tag
                    close_m = section_close_re.search(buffer)
                    if close_m:
                        chunk = buffer[: close_m.start()]
                        # Extract score from chunk
                        score_m = score_re.search(chunk)
                        score_val = int(score_m.group(1)) if score_m else 0

                        # Emit remaining text before close (strip score line for cleanliness)
                        display_chunk = score_re.sub("", chunk).strip()
                        if display_chunk:
                            yield _event(
                                source,
                                event="text_delta",
                                component=current_section,
                                text=display_chunk,
                            )

                        scores[current_section] = {
                            "score": score_val,
                            "max": MAX_SCORES[current_section],
                        }
                        yield _event(source, event="section_end", component=current_section)
                        current_section = None
                        buffer = buffer[close_m.end():]
                    else:
                        # Stream safe prefix (keep last 30 chars for partial tag detection)
                        safe_end = max(0, len(buffer) - 30)
                        if safe_end > 0:
                            chunk = buffer[:safe_end]
                            # Don't emit score line mid-stream; hold it until section ends
                            if not score_re.search(chunk):
                                yield _event(
                                    source,
                                    event="text_delta",
                                    component=current_section,
                                    text=chunk,
                                )
                            buffer = buffer[safe_end:]
                        break

    yield _event(source, event="agent_done")

    # Emit scores event
    total_score = sum(v["score"] for v in scores.values())
    total_max = sum(v["max"] for v in scores.values())
    scores["total"] = {"score": total_score, "max": total_max}
    yield _event(source, event="scores", scores=scores)
