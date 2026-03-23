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

SYSTEM_PROMPT = """You are an expert essay editor and writing coach.
Review and refine the provided essay by producing exactly two XML-delimited sections in this order:
review, refined_essay.

Output format:
<section name="review">
Provide detailed editorial feedback covering:
- Writing style and clarity
- Structure and flow
- Argument coherence
- Vocabulary and tone
- Specific suggestions for improvement
</section>
<section name="refined_essay">
Provide the complete improved version of the essay incorporating your feedback.
Maintain the author's voice while enhancing quality.
</section>

Be constructive, specific, and thorough in your feedback."""

SECTION_ORDER = ["review", "refined_essay"]


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _event(source: str, **kwargs) -> str:
    return json.dumps({"source": source, "timestamp": _ts(), **kwargs}) + "\n"


async def stream_review(essay: str):
    source = "review_agent"
    yield _event(source, event="agent_start")

    current_section = None
    buffer = ""
    section_open_re = re.compile(r'<section name="([^"]+)">')
    section_close_re = re.compile(r"</section>")

    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Please review and refine the following essay:\n\n{essay}"}],
    ) as stream:
        async for text in stream.text_stream:
            buffer += text

            while buffer:
                if current_section is None:
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
                        if len(buffer) > 64:
                            buffer = buffer[-32:]
                        break
                else:
                    close_m = section_close_re.search(buffer)
                    if close_m:
                        chunk = buffer[: close_m.start()].strip()
                        if chunk:
                            yield _event(
                                source,
                                event="text_delta",
                                component=current_section,
                                text=chunk,
                            )
                        yield _event(source, event="section_end", component=current_section)
                        current_section = None
                        buffer = buffer[close_m.end():]
                    else:
                        safe_end = max(0, len(buffer) - 30)
                        if safe_end > 0:
                            chunk = buffer[:safe_end]
                            yield _event(
                                source,
                                event="text_delta",
                                component=current_section,
                                text=chunk,
                            )
                            buffer = buffer[safe_end:]
                        break

    yield _event(source, event="agent_done")
