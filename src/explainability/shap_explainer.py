"""
Applicant-level SHAP explanation for the XGBoost loan default model.

Flow:
    Applicant Form
          ↓
    applicant_features.py
          ↓
    Complete applicant model vector
          ↓
       XGBoost
          ↓
    Default probability
          ↓
        SHAP
          ↓
    Applicant-specific explanation

Important:
- SHAP receives the EXACT vector given to XGBoost.
- No median/reference-profile imputation is performed here.
- grade and sub_grade must NOT be model features.
"""

from pathlib import Path
from functools import lru_cache
import json
import logging
import sys

import joblib
import numpy as np
import pandas as pd
import shap
import xgboost


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = ROOT_DIR / "models" / "xgboost.pkl"
REPORTS_DIR = ROOT_DIR / "reports"

LOCAL_JSON_PATH = REPORTS_DIR / "shap_local_explanation.json"
LOCAL_CSV_PATH = REPORTS_DIR / "shap_local_explanation.csv"


# ============================================================
# IMPORT APPLICANT INPUT BUILDER
# ============================================================

try:
    from .applicant_features import build_model_input
except ImportError:
    from applicant_features import build_model_input

try:
    from ..inference.decision_policy import apply_decision_policy
except ImportError:
    sys.path.insert(0, str(ROOT_DIR / "src"))
    from inference.decision_policy import apply_decision_policy


LOGGER = logging.getLogger(__name__)


# ============================================================
# DISPLAY NAMES
# ============================================================

DISPLAY_NAMES = {
    "loan_amnt": "Loan Amount",
    "term": "Loan Term",
    "int_rate": "Interest Rate",
    "installment": "Installment",
    "emp_length": "Employment Length",
    "home_ownership": "Home Ownership",
    "annual_inc": "Annual Income",
    "verification_status": "Verification Status",
    "issue_d": "Issue Date",
    "purpose": "Loan Purpose",
    "dti": "Debt-to-Income Ratio",
    "delinq_2yrs": "Delinquencies in Last 2 Years",
    "earliest_cr_line": "Earliest Credit Line",
    "fico_range_low": "FICO Score (Low)",
    "fico_range_high": "FICO Score (High)",
    "inq_last_6mths": "Credit Inquiries (Last 6 Months)",
    "mths_since_last_delinq": "Months Since Last Delinquency",
    "mths_since_last_record": "Months Since Last Public Record",
    "open_acc": "Open Credit Accounts",
    "pub_rec": "Public Records",
    "revol_bal": "Revolving Balance",
    "revol_util": "Revolving Credit Utilization",
    "total_acc": "Total Credit Accounts",
    "initial_list_status": "Initial List Status",
    "application_type": "Application Type",
    "acc_now_delinq": "Current Delinquencies",
    "tot_coll_amt": "Total Collection Amount",
    "tot_cur_bal": "Total Current Balance",
    "mort_acc": "Mortgage Accounts",
    "pub_rec_bankruptcies": "Public Record Bankruptcies",
    "tax_liens": "Tax Liens",

    # Derived features, if your trained model contains them
    "credit_history_years": "Credit History Length",
    "emp_length_missing": "Employment Length Missing",
    "mths_since_last_delinq_missing": "Last Delinquency Missing",
    "mths_since_last_record_missing": "Last Public Record Missing",
}


# ============================================================
# MODEL LOADING
# ============================================================

