"""Application service that delegates prediction and local SHAP to the existing pipeline."""

from datetime import datetime, timezone
from typing import Any

from src.explainability.shap_explainer import explain_applicant


DISPLAY_NAMES = {
    "loan_amnt": "Loan Amount", "term": "Loan Term", "int_rate": "Interest Rate",
    "installment": "Monthly Installment", "emp_length": "Employment Length",
    "home_ownership": "Home Ownership", "annual_inc": "Annual Income",
    "verification_status": "Verification Status", "issue_d": "Loan Issue Date",
    "purpose": "Loan Purpose", "dti": "Debt-to-Income Ratio",
    "delinq_2yrs": "Delinquencies (Last 2 Years)", "earliest_cr_line": "Earliest Credit Line",
    "fico_range_low": "FICO Score (Low)", "fico_range_high": "FICO Score (High)",
    "inq_last_6mths": "Credit Inquiries (Last 6 Months)",
    "mths_since_last_delinq": "Months Since Last Delinquency",
    "mths_since_last_record": "Months Since Last Public Record", "open_acc": "Open Credit Accounts",
    "pub_rec": "Public Records", "revol_bal": "Revolving Balance",
    "revol_util": "Revolving Credit Utilization", "total_acc": "Total Credit Accounts",
    "acc_now_delinq": "Current Delinquencies", "tot_coll_amt": "Total Collection Amount",
    "tot_cur_bal": "Total Current Balance", "mort_acc": "Mortgage Accounts",
    "pub_rec_bankruptcies": "Public Record Bankruptcies", "tax_liens": "Tax Liens",
    "initial_list_status": "Initial Listing Status", "application_type": "Application Type",
    "credit_history_years": "Credit History Length",
}

ONE_HOT_PREFIXES = {
    "home_ownership_": "home_ownership", "verification_status_": "verification_status",
    "purpose_": "purpose", "initial_list_status_": "initial_list_status",
    "application_type_": "application_type",
}

_HISTORY: list[dict[str, Any]] = []


def _display_value(factor: dict[str, Any], applicant: dict[str, Any]) -> tuple[str, Any]:
    feature = factor.get("feature", "")
    raw_feature = feature
    value = applicant.get(feature, factor.get("value"))
    for prefix, base_feature in ONE_HOT_PREFIXES.items():
        if feature.startswith(prefix):
            raw_feature = base_feature
            value = applicant.get(base_feature, feature[len(prefix):])
            break
    return DISPLAY_NAMES.get(raw_feature, factor.get("display_name", "Applicant factor")), value


def _message(label: str, value: Any, increases: bool) -> str:
    direction = "higher" if increases else "lower"
    return f"Your {label} of {value} is contributing to {direction} estimated default risk."


def _public_factor(factor: dict[str, Any], applicant: dict[str, Any]) -> dict[str, Any]:
    label, value = _display_value(factor, applicant)
    increases = float(factor.get("shap_value", 0)) > 0
    return {
        "feature": factor.get("feature", ""),
        "label": label,
        "value": value,
        "direction": "increases" if increases else "reduces",
        "message": _message(label, value, increases),
    }


def _public_result(result: dict[str, Any], name: str) -> dict[str, Any]:
    prediction = result["model_prediction"]
    decision = result["decision"]
    applicant = result.get("applicant") or {}
    explanation = result.get("explanation") or {}
    increasing = explanation.get("top_risk_factors") or []
    reducing = explanation.get("top_protective_factors") or []
    public = {
        "id": f"assessment-{len(_HISTORY) + 1}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "applicant": {"name": name},
        "prediction": {
            "class": prediction["label"],
            "default_probability": prediction["default_probability"],
            "default_probability_percent": prediction["default_probability_percent"],
            "non_default_probability": prediction["non_default_probability"],
            "non_default_probability_percent": prediction["non_default_probability_percent"],
        },
        "decision": {
            "risk_level": decision["risk_level"],
            "recommendation": decision["recommendation"],
        },
        "explanation": {
            "available": bool(increasing or reducing),
            "increasing_risk": [_public_factor(item, applicant) for item in increasing],
            "reducing_risk": [_public_factor(item, applicant) for item in reducing],
        },
    }
    return public


def assess(applicant_data: dict[str, Any], name: str) -> dict[str, Any]:
    result = explain_applicant(applicant_data)
    public = _public_result(result, name)
    _HISTORY.insert(0, public)
    return public


def applications() -> list[dict[str, Any]]:
    return list(_HISTORY)


def dashboard_stats() -> dict[str, int]:
    predictions = [item["prediction"]["class"] for item in _HISTORY]
    levels = [item["decision"]["risk_level"] for item in _HISTORY]
    return {
        "total_assessments": len(_HISTORY),
        "default_predictions": predictions.count("Default"),
        "non_default_predictions": predictions.count("Non-default"),
        "high_risk": levels.count("HIGH"),
        "medium_risk": levels.count("MEDIUM"),
        "low_risk": levels.count("LOW"),
    }
