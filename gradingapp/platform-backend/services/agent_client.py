import asyncio
import httpx


async def stream_agent(url: str, essay: str, queue: asyncio.Queue) -> None:
    """Stream NDJSON lines from an agent into the shared queue."""
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                url,
                json={"essay": essay},
                headers={"Content-Type": "application/json"},
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    line = line.strip()
                    if line:
                        await queue.put(line + "\n")
    except Exception as exc:
        import json
        from datetime import datetime, timezone

        source = url.split("/")[-2] if "/" in url else "unknown_agent"
        error_event = json.dumps({
            "source": source,
            "event": "error",
            "message": str(exc),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        await queue.put(error_event + "\n")
    finally:
        await queue.put(None)
