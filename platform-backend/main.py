import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers.process import router as process_router

load_dotenv()

app = FastAPI(title="Platform Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(process_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "platform-backend"}
