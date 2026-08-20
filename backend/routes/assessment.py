import json
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from backend.services.credit_report import parse_credit_report
from backend.services.lender_config import LENDER_VALUES
from backend.services.prediction_service import assess, applications, dashboard_stats

router = APIRouter(prefix="/api")
MAX_REPORT_BYTES = 256 * 1024
LOGGER = logging.getLogger(__name__)


def _parse_report_text(text: str) -> dict[str, Any]:
    class TextUpload:
        name = "credit-report.txt"

        def getvalue(self):
            return text.encode("utf-8")

    return parse_credit_report(TextUpload())


def _merge_payload(payload: dict[str, Any], credit_report: dict[str, Any] | None = None) -> tuple[str, dict[str, Any]]:
    applicant = payload.get("applicant") or {}
    application = payload.get("application") or {}
    supplied_credit = payload.get("credit_report") or credit_report or {}
    name = str(applicant.get("full_name") or applicant.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="Full name is required.")
    merged = {
        **application,
        **supplied_credit,
        "emp_length": application.get("emp_length"),
        "home_ownership": application.get("home_ownership"),
        "loan_amnt": application.get("loan_amnt"),
        "term": application.get("term"),
        "annual_inc": application.get("annual_inc"),
        "purpose": application.get("purpose"),
        "dti": application.get("dti"),
        "application_type": application.get("application_type"),
        **LENDER_VALUES,
    }
    return name, merged


@router.post("/assessment")
async def create_assessment(request: Request):
    try:
        content_type = request.headers.get("content-type", "")
        credit_report = None
        if content_type.startswith("multipart/form-data"):
            form = await request.form()
            applicant = json.loads(str(form.get("applicant", "{}")))
            application = json.loads(str(form.get("application", "{}")))
            payload = {"applicant": applicant, "application": application}
            report = form.get("credit_report")
            if report is not None and hasattr(report, "read") and hasattr(report, "filename"):
                raw = await report.read(MAX_REPORT_BYTES + 1)
                if len(raw) > MAX_REPORT_BYTES:
                    raise HTTPException(status_code=413, detail="Credit report is too large.")
                if not report.filename or not report.filename.lower().endswith(".txt"):
                    raise HTTPException(status_code=422, detail="Credit report must be a .txt file.")
                credit_report = _parse_report_text(raw.decode("utf-8", errors="replace"))
        else:
            payload = await request.json()
        name, applicant_data = _merge_payload(payload, credit_report)
        return assess(applicant_data, name)
    except HTTPException:
        raise
    except (ValueError, TypeError, KeyError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        LOGGER.exception("Assessment request failed during ML processing.")
        raise HTTPException(status_code=500, detail="Unable to complete the assessment.") from error


@router.get("/applications")
def get_applications():
    return applications()


@router.get("/dashboard")
def get_dashboard():
    return dashboard_stats()
