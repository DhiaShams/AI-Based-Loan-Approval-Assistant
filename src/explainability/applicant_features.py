"""
Applicant input validation and XGBoost model-vector construction.

Purpose
-------
This module converts the values entered by an applicant into the exact
feature vector expected by the trained XGBoost model.

Flow
----
Frontend
    ↓
Applicant data
    ↓
validate_applicant_fields()
    ↓
_normalize_applicant()
    ↓
build_model_input()
    ↓
Complete XGBoost feature vector
    ↓
XGBoost prediction + SHAP explanation

Important
---------
This module does NOT:
- load a reference/median applicant
- perform median imputation
- make predictions
- calculate SHAP values
- generate reports

The vector returned by build_model_input() must be passed unchanged
to both XGBoost and SHAP.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = ROOT_DIR / "models" / "xgboost.pkl"


# ============================================================
# MODEL / INPUT DEFINITIONS
# ============================================================

# These are fields that must NEVER be supplied by the applicant
# because they represent outcomes, post-loan information, or IDs.
LEAKAGE_COLUMNS = {
    "id",
    "loan_status",
    "default_flag",
    "actual_default",
    "predicted_default",
    "default_probability",
    "recoveries",
    "collection_recovery_fee",
    "out_prncp",
    "out_prncp_inv",
    "total_pymnt",
    "total_pymnt_inv",
    "total_rec_prncp",
    "total_rec_int",
    "total_rec_late_fee",
    "last_pymnt_d",
    "last_pymnt_amnt",
    "next_pymnt_d",
    "last_credit_pull_d",
    "last_fico_range_high",
    "last_fico_range_low",
}


# grade and sub_grade are deliberately excluded from the new model.
FORBIDDEN_MODEL_FEATURES = {
    "grade",
    "sub_grade",
    "grade_encoded",
    "sub_grade_encoded",
}


# Frontend identity fields are stored with an assessment but are never model features.
FRONTEND_ONLY_FIELDS = {"full_name", "age"}


# ============================================================
# APPLICANT INPUT FIELDS
# ============================================================

# These are the actual application-time fields that the frontend
# can collect from the user.

APPLICANT_FEATURES = [
    "loan_amnt",
    "term",
    "int_rate",
    "installment",
    "emp_length",
    "home_ownership",
    "annual_inc",
    "verification_status",
    "issue_d",
    "purpose",
    "dti",
    "delinq_2yrs",
    "earliest_cr_line",
    "fico_range_low",
    "fico_range_high",
    "inq_last_6mths",
    "mths_since_last_delinq",
    "mths_since_last_record",
    "open_acc",
    "pub_rec",
    "revol_bal",
    "revol_util",
    "total_acc",
    "initial_list_status",
    "application_type",
    "acc_now_delinq",
    "tot_coll_amt",
    "tot_cur_bal",
    "mort_acc",
    "pub_rec_bankruptcies",
    "tax_liens",
]


# ============================================================
# FIELD TYPES
# ============================================================

CATEGORICAL_FIELDS = {
    "home_ownership",
    "verification_status",
    "purpose",
    "initial_list_status",
    "application_type",
}


DATE_FIELDS = {
    "issue_d",
    "earliest_cr_line",
}


# These fields are allowed to be unavailable in the application.
OPTIONAL_FIELDS = {
    "emp_length",
    "mths_since_last_delinq",
    "mths_since_last_record",
}


# ============================================================
# APPLICANT FIELD METADATA
# ============================================================

APPLICANT_FEATURE_METADATA = {
    feature: {
        "display_name": feature.replace("_", " ").title(),
        "type": (
            "select"
            if feature in CATEGORICAL_FIELDS
            else "date"
            if feature in DATE_FIELDS
            else "number"
        ),
        "description": (
            f"Application-time value for "
            f"{feature.replace('_', ' ')}."
        ),
        "required": feature not in OPTIONAL_FIELDS,
        "example": None,
        "numeric": (
            feature not in CATEGORICAL_FIELDS
            and feature not in DATE_FIELDS
        ),
    }
    for feature in APPLICANT_FEATURES
}


# More useful examples for frontend/schema generation.
APPLICANT_FEATURE_METADATA.update(
    {
        "loan_amnt": {
            **APPLICANT_FEATURE_METADATA["loan_amnt"],
            "display_name": "Loan Amount",
            "description": "Amount of loan requested.",
            "example": 15000,
        },
        "term": {
            **APPLICANT_FEATURE_METADATA["term"],
            "display_name": "Loan Term",
            "description": "Repayment term in months.",
            "example": 36,
        },
        "int_rate": {
            **APPLICANT_FEATURE_METADATA["int_rate"],
            "display_name": "Interest Rate",
            "description": "Annual interest rate as a percentage.",
            "example": 12.5,
        },
        "installment": {
            **APPLICANT_FEATURE_METADATA["installment"],
            "display_name": "Installment",
            "description": "Monthly loan installment.",
            "example": 500,
        },
        "emp_length": {
            **APPLICANT_FEATURE_METADATA["emp_length"],
            "display_name": "Employment Length",
            "description": "Years employed with current employer.",
            "example": 5,
        },
        "home_ownership": {
            **APPLICANT_FEATURE_METADATA["home_ownership"],
            "display_name": "Home Ownership",
            "description": "Applicant home ownership category.",
            "example": "RENT",
        },
        "annual_inc": {
            **APPLICANT_FEATURE_METADATA["annual_inc"],
            "display_name": "Annual Income",
            "description": "Gross annual income.",
            "example": 60000,
        },
        "verification_status": {
            **APPLICANT_FEATURE_METADATA["verification_status"],
            "display_name": "Verification Status",
            "description": "Income verification status.",
            "example": "Verified",
        },
        "issue_d": {
            **APPLICANT_FEATURE_METADATA["issue_d"],
            "display_name": "Loan Issue Date",
            "description": "Date on which the loan was issued.",
            "example": "Dec-2015",
        },
        "purpose": {
            **APPLICANT_FEATURE_METADATA["purpose"],
            "display_name": "Loan Purpose",
            "description": "Purpose for which the loan is requested.",
            "example": "debt_consolidation",
        },
        "dti": {
            **APPLICANT_FEATURE_METADATA["dti"],
            "display_name": "Debt-to-Income Ratio",
            "description": "Debt-to-income ratio.",
            "example": 20,
        },
        "fico_range_low": {
            **APPLICANT_FEATURE_METADATA["fico_range_low"],
            "display_name": "FICO Score - Low",
            "description": "Lower bound of FICO score.",
            "example": 700,
        },
        "fico_range_high": {
            **APPLICANT_FEATURE_METADATA["fico_range_high"],
            "display_name": "FICO Score - High",
            "description": "Upper bound of FICO score.",
            "example": 704,
        },
        "earliest_cr_line": {
            **APPLICANT_FEATURE_METADATA["earliest_cr_line"],
            "display_name": "Earliest Credit Line",
            "description": "Date of earliest reported credit line.",
            "example": "Jan-2000",
        },
    }
)


# ============================================================
# VALUE MAPPINGS
# ============================================================

EMP_LENGTH_MAP = {
    "< 1 year": 0,
    "1 year": 1,
    "2 years": 2,
    "3 years": 3,
    "4 years": 4,
    "5 years": 5,
    "6 years": 6,
    "7 years": 7,
    "8 years": 8,
    "9 years": 9,
    "10+ years": 10,
}


ALLOWED_CATEGORIES = {
    "home_ownership": {
        "RENT",
        "MORTGAGE",
        "OWN",
        "NONE",
        "OTHER",
    },
    "verification_status": {
        "Not Verified",
        "Source Verified",
        "Verified",
    },
    "purpose": {
        "credit_card",
        "debt_consolidation",
        "educational",
        "home_improvement",
        "house",
        "major_purchase",
        "medical",
        "moving",
        "other",
        "renewable_energy",
        "small_business",
        "vacation",
        "wedding",
    },
    "initial_list_status": {
        "f",
        "w",
    },
    "application_type": {
        "Individual",
        "Joint App",
    },
}


# ============================================================
# VALIDATION
# ============================================================

def validate_applicant_fields(applicant_data):
    """
    Validate the applicant dictionary.

    Ensures:
    - input is a dictionary
    - no leakage fields are supplied
    - no unsupported fields are supplied
    - required fields are present
    - categorical values are valid
    """

    if not isinstance(applicant_data, dict):
        raise TypeError(
            "applicant_data must be a dictionary."
        )

    # Check leakage fields.
    forbidden = sorted(
        set(applicant_data) & LEAKAGE_COLUMNS
    )

    if forbidden:
        raise ValueError(
            "Leakage/post-outcome fields cannot be "
            f"used as applicant inputs: {forbidden}"
        )

    # Check unsupported fields.
    unknown = sorted(
        set(applicant_data) - set(APPLICANT_FEATURES)
    )

    if unknown:
        raise ValueError(
            f"Unsupported applicant fields: {unknown}"
        )

    # Check required fields.
    missing = [
        feature
        for feature in APPLICANT_FEATURES
        if (
            APPLICANT_FEATURE_METADATA[feature]["required"]
            and feature not in applicant_data
        )
    ]

    if missing:
        raise ValueError(
            "Applicant input is missing required fields: "
            f"{missing}"
        )

    # Check categorical values.
    for feature, allowed_values in ALLOWED_CATEGORIES.items():

        if feature not in applicant_data:
            continue

        value = applicant_data[feature]

        if value not in allowed_values:
            raise ValueError(
                f"Unsupported {feature} value: {value}. "
                f"Allowed values: {sorted(allowed_values)}"
            )


# ============================================================
# NUMERIC NORMALIZATION
# ============================================================

def _number(feature, value):
    """
    Convert an applicant value to a finite float.
    """

    try:
        result = float(value)

    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Applicant field '{feature}' must be numeric. "
            f"Received: {value}"
        ) from error

    if not np.isfinite(result):
        raise ValueError(
            f"Applicant field '{feature}' must be finite."
        )

    return result


# ============================================================
# DATE NORMALIZATION
# ============================================================

def _date(feature, value):
    """
    Convert an applicant date into pandas Timestamp.

    Expected examples:
        Dec-2015
        Jan-2000
    """

    parsed = pd.to_datetime(
        value,
        format="%b-%Y",
        errors="coerce",
    )

    if pd.isna(parsed):

        parsed = pd.to_datetime(
            value,
            errors="coerce",
        )

    if pd.isna(parsed):
        raise ValueError(
            f"Applicant field '{feature}' must be a valid "
            f"date such as 'Dec-2015'."
        )

    return parsed


# ============================================================
# APPLICANT NORMALIZATION
# ============================================================

def _normalize_applicant(applicant_data):
    """
    Normalize raw frontend values.

    This function does NOT use dataset medians.
    """

    normalized = dict(applicant_data)

    # Optional fields are explicitly represented as None.
    for feature in OPTIONAL_FIELDS:
        normalized.setdefault(feature, None)

    # -------------------------
    # Term
    # -------------------------

    term = normalized["term"]

    if isinstance(term, str):
        term = term.strip().split()[0]

    normalized["term"] = _number(
        "term",
        term,
    )

    # -------------------------
    # Employment length
    # -------------------------

    emp_length = normalized["emp_length"]

    if isinstance(emp_length, str):

        if emp_length not in EMP_LENGTH_MAP:
            raise ValueError(
                "Unsupported emp_length value: "
                f"{emp_length}"
            )

        normalized["emp_length"] = EMP_LENGTH_MAP[
            emp_length
        ]

    elif emp_length is not None:

        normalized["emp_length"] = _number(
            "emp_length",
            emp_length,
        )

    # -------------------------
    # Numeric fields
    # -------------------------

    for feature, metadata in APPLICANT_FEATURE_METADATA.items():

        if not metadata["numeric"]:
            continue

        if feature in {
            "term",
            "emp_length",
        }:
            continue

        value = normalized.get(feature)

        if value is not None:
            normalized[feature] = _number(
                feature,
                value,
            )

    # -------------------------
    # Dates
    # -------------------------

    normalized["issue_d"] = _date(
        "issue_d",
        normalized["issue_d"],
    )

    normalized["earliest_cr_line"] = _date(
        "earliest_cr_line",
        normalized["earliest_cr_line"],
    )

    return normalized


# ============================================================
# MODEL FEATURE VALIDATION
# ============================================================

def _model_features(model):
    """
    Read the exact feature order expected by XGBoost.

    The model must have been trained without grade/sub_grade.
    """

    if not hasattr(model, "feature_names_in_"):
        raise ValueError(
            "Loaded XGBoost model does not expose "
            "feature_names_in_."
        )

    features = list(
        model.feature_names_in_
    )

    if not features:
        raise ValueError(
            "The loaded model has no feature names."
        )

    # Ensure grade/sub_grade are not present.
    forbidden = sorted(
        set(features) & FORBIDDEN_MODEL_FEATURES
    )

    # Also catch names such as grade_encoded.
    grade_related = [
        feature
        for feature in features
        if "grade" in feature.lower()
    ]

    if grade_related:
        raise ValueError(
            "The loaded XGBoost model still contains "
            "grade/sub_grade-related features: "
            f"{grade_related}. "
            "Retrain the model without these features."
        )

    return features


# ============================================================
# MODEL INPUT CONSTRUCTION
# ============================================================

def build_model_input(applicant_data, model=None):
    """
    Construct the complete applicant-specific XGBoost vector.

    Returns
    -------
    result : pandas.DataFrame
        One-row DataFrame in EXACT model feature order.

    normalized : dict
        Normalized applicant values.

    Important
    ---------
    No median/reference profile is used.

    Every model feature must come from:
        1. applicant input
        2. categorical encoding
        3. explicitly derived feature
        4. training-consistent missing-value representation
    """

    # ----------------------------------------
    # 1. Remove frontend-only identity fields
    # ----------------------------------------

    if not isinstance(applicant_data, dict):
        raise TypeError("applicant_data must be a dictionary.")

    model_applicant_data = {
        field: value
        for field, value in applicant_data.items()
        if field not in FRONTEND_ONLY_FIELDS
    }

    # ----------------------------------------
    # 2. Validate
    # ----------------------------------------

    validate_applicant_fields(
        model_applicant_data
    )

    # ----------------------------------------
    # 3. Load model
    # ----------------------------------------

    if model is None:
        model = joblib.load(
            MODEL_PATH
        )

    # ----------------------------------------
    # 4. Get exact model columns
    # ----------------------------------------

    model_features = _model_features(
        model
    )

    # ----------------------------------------
    # 5. Normalize applicant values
    # ----------------------------------------

    normalized = _normalize_applicant(
        model_applicant_data
    )

    row = {}

    # ----------------------------------------
    # 5. Direct applicant features
    # ----------------------------------------

    for feature in APPLICANT_FEATURES:

        if feature not in model_features:
            continue

        value = normalized.get(
            feature
        )

        # Optional values must follow the
        # SAME missing-value convention used
        # during model training.
        if value is None:

            if feature == "emp_length":

                # Use ONLY if training used 0
                # for missing employment length.
                value = 0.0

            elif feature in {
                "mths_since_last_delinq",
                "mths_since_last_record",
            }:

                # Use ONLY if training used -1
                # for missing credit-history fields.
                value = -1.0

            else:
                raise ValueError(
                    f"Applicant input is missing "
                    f"model feature: {feature}"
                )

        row[feature] = value

    # ----------------------------------------
    # 6. Derived credit-history feature
    # ----------------------------------------

    if "credit_history_years" in model_features:

        credit_history_days = (
            normalized["issue_d"]
            - normalized["earliest_cr_line"]
        ).days

        row["credit_history_years"] = (
            credit_history_days / 365.25
        )

    # ----------------------------------------
    # 7. Missingness indicators
    # ----------------------------------------

    if "emp_length_missing" in model_features:

        row["emp_length_missing"] = float(
            normalized["emp_length"] is None
        )

    for feature in (
        "mths_since_last_delinq",
        "mths_since_last_record",
    ):

        flag = f"{feature}_missing"

        if flag in model_features:

            row[flag] = float(
                normalized[feature] is None
            )

    # ----------------------------------------
    # 8. One-hot categorical encoding
    # ----------------------------------------

    prefixes = {
        "home_ownership": "home_ownership_",
        "verification_status": "verification_status_",
        "purpose": "purpose_",
        "initial_list_status": "initial_list_status_",
        "application_type": "application_type_",
    }

    for raw_feature, prefix in prefixes.items():

        value = normalized[raw_feature]

        for model_feature in model_features:

            if model_feature.startswith(prefix):

                expected_value = (
                    model_feature[len(prefix):]
                )

                row[model_feature] = float(
                    expected_value == value
                )

    # ----------------------------------------
    # 9. Make sure EVERY model feature exists
    # ----------------------------------------

    missing = [
        feature
        for feature in model_features
        if feature not in row
    ]

    if missing:
        raise ValueError(
            "Could not construct a complete "
            "applicant-specific XGBoost vector. "
            f"Missing model features: {missing}"
        )

    # ----------------------------------------
    # 10. Build DataFrame in exact model order
    # ----------------------------------------

    result = pd.DataFrame(
        [
            [
                row[feature]
                for feature in model_features
            ]
        ],
        columns=model_features,
    )

    # ----------------------------------------
    # 11. Convert to numeric
    # ----------------------------------------

    result = result.apply(
        pd.to_numeric,
        errors="raise",
    )

    # ----------------------------------------
    # 12. Safety validation
    # ----------------------------------------

    if result.isna().any().any():

        missing_values = result.columns[
            result.isna().any()
        ].tolist()

        raise ValueError(
            "Applicant model vector contains "
            f"NaN values: {missing_values}"
        )

    values = result.to_numpy(
        dtype=float
    )

    if not np.isfinite(values).all():

        raise ValueError(
            "Applicant model vector contains "
            "infinite values."
        )

    # ----------------------------------------
    # 13. Verify feature order
    # ----------------------------------------

    if list(result.columns) != model_features:

        raise ValueError(
            "Applicant model input columns do not "
            "match model.feature_names_in_."
        )

    return result, normalized


# ============================================================
# FRONTEND SCHEMA
# ============================================================

def schema_for_json():
    """
    Return frontend-friendly input metadata.

    The frontend can use this to construct
    form fields dynamically.
    """

    return [
        {
            "name": name,
            **{
                key: value
                for key, value in metadata.items()
                if key != "numeric"
            },
        }
        for name, metadata
        in APPLICANT_FEATURE_METADATA.items()
    ]


# ============================================================
# DEBUG / TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("APPLICANT FEATURE VECTOR TEST")
    print("=" * 60)

    # Example applicant.
    example_applicant = {
        "loan_amnt": 15000,
        "term": 36,
        "int_rate": 12.5,
        "installment": 500,
        "emp_length": 5,
        "home_ownership": "RENT",
        "annual_inc": 60000,
        "verification_status": "Verified",
        "issue_d": "Dec-2015",
        "purpose": "debt_consolidation",
        "dti": 20,
        "delinq_2yrs": 0,
        "earliest_cr_line": "Jan-2000",
        "fico_range_low": 700,
        "fico_range_high": 704,
        "inq_last_6mths": 1,
        "mths_since_last_delinq": 20,
        "mths_since_last_record": 40,
        "open_acc": 8,
        "pub_rec": 0,
        "revol_bal": 5000,
        "revol_util": 35,
        "total_acc": 15,
        "initial_list_status": "w",
        "application_type": "Individual",
        "acc_now_delinq": 0,
        "tot_coll_amt": 0,
        "tot_cur_bal": 25000,
        "mort_acc": 1,
        "pub_rec_bankruptcies": 0,
        "tax_liens": 0,
    }

    model = joblib.load(
        MODEL_PATH
    )

    model_input, normalized = build_model_input(
        example_applicant,
        model,
    )

    print(
        f"\nModel expects: "
        f"{len(model.feature_names_in_)} features"
    )

    print(
        f"Generated: "
        f"{len(model_input.columns)} features"
    )

    print(
        "\nFeature order correct:",
        list(model_input.columns)
        == list(model.feature_names_in_),
    )

    print(
        "\nContains NaN:",
        model_input.isna().any().any(),
    )

    print(
        "Contains infinite:",
        not np.isfinite(
            model_input.to_numpy(
                dtype=float
            )
        ).all(),
    )

    print("\nMODEL INPUT:")
    print(model_input.to_string(index=False))

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)