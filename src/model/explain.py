import os
import json
import joblib
import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = "models/lightgbm.pkl"
PREDICTIONS_PATH = "reports/lightgbm_predictions.csv"

REPORTS_DIR = "reports"

GLOBAL_IMPORTANCE_PATH = (
    "reports/shap_feature_importance.csv"
)

GLOBAL_PLOT_PATH = (
    "reports/shap_beeswarm.png"
)

LOCAL_IMPORTANCE_PATH = (
    "reports/shap_local_explanation.csv"
)

LOCAL_PLOT_PATH = (
    "reports/shap_local_explanation.png"
)

LOCAL_JSON_PATH = (
    "reports/shap_local_explanation.json"
)

# Default applicant
# Change this number later when explaining another applicant
APPLICANT_INDEX = 0


# ============================================================
# CREATE REPORT DIRECTORY
# ============================================================

os.makedirs(REPORTS_DIR, exist_ok=True)


# ============================================================
# 1. LOAD LGBMOOST MODEL
# ============================================================

print("Loading LightGBM model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully!")
print("Model type:", type(model))


# ============================================================
# 2. LOAD TEST DATA
# ============================================================

print("\nLoading test predictions...")

predictions = pd.read_csv(
    PREDICTIONS_PATH
)

print("Rows:", len(predictions))
print("Columns:", len(predictions.columns))


# ============================================================
# 3. GET EXACT MODEL FEATURES
# ============================================================

# IMPORTANT:
# Use the feature names stored inside the LightGBM model.
#
# This guarantees that SHAP receives exactly the same
# features and order that LightGBM expects.

feature_names = list(
    model.feature_names_in_
)

print("\nNumber of model features:", len(feature_names))

print("Model features:")
print(feature_names)


# ============================================================
# 4. CREATE X INPUT FOR SHAP
# ============================================================

# Only take the 52 features used by LightGBM.
#
# Do NOT include:
# actual_default
# predicted_default
# default_probability
#
# These are prediction outputs, not model inputs.

X = predictions[
    feature_names
].copy()


# ============================================================
# 5. CONVERT BOOLEAN FEATURES
# ============================================================

boolean_features = X.select_dtypes(
    include=["bool"]
).columns.tolist()

if boolean_features:

    print("\nConverting boolean features:")

    print(boolean_features)

    X[boolean_features] = (
        X[boolean_features]
        .astype(int)
    )


# Make sure everything is numeric

X = X.apply(
    pd.to_numeric,
    errors="coerce"
)


print("\nX shape:", X.shape)


# ============================================================
# 6. CREATE SHAP EXPLAINER
# ============================================================

print("\nCreating SHAP TreeExplainer...")

explainer = shap.TreeExplainer(
    model
)

print(
    "SHAP TreeExplainer created successfully!"
)


# ============================================================
# 7. CALCULATE SHAP VALUES
# ============================================================

print("\nCalculating SHAP values...")

shap_values = explainer.shap_values(X)

print(
    "SHAP values calculated successfully!"
)

print(
    "SHAP shape:",
    np.array(shap_values).shape
)


# ============================================================
# 8. HANDLE SHAP OUTPUT
# ============================================================

# For binary LightGBM classification, SHAP normally
# returns:
#
#     samples × features
#
# Some versions/configurations can return additional
# dimensions, so normalize it here.

if isinstance(shap_values, list):

    # Binary classification:
    # use SHAP values corresponding to class 1 = Default
    shap_values = shap_values[1]


shap_values = np.asarray(
    shap_values
)


if shap_values.ndim == 3:

    # If shape is:
    #
    # samples × features × classes
    #
    # select class 1 = Default

    shap_values = shap_values[:, :, 1]


print(
    "Final SHAP shape:",
    shap_values.shape
)


# ============================================================
# 9. GLOBAL SHAP FEATURE IMPORTANCE
# ============================================================

print("\nGenerating SHAP feature importance...")


# Average absolute SHAP value across all applicants

mean_abs_shap = np.abs(
    shap_values
).mean(axis=0)


