"""
Threshold analysis for Approve / Review / Reject tiers.
Generates a visual justification for threshold placement,
based on the model's predicted probability distribution.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- Load model predictions ----
# Expects a CSV with columns: y_true, predicted_probability
# (probability of default, from model.predict_proba(X_test)[:, 1])
predictions = pd.read_csv("reports/lightgbm_predictions.csv")

probs = predictions["default_probability"]
y_true = predictions["actual_default"]

# ---- Set thresholds (tune these based on the histogram) ----
LOW_THRESHOLD = 0.35   # below this = Approve
HIGH_THRESHOLD = 0.55  # above this = Reject
# everything in between = Needs Review

# ---- Classify each applicant into a tier ----
def classify(p):
    if p < LOW_THRESHOLD:
        return "Approved"
    elif p > HIGH_THRESHOLD:
        return "Rejected"
    else:
        return "Needs Review"

predictions["decision_tier"] = probs.apply(classify)

# ---- Print summary stats (useful for your slide/report text) ----
tier_counts = predictions["decision_tier"].value_counts()
tier_pct = predictions["decision_tier"].value_counts(normalize=True) * 100

print("Decision tier breakdown:")
for tier in ["Approved", "Needs Review", "Rejected"]:
    count = tier_counts.get(tier, 0)
    pct = tier_pct.get(tier, 0)
    print(f"  {tier}: {count:,} applicants ({pct:.1f}%)")

# ---- Plot: probability distribution with threshold bands ----
fig, ax = plt.subplots(figsize=(10, 6))

ax.hist(probs, bins=60, color="#4C72B0", edgecolor="white", alpha=0.85)

# Shade the three zones
ax.axvspan(0, LOW_THRESHOLD, color="green", alpha=0.12, label="Auto-Approve zone")
ax.axvspan(LOW_THRESHOLD, HIGH_THRESHOLD, color="orange", alpha=0.12, label="Needs Review zone")
ax.axvspan(HIGH_THRESHOLD, 1, color="red", alpha=0.12, label="Auto-Reject zone")

# Threshold lines
ax.axvline(LOW_THRESHOLD, color="green", linestyle="--", linewidth=1.5)
ax.axvline(HIGH_THRESHOLD, color="red", linestyle="--", linewidth=1.5)

ax.set_xlabel("Predicted Probability of Default", fontsize=12)
ax.set_ylabel("Number of Applicants", fontsize=12)
ax.set_title("Model Confidence Distribution & Decision Thresholds", fontsize=14)
ax.legend(loc="upper right")

plt.tight_layout()
plt.savefig("outputs/threshold_analysis.png", dpi=150)
plt.show()

print(f"\nPlot saved to outputs/threshold_analysis.png")