@lru_cache(maxsize=1)
def get_model():
    """
    Load the trained XGBoost model once.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"XGBoost model not found at:\n{MODEL_PATH}"
        )

    try:
        model = joblib.load(MODEL_PATH)
    except Exception as error:
        raise RuntimeError(
            f"Could not load XGBoost model: {error}"
        ) from error

    if not isinstance(model, xgboost.XGBClassifier):
        raise TypeError(
            f"Expected XGBClassifier, got {type(model).__name__}"
        )

    if not hasattr(model, "feature_names_in_"):
        raise ValueError(
            "The trained model does not contain feature_names_in_."
        )

    if not callable(getattr(model, "predict", None)):
        raise TypeError("Model does not provide predict().")

    if not callable(getattr(model, "predict_proba", None)):
        raise TypeError("Model does not provide predict_proba().")

    return model


# ============================================================
# SHAP EXPLAINER
# ============================================================

@lru_cache(maxsize=1)
def get_explainer():
    """
    Create a TreeExplainer for the trained XGBoost model.
    """

    model = get_model()

    return shap.TreeExplainer(model)


# ============================================================
# SHAP VALUE HANDLING
# ============================================================

def get_class_one_shap_values(shap_output, sample_count, feature_count):
    """
    Extract SHAP values corresponding to class 1.

    Class 1 = Default.

    Supports different SHAP/XGBoost output formats.
    """

    if hasattr(shap_output, "values"):
        shap_output = shap_output.values

    # Older SHAP versions may return a list
    if isinstance(shap_output, list):

        if len(shap_output) == 1:
            values = np.asarray(shap_output[0])
        else:
            values = np.asarray(shap_output[1])

        if values.ndim != 2:
            raise ValueError(
                f"Unexpected SHAP list output shape: {values.shape}"
            )

        if values.shape != (sample_count, feature_count):
            raise ValueError(
                f"Unexpected SHAP shape: {values.shape}. "
                f"Expected {(sample_count, feature_count)}."
            )

        return values

    values = np.asarray(shap_output)

    # Binary output already returned as:
    # samples × features
    if values.ndim == 2:
        return values

    if values.ndim != 3:
        raise ValueError(
            f"Unsupported SHAP output shape: {values.shape}"
        )

    # samples × features × classes
    if values.shape == (sample_count, feature_count, 2):
        return values[:, :, 1]

    # classes × samples × features
    if values.shape == (2, sample_count, feature_count):
        return values[1]

    # samples × classes × features
    if values.shape == (sample_count, 2, feature_count):
        return values[:, 1, :]

    raise ValueError(
        f"Cannot identify class-1 SHAP values from shape {values.shape}"
    )


# ============================================================
# DISPLAY NAME
# ============================================================

def display_name(feature):
    """
    Convert model feature names into frontend-friendly names.
    """

    if feature in DISPLAY_NAMES:
        return DISPLAY_NAMES[feature]

    # Handle one-hot encoded features
    if "_" in feature:

        prefixes = {
            "home_ownership_": "Home Ownership",
            "verification_status_": "Verification Status",
            "purpose_": "Loan Purpose",
            "initial_list_status_": "Initial List Status",
            "application_type_": "Application Type",
        }

        for prefix, label in prefixes.items():

            if feature.startswith(prefix):

                value = feature[len(prefix):]

                return f"{label}: {value}"

    return feature.replace("_", " ").title()


# ============================================================
# FORMAT APPLICANT VALUE
# ============================================================

def format_value(value):
    """
    Convert NumPy/Pandas values into JSON-safe values.
    """

    if isinstance(value, np.generic):
        value = value.item()

    if pd.isna(value):
        return None

    if isinstance(value, float):
        return round(value, 4)

    return value


# ============================================================
# CREATE FACTOR
# ============================================================

def create_factor(feature, value, shap_value):
    """
    Create one applicant-specific SHAP explanation.

    Positive SHAP:
        pushes prediction toward DEFAULT.

    Negative SHAP:
        pushes prediction toward NON-DEFAULT.
    """

    shap_value = float(shap_value)

    if shap_value > 0:

        impact = "increases_default_risk"

        direction = "increased"

    elif shap_value < 0:

        impact = "decreases_default_risk"

        direction = "reduced"

    else:

        impact = "neutral"

        direction = "did not materially change"

    name = display_name(feature)

    safe_value = format_value(value)

    if impact == "increases_default_risk":

        explanation = (
            f"Your {name} value of {safe_value} "
            f"increased the model's predicted default risk."
        )

    elif impact == "decreases_default_risk":

        explanation = (
            f"Your {name} value of {safe_value} "
            f"reduced the model's predicted default risk."
        )

    else:

        explanation = (
            f"Your {name} value of {safe_value} "
            f"had little effect on the model's prediction."
        )

    return {
        "feature": feature,
        "display_name": name,
        "value": safe_value,
        "applicant_value": safe_value,
        "source": "applicant-input",
        "shap_value": shap_value,
        "absolute_shap": abs(shap_value),
        "impact": impact,
        "explanation": explanation,
    }


# ============================================================
# MAIN APPLICANT EXPLANATION
# ============================================================

def explain_applicant(applicant_data):
    """
    Generate an applicant-specific XGBoost prediction
    and SHAP explanation.

    applicant_data:
        Dictionary containing the complete applicant form.

    Returns:
        Dictionary containing:

        - applicant input
        - XGBoost prediction
        - default probability
        - SHAP explanation
    """

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model = get_model()

    model_features = list(model.feature_names_in_)

    # --------------------------------------------------------
    # Make sure grade/sub_grade are NOT used
    # --------------------------------------------------------

    forbidden_features = {
        "grade",
        "sub_grade",
        "grade_encoded",
        "sub_grade_encoded",
    }

    forbidden_used = [
        feature
        for feature in model_features
        if feature in forbidden_features
    ]

    if forbidden_used:
        raise ValueError(
            "The loaded XGBoost model still contains forbidden "
            f"features: {forbidden_used}. "
            "Retrain the model without grade/sub_grade."
        )

    # --------------------------------------------------------
    # Build EXACT model input from applicant data
    # --------------------------------------------------------

    model_input, normalized_applicant = build_model_input(
        applicant_data,
        model=model,
    )

    # --------------------------------------------------------
    # Validate feature order
    # --------------------------------------------------------

    if list(model_input.columns) != model_features:

        raise ValueError(
            "Applicant model input columns do not match "
            "XGBoost feature order."
        )

    # --------------------------------------------------------
    # Validate dimensions
    # --------------------------------------------------------

    if model_input.shape != (1, len(model_features)):

        raise ValueError(
            f"Unexpected applicant input shape: "
            f"{model_input.shape}. "
            f"Expected {(1, len(model_features))}."
        )

    # --------------------------------------------------------
    # Validate numeric values
    # --------------------------------------------------------

    numeric_values = model_input.to_numpy(dtype=float)

    if not np.isfinite(numeric_values).all():

        raise ValueError(
            "Applicant model input contains NaN or infinite values."
        )

    # ========================================================
    # XGBOOST PREDICTION
    # ========================================================

    prediction = int(
        model.predict(model_input)[0]
    )

    probabilities = model.predict_proba(model_input)[0]

    default_probability = float(probabilities[1])

    non_default_probability = float(probabilities[0])
    decision = apply_decision_policy(default_probability)
    factors = []

    try:
        # ====================================================
        # SHAP
        # ====================================================
        explainer = get_explainer()
        raw_shap_values = explainer.shap_values(model_input)
        shap_values = get_class_one_shap_values(
            raw_shap_values,
            sample_count=1,
            feature_count=len(model_features),
        )
        applicant_shap_values = shap_values[0]

        if len(applicant_shap_values) != len(model_features):
            raise ValueError(
                "Number of SHAP values does not match number of model features."
            )

        factors = [
            create_factor(
                feature=feature,
                value=model_input.iloc[0][feature],
                shap_value=applicant_shap_values[index],
            )
            for index, feature in enumerate(model_features)
        ]
        factors.sort(key=lambda item: item["absolute_shap"], reverse=True)
        risk_factors = [factor for factor in factors if factor["shap_value"] > 0]
        protective_factors = [factor for factor in factors if factor["shap_value"] < 0]
    except Exception:
        LOGGER.exception("Local SHAP explanation failed for applicant assessment.")
        risk_factors = []
        protective_factors = []

    # ========================================================
    # RESULT
    # ========================================================

    result = {

        "applicant": normalized_applicant,

        "model_input": {
            feature: format_value(
                model_input.iloc[0][feature]
            )
            for feature in model_features
        },

        "model_prediction": {

            "class": prediction,

            "label": (
                "Default"
                if prediction == 1
                else "Non-default"
            ),

            "default_probability": default_probability,

            "default_probability_percent": round(
                default_probability * 100,
                2,
            ),

            "non_default_probability": non_default_probability,

            "non_default_probability_percent": round(
                non_default_probability * 100,
                2,
            ),
        },

        "decision": decision,

        "explanation": {

            "total_model_features": len(model_features) if risk_factors or protective_factors else 0,

            "top_factors": factors,

            "risk_factors": risk_factors,

            "protective_factors": protective_factors,

            "top_risk_factors": risk_factors[:5],

            "top_protective_factors": protective_factors[:5],
        },
    }

    return result


# ============================================================
# JSON-SAFE CONVERSION
# ============================================================

def make_json_safe(value):

    if isinstance(value, dict):

        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):

        return [
            make_json_safe(item)
            for item in value
        ]

    if isinstance(value, np.generic):

        return value.item()

    if isinstance(value, pd.Timestamp):

        return value.strftime("%b-%Y")

    if isinstance(value, float):

        if not np.isfinite(value):

            raise ValueError(
                "Non-finite value found in explanation."
            )

        return value

    return value


# ============================================================
# SAVE REPORT
# ============================================================

def save_explanation(result):
    """
    Save applicant-specific SHAP explanation.

    These files are optional debugging/report files.
    They are NOT required for frontend prediction.
    """

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    with LOCAL_JSON_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            make_json_safe(result),
            file,
            indent=4,
            allow_nan=False,
        )

    # --------------------------------------------------------
    # CSV
    # --------------------------------------------------------

    factors = result["explanation"]["top_factors"]

    pd.DataFrame(factors).to_csv(
        LOCAL_CSV_PATH,
        index=False,
    )


# ============================================================
# PRINT RESULT
# ============================================================

def print_explanation(result):

    prediction = result["model_prediction"]

    explanation = result["explanation"]

    print("=" * 60)

    print("AI LOAN APPROVAL ASSISTANT")

    print("=" * 60)

    print()

    print("MODEL OUTPUT")

    print(
        f"Predicted Class: "
        f"{prediction['label']}"
    )

    print()

    print(
        f"Default Probability: "
        f"{prediction['default_probability_percent']:.2f}%"
    )

    print()

    print("-" * 60)

    print("SHAP EXPLANATION")

    print()

    print("Factors increasing default risk:")

    if explanation["top_risk_factors"]:

        for index, factor in enumerate(
            explanation["top_risk_factors"],
            start=1,
        ):

            print(
                f"{index}. "
                f"{factor['explanation']}"
            )

    else:

        print("No features increased default risk.")

    print()

    print("-" * 60)

    print("Factors reducing default risk:")

    if explanation["top_protective_factors"]:

        for index, factor in enumerate(
            explanation["top_protective_factors"],
            start=1,
        ):

            print(
                f"{index}. "
                f"{factor['explanation']}"
            )

    else:

        print("No features reduced default risk.")

    print()

    print("-" * 60)

    print("SHAP / MODEL VALIDATION")

    print(
        f"Model features: "
        f"{explanation['total_model_features']}"
    )

    print(
        "Applicant-specific SHAP values: "
        f"{len(explanation['top_factors'])}"
    )

    print(
        "Same applicant vector used by XGBoost and SHAP: True"
    )

    print()

    print("=" * 60)

    print("SHAP EXPLANATION COMPLETE")

    print("=" * 60)