global_importance = pd.DataFrame({

    "feature": feature_names,

    "mean_abs_shap": mean_abs_shap

})


global_importance = (
    global_importance
    .sort_values(
        "mean_abs_shap",
        ascending=False
    )
    .reset_index(drop=True)
)


print("\nTop 15 SHAP features:")

print(
    global_importance.head(15).to_string(
        index=False
    )
)


global_importance.to_csv(
    GLOBAL_IMPORTANCE_PATH,
    index=False
)


print(
    "\nSaved:",
    GLOBAL_IMPORTANCE_PATH
)


# ============================================================
# 10. GLOBAL SHAP BEESWARM PLOT
# ============================================================

print("\nGenerating SHAP beeswarm plot...")


plt.figure(
    figsize=(10, 8)
)


shap.summary_plot(
    shap_values,
    X,
    feature_names=feature_names,
    max_display=20,
    show=False
)


plt.tight_layout()


plt.savefig(
    GLOBAL_PLOT_PATH,
    dpi=200,
    bbox_inches="tight"
)


plt.close()


print(
    "Saved:",
    GLOBAL_PLOT_PATH
)


# ============================================================
# 11. SELECT APPLICANT
# ============================================================

if (
    APPLICANT_INDEX < 0
    or APPLICANT_INDEX >= len(X)
):

    raise IndexError(
        f"Applicant index {APPLICANT_INDEX} "
        f"is outside available range "
        f"0-{len(X)-1}"
    )


print(
    f"\nExplaining applicant index: "
    f"{APPLICANT_INDEX}"
)


applicant = X.iloc[
    APPLICANT_INDEX
]

applicant_shap = shap_values[
    APPLICANT_INDEX
]


# ============================================================
# 12. GET MODEL PREDICTION
# ============================================================

applicant_df = applicant.to_frame().T


prediction = int(
    model.predict(applicant_df)[0]
)


default_probability = float(
    model.predict_proba(
        applicant_df
    )[0][1]
)


prediction_label = (
    "Default"
    if prediction == 1
    else "Non-default"
)


print("\nPrediction:")
print(
    "Class:",
    prediction_label
)

print(
    "Default probability:",
    f"{default_probability * 100:.2f}%"
)


# ============================================================
# 13. CREATE LOCAL SHAP DATA
# ============================================================

local_data = pd.DataFrame({

    "feature": feature_names,

    "value": applicant.values,

    "shap_value": applicant_shap

})


# Absolute importance

local_data["abs_shap"] = (
    local_data["shap_value"]
    .abs()
)


# Direction of influence

local_data["impact"] = np.where(

    local_data["shap_value"] > 0,

    "increases_default_risk",

    "decreases_default_risk"

)


# Sort by strongest impact

local_data = (
    local_data
    .sort_values(
        "abs_shap",
        ascending=False
    )
    .reset_index(drop=True)
)


# ============================================================
# 14. SAVE LOCAL CSV
# ============================================================

local_data.to_csv(
    LOCAL_IMPORTANCE_PATH,
    index=False
)


print(
    "\nSaved:",
    LOCAL_IMPORTANCE_PATH
)


# ============================================================
# 15. RISK / PROTECTIVE FACTORS
# ============================================================

risk_factors = (
    local_data[
        local_data["shap_value"] > 0
    ]
    .head(5)
)


protective_factors = (
    local_data[
        local_data["shap_value"] < 0
    ]
    .head(5)
)


# ============================================================
# 16. PRINT HUMAN-READABLE EXPLANATION
# ============================================================

print("\n")
print("=" * 65)

print(
    "LOCAL SHAP EXPLANATION"
)

print("=" * 65)


print(
    f"\nPrediction: {prediction_label}"
)

print(
    f"Default probability: "
    f"{default_probability * 100:.2f}%"
)


# ------------------------------------------------------------
# Factors increasing default risk
# ------------------------------------------------------------

print(
    "\nFactors pushing toward DEFAULT:"
)


for _, row in risk_factors.iterrows():

    print(
        f"  + {row['feature']}: "
        f"value={row['value']}, "
        f"SHAP={row['shap_value']:.4f}"
    )


