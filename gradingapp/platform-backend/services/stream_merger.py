import asyncio
from typing import AsyncGenerator
from services.agent_client import stream_agent


async def merged_stream(
    grading_url: str,
    review_url: str,
    essay: str,
) -> AsyncGenerator[str, None]:
    """Fan out to both agents concurrently and yield merged NDJSON lines."""
    queue: asyncio.Queue = asyncio.Queue()

    # Launch both agent tasks concurrently
    task1 = asyncio.create_task(stream_agent(grading_url, essay, queue))
    task2 = asyncio.create_task(stream_agent(review_url, essay, queue))

    done_count = 0
    total_agents = 2

    try:
        while done_count < total_agents:
            item = await queue.get()
            if item is None:
                done_count += 1
            else:
                yield item
    finally:
        # Ensure tasks are cleaned up
        task1.cancel()
        task2.cancel()
        try:
            await asyncio.gather(task1, task2, return_exceptions=True)
        except Exception:
            pass
