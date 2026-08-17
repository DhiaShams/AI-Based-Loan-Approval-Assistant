"""Prediction utilities for a single applicant record."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import joblib
import pandas as pd

from src.model.decision import decide_default_risk

ROOT_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT_DIR / "models" / "loan_default_model.joblib"

REQUIRED_FEATURES = [
    "loan_amnt",
    "annual_inc",
    "dti",
    "fico_range_low",
    "revol_util",
]


def validate_required_features(applicant: Dict[str, Any]) -> None:
    missing = [feature for feature in REQUIRED_FEATURES if feature not in applicant]
    if missing:
        raise ValueError(
            "Missing required applicant features: " + ", ".join(missing)
        )


def _as_float(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return float(default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _as_int(value: Any, default: int = 0) -> int:
    if value is None or value == "":
        return int(default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _normalize_emp_length(value: Any) -> int:
    if value is None or value == "":
        return 0
    if isinstance(value, str):
        cleaned = value.strip().lower().replace("years", "").replace("year", "").strip()
        if "<" in cleaned:
            return 0
        try:
            return int(float(cleaned))
        except ValueError:
            return 0
    return int(value)


def _safe_date(value: Any) -> pd.Timestamp | pd.NaT:
    if value is None or value == "":
        return pd.NaT
    try:
        return pd.to_datetime(value, errors="coerce")
    except Exception:
        return pd.NaT


def prepare_applicant_record(applicant: Dict[str, Any]) -> pd.DataFrame:
    """Create a single-row DataFrame aligned to the cleaned loan dataset features.

    This function is intentionally lightweight and intentionally mirrors the
    feature engineering rules from the existing cleaning script without
    requiring the full Kaggle CSV to be present.
    """
    record = dict(applicant)
    record.setdefault("loan_amnt", 15000)
    record.setdefault("term", 36)
    record.setdefault("int_rate", 8.5)
    record.setdefault("installment", 500.0)
    record.setdefault("annual_inc", 60000)
    record.setdefault("dti", 15.0)
    record.setdefault("fico_range_low", 700)
    record.setdefault("fico_range_high", 704)
    record.setdefault("revol_util", 35.0)
    record.setdefault("emp_length", 3)
    record.setdefault("home_ownership", "MORTGAGE")
    record.setdefault("verification_status", "Verified")
    record.setdefault("purpose", "debt_consolidation")
    record.setdefault("grade", "B")
    record.setdefault("sub_grade", "B1")
    record.setdefault("issue_d", "2020-01-01")
    record.setdefault("earliest_cr_line", "2015-01-01")
    record.setdefault("delinq_2yrs", 0)
    record.setdefault("inq_last_6mths", 0)
    record.setdefault("mths_since_last_delinq", -1)
    record.setdefault("mths_since_last_record", -1)
    record.setdefault("open_acc", 8)
    record.setdefault("pub_rec", 0)
    record.setdefault("revol_bal", 20000)
    record.setdefault("total_acc", 20)
    record.setdefault("initial_list_status", "f")
    record.setdefault("application_type", "INDIVIDUAL")
    record.setdefault("acc_now_delinq", 0)
    record.setdefault("tot_coll_amt", 0)
    record.setdefault("tot_cur_bal", 50000)
    record.setdefault("mort_acc", 1)
    record.setdefault("pub_rec_bankruptcies", 0)
    record.setdefault("tax_liens", 0)

    df = pd.DataFrame([record])
    df["loan_amnt"] = df["loan_amnt"].apply(_as_float)
    df["term"] = df["term"].apply(_as_float)
    df["int_rate"] = df["int_rate"].apply(_as_float)
    df["installment"] = df["installment"].apply(_as_float)
    df["annual_inc"] = df["annual_inc"].apply(_as_float)
    df["dti"] = df["dti"].apply(_as_float)
    df["fico_range_low"] = df["fico_range_low"].apply(_as_float)
    df["fico_range_high"] = df["fico_range_high"].apply(_as_float)
    df["revol_util"] = df["revol_util"].apply(_as_float)
    df["emp_length"] = df["emp_length"].apply(_normalize_emp_length)
    df["issue_d"] = df["issue_d"].apply(_safe_date)
    df["earliest_cr_line"] = df["earliest_cr_line"].apply(_safe_date)

    df["credit_history_years"] = (
        (df["issue_d"] - df["earliest_cr_line"]).dt.days / 365.25
    )
    df["credit_history_years"] = df["credit_history_years"].fillna(0)

    grade_levels = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6}
    df["grade_encoded"] = df["grade"].map(grade_levels).fillna(1)
    df["sub_grade_encoded"] = df["sub_grade"].apply(
        lambda s: (
            (grade_levels.get(str(s)[0], 1) * 5) + int(str(s)[1])
            if isinstance(s, str) and len(str(s)) > 1 and str(s)[1].isdigit()
            else 1
        )
    )

    for col in [
        "mths_since_last_delinq",
        "mths_since_last_record",
        "delinq_2yrs",
        "inq_last_6mths",
        "open_acc",
        "pub_rec",
        "revol_bal",
        "total_acc",
        "acc_now_delinq",
        "tot_coll_amt",
        "tot_cur_bal",
        "mort_acc",
        "pub_rec_bankruptcies",
        "tax_liens",
    ]:
        df[col] = df[col].apply(_as_float)

    cat_cols = [
        "home_ownership",
        "verification_status",
        "purpose",
        "initial_list_status",
        "application_type",
    ]
    for col in cat_cols:
        if col not in df.columns:
            df[col] = "Unknown"
        df[col] = df[col].fillna("Unknown").astype(str)

    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    for col in ["grade", "sub_grade", "issue_d", "earliest_cr_line"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    return df


def predict_applicant(
    applicant: Dict[str, Any],
    model: Optional[Any] = None,
    model_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Predict default probability for a single applicant and convert it to risk."""
    validate_required_features(applicant)

    if model is None:
        model = joblib.load(model_path or MODEL_PATH)

    prepared = prepare_applicant_record(applicant)

    if hasattr(model, "feature_names_in_"):
        expected = list(model.feature_names_in_)
        missing_columns = [col for col in expected if col not in prepared.columns]
        for col in missing_columns:
            prepared[col] = 0
        prepared = prepared[expected]

    probability = float(model.predict_proba(prepared)[0, 1])
    decision = decide_default_risk(probability)
    decision["default_probability"] = probability
    return decision