# ------------------------------------------------------------
# Factors decreasing default risk
# ------------------------------------------------------------

print(
    "\nFactors pushing toward NON-DEFAULT:"
)


for _, row in protective_factors.iterrows():

    print(
        f"  - {row['feature']}: "
        f"value={row['value']}, "
        f"SHAP={row['shap_value']:.4f}"
    )


# ============================================================
# 17. LOCAL SHAP BAR GRAPH
# ============================================================

print(
    "\nGenerating local SHAP explanation graph..."
)


# Show top 10 factors

plot_data = (
    local_data
    .head(10)
    .sort_values(
        "shap_value"
    )
)


plt.figure(
    figsize=(10, 6)
)


plt.barh(
    plot_data["feature"],
    plot_data["shap_value"]
)


plt.axvline(
    0,
    linewidth=1
)


plt.xlabel(
    "SHAP value"
)

plt.ylabel(
    "Feature"
)

plt.title(
    f"Why LightGBM predicted "
    f"{prediction_label}"
)


plt.tight_layout()


plt.savefig(
    LOCAL_PLOT_PATH,
    dpi=200,
    bbox_inches="tight"
)


plt.close()


print(
    "Saved:",
    LOCAL_PLOT_PATH
)


# ============================================================
# 18. CREATE JSON FOR FRONTEND
# ============================================================

print(
    "\nCreating frontend JSON..."
)


# Convert Pandas/Numpy values into normal Python values

def convert_value(value):

    if pd.isna(value):

        return None

    if isinstance(
        value,
        (np.integer,)
    ):

        return int(value)

    if isinstance(
        value,
        (np.floating,)
    ):

        return float(value)

    return value


def create_factor(row):

    return {

        "feature": str(
            row["feature"]
        ),

        "value": convert_value(
            row["value"]
        ),

        "shap_value": float(
            row["shap_value"]
        ),

        "absolute_shap": float(
            row["abs_shap"]
        ),

        "impact": str(
            row["impact"]
        )

    }


# Top 10 factors

top_factors = [

    create_factor(row)

    for _, row
    in local_data.head(10).iterrows()

]


# Top risk factors

risk_factor_json = [

    create_factor(row)

    for _, row
    in risk_factors.iterrows()

]


# Top protective factors

protective_factor_json = [

    create_factor(row)

    for _, row
    in protective_factors.iterrows()

]


# ------------------------------------------------------------
# Final JSON structure
# ------------------------------------------------------------

explanation = {

    "applicant_index":
        APPLICANT_INDEX,

    "prediction": {

        "class":
            prediction,

        "label":
            prediction_label,

        "default_probability":
            default_probability,

        "default_probability_percent":
            round(
                default_probability * 100,
                2
            )

    },

    "top_factors":
        top_factors,

    "risk_factors":
        risk_factor_json,

    "protective_factors":
        protective_factor_json,

    "visualization": {

        "local_plot":
            "shap_local_explanation.png",

        "global_plot":
            "shap_beeswarm.png"

    }

}


# ============================================================
# 19. SAVE JSON
# ============================================================

with open(
    LOCAL_JSON_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        explanation,
        file,
        indent=4
    )


print(
    "Saved:",
    LOCAL_JSON_PATH
)


# ============================================================
# 20. FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 65)

print("SHAP EXPLANATION COMPLETE")

print("=" * 65)

print(
    "\nGenerated files:"
)

print(
    "1. Global importance:"
)

print(
    f"   {GLOBAL_IMPORTANCE_PATH}"
)

print(
    "2. Global beeswarm:"
)

print(
    f"   {GLOBAL_PLOT_PATH}"
)

print(
    "3. Local explanation CSV:"
)

print(
    f"   {LOCAL_IMPORTANCE_PATH}"
)

print(
    "4. Local explanation graph:"
)

print(
    f"   {LOCAL_PLOT_PATH}"
)

print(
    "5. Frontend JSON:"
)

print(
    f"   {LOCAL_JSON_PATH}"
)

print("\nDone!")