import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import csv
from pathlib import Path

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


@app.get("/api/fairness")
def get_fairness_metrics():
    csv_path = Path(__file__).resolve().parents[1] / "outputs" / "fairness_by_group.csv"
    with csv_path.open(newline="", encoding="utf-8") as fairness_file:
        reader = csv.DictReader(fairness_file)
        return [
            {
                "state_group": row["state_group"],
                **{
                    metric: float(row[metric])
                    for metric in (
                        "accuracy",
                        "selection_rate",
                        "false_positive_rate",
                        "false_negative_rate",
                        "precision",
                        "recall",
                    )
                },
            }
            for row in reader
        ]


@app.get("/api/health")
def health():
    return {"status": "ok"}
