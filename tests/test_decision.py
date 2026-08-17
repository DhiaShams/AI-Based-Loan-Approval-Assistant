import pytest

from src.model.decision import decide_default_risk


def test_decision_thresholds():
    low = decide_default_risk(0.25)
    medium = decide_default_risk(0.45)
    high = decide_default_risk(0.75)

    assert low["risk_level"] == "LOW"
    assert low["recommendation"] == "APPROVE"
    assert medium["risk_level"] == "MEDIUM"
    assert medium["recommendation"] == "MANUAL REVIEW"
    assert high["risk_level"] == "HIGH"
    assert high["recommendation"] == "REJECT"
