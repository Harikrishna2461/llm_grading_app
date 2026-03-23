from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import EssayRequest
from services.grader import stream_grading

router = APIRouter()


@router.post("/grade")
async def grade_essay(request: EssayRequest):
    return StreamingResponse(
        stream_grading(request.essay),
        media_type="application/x-ndjson",
    )
