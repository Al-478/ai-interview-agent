from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import config
from app.api.interview import router as interview_router

app = FastAPI(title="AI Interview Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-interview-agent"}
