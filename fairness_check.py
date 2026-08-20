import pandas as pd
from fairlearn.metrics import (
    MetricFrame, selection_rate, false_positive_rate, false_negative_rate,
    demographic_parity_difference, equalized_odds_difference
)
from sklearn.metrics import accuracy_score, recall_score, precision_score

# ---- Load data ----
preds = pd.read_csv("reports/lightgbm_predictions.csv")
fairness_ref = pd.read_csv("data/processed/fairness_reference_v1.csv")

# ---- Merge on shared row order/id ----
# This assumes both CSVs have the exact same row order. 
df = preds.merge(fairness_ref, left_index=True, right_index=True)

# ---- Convert probability to hard decision using your threshold ----
THRESHOLD = 0.5  
# UPDATED: Changed from 'predicted_probability' to 'default_probability'
df["y_pred"] = (df["default_probability"] >= THRESHOLD).astype(int)

# Alternative: Since your CSV already contains 'predicted_default', 
# you could simply use: df["y_pred"] = df["predicted_default"]

# ---- Group rare states together to avoid noisy small-sample groups ----
state_counts = df["addr_state"].value_counts()
top_states = state_counts[state_counts >= 1000].index  # keep states w/ enough data
df["state_group"] = df["addr_state"].where(df["addr_state"].isin(top_states), "Other")

# ---- Compute per-group metrics ----
metric_frame = MetricFrame(
    metrics={
        "accuracy": accuracy_score,
        "selection_rate": selection_rate,        # % predicted default (flagged risky)
        "false_positive_rate": false_positive_rate,
        "false_negative_rate": false_negative_rate,
        "precision": precision_score,
        "recall": recall_score,
    },
    # UPDATED: Changed 'y_true' to 'actual_default'
    y_true=df["actual_default"],
    y_pred=df["y_pred"],
    sensitive_features=df["state_group"]
)

by_group = metric_frame.by_group
print(by_group)

# ---- Headline fairness metrics ----
# UPDATED: Changed 'y_true' to 'actual_default'
# ---- Headline fairness metrics ----
dp_diff = demographic_parity_difference(df["actual_default"], df["y_pred"], sensitive_features=df["state_group"])
eo_diff = equalized_odds_difference(df["actual_default"], df["y_pred"], sensitive_features=df["state_group"])

print(f"\nDemographic Parity Difference: {dp_diff:.3f}")
print(f"Equalized Odds Difference: {eo_diff:.3f}")

# ---- Save for dashboard / report ----
by_group.to_csv("outputs/fairness_by_group.csv")

# ---- NEW CODE: Find states with the highest False Positive Rate ----
sorted_by_fpr = by_group.sort_values(by="false_positive_rate", ascending=False)

print("\n--- Top 5 States by Highest False Positive Rate ---")
print(sorted_by_fpr[["false_positive_rate", "false_negative_rate", "selection_rate"]].head())