from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import EssayRequest
from services.reviewer import stream_review

router = APIRouter()


@router.post("/review")
async def review_essay(request: EssayRequest):
    return StreamingResponse(
        stream_review(request.essay),
        media_type="application/x-ndjson",
    )
