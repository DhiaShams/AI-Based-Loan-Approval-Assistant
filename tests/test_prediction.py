import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from src.model.predict import predict_applicant


def test_prediction_output_structure():
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=1000, random_state=42))
    ])
    X = pd.DataFrame(
        {
            "loan_amnt": [10000, 20000],
            "annual_inc": [60000, 80000],
            "dti": [15.0, 30.0],
            "fico_range_low": [680, 720],
            "revol_util": [35.0, 60.0],
        }
    )
    y = [0, 1]
    model.fit(X, y)

    record = {
        "loan_amnt": 15000,
        "annual_inc": 65000,
        "dti": 18.0,
        "fico_range_low": 700,
        "revol_util": 45.0,
    }

    result = predict_applicant(record, model=model)
    assert set(result.keys()) == {"default_probability", "risk_level", "recommendation"}
    assert 0.0 <= result["default_probability"] <= 1.0
    assert result["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
    assert result["recommendation"] in {"APPROVE", "MANUAL REVIEW", "REJECT"}
