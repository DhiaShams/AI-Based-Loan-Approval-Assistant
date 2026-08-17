import pandas as pd
import pytest

from src.model.predict import validate_required_features, prepare_applicant_record


def test_missing_required_features():
    record = {"loan_amnt": 15000, "dti": 18.0}
    with pytest.raises(ValueError):
        validate_required_features(record)


def test_basic_preprocessing_behavior():
    record = {
        "loan_amnt": 15000,
        "annual_inc": 65000,
        "dti": 18.0,
        "fico_range_low": 700,
        "revol_util": 45.0,
        "term": 36,
        "int_rate": 8.5,
        "emp_length": 5,
        "home_ownership": "MORTGAGE",
        "verification_status": "Verified",
        "purpose": "debt_consolidation",
    }

    prepared = prepare_applicant_record(record)
    assert isinstance(prepared, pd.DataFrame)
    assert prepared.shape[1] >= 1
    assert prepared.loc[0, "loan_amnt"] == 15000
