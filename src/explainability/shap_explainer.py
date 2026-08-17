"""SHAP-based explanations for individual predictions."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import joblib
import pandas as pd
import shap

from src.model.predict import prepare_applicant_record

ROOT_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT_DIR / "models" / "loan_default_model.joblib"


def explain_applicant(applicant: Dict[str, Any], model_path: Path = MODEL_PATH) -> Dict[str, Any]:
    """Return SHAP-based explanation data for a single applicant record."""
    model = joblib.load(model_path)
    prepared = prepare_applicant_record(applicant)

    if hasattr(model, "feature_names_in_"):
        expected = list(model.feature_names_in_)
        missing_columns = [col for col in expected if col not in prepared.columns]
        for col in missing_columns:
            prepared[col] = 0
        prepared = prepared[expected]

    explainer = shap.Explainer(model, prepared)
    shap_values = explainer(prepared)
    values = shap_values.values[0]
    feature_names = list(prepared.columns)

    explanation_rows = []
    for feature_name, feature_value, shap_value in zip(feature_names, prepared.iloc[0].tolist(), values):
        direction = "increasing_risk" if shap_value > 0 else "reducing_risk"
        explanation_rows.append(
            {
                "feature": feature_name,
                "feature_value": feature_value,
                "shap_value": float(shap_value),
                "direction": direction,
            }
        )

    increasing = sorted(
        [row for row in explanation_rows if row["direction"] == "increasing_risk"],
        key=lambda row: abs(row["shap_value"]),
        reverse=True,
    )[:5]
    decreasing = sorted(
        [row for row in explanation_rows if row["direction"] == "reducing_risk"],
        key=lambda row: abs(row["shap_value"]),
        reverse=True,
    )[:5]

    return {
        "prediction_input": prepared,
        "shap_values": explanation_rows,
        "top_increasing_risk": increasing,
        "top_reducing_risk": decreasing,
    }
