"""
Day 2: Cleans the Day-1 sampled loan data.
- Fixes dtypes (dates, percent-strings, emp_length text -> numeric)
- Encodes the target (loan_status -> binary default flag)
- Handles missing values per column
- Encodes obvious categoricals
- Confirms no leakage columns are present
- Engineers a couple of basic features (credit history length)

Input:  data/interim/loans_sample_v1.csv   (output of Day 1 filter_sample.py)
Output: data/processed/loans_clean_v1.csv
"""

import pandas as pd
import numpy as np

INPUT_PATH = "data/interim/loans_sample_v1.csv"
OUTPUT_PATH = "data/processed/loans_clean_v1.csv"

# Columns that would leak the outcome if present. Day 1 already excludes
# these by only selecting CORE_COLUMNS, but we assert here as a guardrail
# in case someone re-runs Day 1 with a wider column list later.
LEAKAGE_COLUMNS = [
    "out_prncp", "out_prncp_inv", "total_pymnt", "total_pymnt_inv",
    "total_rec_prncp", "total_rec_int", "total_rec_late_fee",
    "recoveries", "collection_recovery_fee",
    "last_pymnt_d", "last_pymnt_amnt", "next_pymnt_d", "last_credit_pull_d",
    "last_fico_range_high", "last_fico_range_low",
    "hardship_flag", "hardship_type", "hardship_reason", "hardship_status",
    "debt_settlement_flag", "settlement_status", "settlement_amount",
]

# Columns that are effectively identifiers / free text / not modeling
# features. Dropped here rather than at Day 1, in case the team wants
# them for reference during EDA before this point.
DROP_COLUMNS = ["id"]

EMP_LENGTH_MAP = {
    "< 1 year": 0, "1 year": 1, "2 years": 2, "3 years": 3, "4 years": 4,
    "5 years": 5, "6 years": 6, "7 years": 7, "8 years": 8, "9 years": 9,
    "10+ years": 10,
}

CATEGORICAL_COLUMNS = [
    "home_ownership", "verification_status", "purpose",
    "initial_list_status", "application_type",
]

# grade/sub_grade are ordinal (credit quality), encode as ordered integers
# rather than one-hot, so the ordering information isn't thrown away.
GRADE_ORDER = ["A", "B", "C", "D", "E", "F", "G"]


def assert_no_leakage(df):
    present = [c for c in LEAKAGE_COLUMNS if c in df.columns]
    assert not present, f"Leakage columns found in input, remove them: {present}"


def fix_dtypes(df):
    # term: " 36 months" -> 36
    df["term"] = df["term"].str.extract(r"(\d+)").astype(float)

    # int_rate, revol_util: stored as plain numbers here but sometimes
    # arrive with a trailing '%' depending on source export - handle both.
    for col in ["int_rate", "revol_util"]:
        df[col] = (
            df[col].astype(str).str.replace("%", "", regex=False).astype(float)
        )

    # dates: format is like 'Dec-2015'
    for col in ["issue_d", "earliest_cr_line"]:
        df[col] = pd.to_datetime(df[col], format="%b-%Y", errors="coerce")

    # emp_length: text buckets -> numeric years
    df["emp_length"] = df["emp_length"].map(EMP_LENGTH_MAP)

    return df


def encode_target(df):
    df["default_flag"] = df["loan_status"].map(
        {"Fully Paid": 0, "Charged Off": 1, "Default": 1}
    )
    df = df.drop(columns=["loan_status"])
    return df


def engineer_features(df):
    # Credit history length in years at time of loan issue
    df["credit_history_years"] = (
        (df["issue_d"] - df["earliest_cr_line"]).dt.days / 365.25
    )
    return df


def handle_missing(df):
    # mths_since_last_delinq / mths_since_last_record: mostly missing,
    # but "missing" itself is informative (never delinquent/recorded).
    # Add a flag, then fill with a large sentinel value.
    for col in ["mths_since_last_delinq", "mths_since_last_record"]:
        df[f"{col}_missing"] = df[col].isna().astype(int)
        df[col] = df[col].fillna(-1)

    # emp_length missing -> assume 0 (unknown / not reported), flag separately
    df["emp_length_missing"] = df["emp_length"].isna().astype(int)
    df["emp_length"] = df["emp_length"].fillna(0)

    # revol_util, dti, tot_cur_bal, tot_coll_amt: small % missing, median impute
    for col in ["revol_util", "dti", "tot_cur_bal", "tot_coll_amt",
                "mort_acc", "pub_rec_bankruptcies", "credit_history_years"]:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # categorical missing -> explicit "Unknown" bucket
    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    # drop rows still missing the target or core identifiers - shouldn't
    # happen given Day 1 filtering, but guard anyway
    df = df.dropna(subset=["default_flag", "loan_amnt", "int_rate"])

    return df


def encode_categoricals(df):
    # ordinal grade
    df["grade_encoded"] = df["grade"].map(
        {g: i for i, g in enumerate(GRADE_ORDER)}
    )
    df["sub_grade_encoded"] = df["sub_grade"].apply(
        lambda s: (GRADE_ORDER.index(s[0]) * 5 + int(s[1])) if pd.notna(s) else np.nan
    )
    df = df.drop(columns=["grade", "sub_grade"])

    # one-hot the rest
    df = pd.get_dummies(df, columns=CATEGORICAL_COLUMNS, drop_first=True)

    return df


def main():
    print("Loading Day 1 sample...")
    df = pd.read_csv(INPUT_PATH)
    print(f"Rows in: {len(df):,}")

    assert_no_leakage(df)
    df = df.drop(columns=[c for c in DROP_COLUMNS if c in df.columns])

    df = fix_dtypes(df)
    df = encode_target(df)
    df = engineer_features(df)
    df = handle_missing(df)
    df = encode_categoricals(df)

    print(f"Rows out: {len(df):,}, columns out: {df.shape[1]}")
    print(df["default_flag"].value_counts(normalize=True))

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()