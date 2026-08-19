import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.assessment import router as assessment_router

app = FastAPI(title="Loan AI Assessment API", version="1.0.0")
cors_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,https://ai-loan-approval-assistant.in",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=os.getenv("CORS_ORIGIN_REGEX", r"https://.*\.vercel\.app"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(assessment_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
