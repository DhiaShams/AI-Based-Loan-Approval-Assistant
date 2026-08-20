"""Operational probability-to-recommendation policy.

This policy is separate from the LightGBM classifier and from SHAP. The
thresholds are MVP decision-policy settings, not model training thresholds.
"""

import math


LOW_THRESHOLD = 0.35
HIGH_THRESHOLD = 0.55


def apply_decision_policy(default_probability):
    """Return risk and recommendation for a validated default probability."""
    probability = float(default_probability)
    if not math.isfinite(probability) or not 0 <= probability <= 1:
        raise ValueError("default_probability must be a finite value between 0 and 1.")
    if probability < LOW_THRESHOLD:
        risk_level, recommendation = "LOW", "APPROVE"
    elif probability < HIGH_THRESHOLD:
        risk_level, recommendation = "MEDIUM", "REVIEW"
    else:
        risk_level, recommendation = "HIGH", "REJECT"
    return {
        "risk_level": risk_level,
        "recommendation": recommendation,
        "thresholds": {
            "low": LOW_THRESHOLD,
            "high": HIGH_THRESHOLD,
        },
    }