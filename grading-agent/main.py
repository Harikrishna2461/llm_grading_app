from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers.grade import router as grade_router

load_dotenv()

app = FastAPI(title="Grading Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(grade_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "grading-agent"}
