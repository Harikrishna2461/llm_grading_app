import os
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import ProcessRequest
from services.stream_merger import merged_stream

router = APIRouter()

GRADING_AGENT_URL = os.environ.get("GRADING_AGENT_URL", "http://localhost:8001")
REVIEW_AGENT_URL = os.environ.get("REVIEW_AGENT_URL", "http://localhost:8002")


@router.post("/process")
async def process_essay(request: ProcessRequest):
    grading_url = f"{GRADING_AGENT_URL}/grade"
    review_url = f"{REVIEW_AGENT_URL}/review"

    return StreamingResponse(
        merged_stream(grading_url, review_url, request.essay),
        media_type="application/x-ndjson",
    )
