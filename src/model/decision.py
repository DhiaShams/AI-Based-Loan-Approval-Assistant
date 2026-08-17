"""Decision logic that converts model probability into a human-facing recommendation."""

from __future__ import annotations

from typing import Dict, Any


DECISION_THRESHOLDS = {
    "LOW": 0.30,
    "MEDIUM": 0.60,
}


def decide_default_risk(probability: float) -> Dict[str, Any]:
    """Convert a default probability into a risk level and recommendation.

    The thresholds below are intentionally configurable and should be treated as
    starting values rather than claimed optimal operating points.
    """
    probability = float(probability)

    if probability < DECISION_THRESHOLDS["LOW"]:
        risk_level = "LOW"
        recommendation = "APPROVE"
    elif probability < DECISION_THRESHOLDS["MEDIUM"]:
        risk_level = "MEDIUM"
        recommendation = "MANUAL REVIEW"
    else:
        risk_level = "HIGH"
        recommendation = "REJECT"

    return {
        "default_probability": probability,
        "risk_level": risk_level,
        "recommendation": recommendation,
    }
