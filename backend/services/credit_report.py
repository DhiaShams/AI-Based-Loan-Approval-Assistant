"""Parser for the simple key/value credit-report TXT upload."""

import re

CREDIT_REPORT_FIELDS = [
    "delinq_2yrs", "earliest_cr_line", "fico_range_low", "fico_range_high",
    "inq_last_6mths", "mths_since_last_delinq", "mths_since_last_record",
    "open_acc", "pub_rec", "revol_bal", "revol_util", "total_acc",
    "acc_now_delinq", "tot_coll_amt", "tot_cur_bal", "mort_acc",
    "pub_rec_bankruptcies", "tax_liens",
]


def parse_credit_report(uploaded_file):
    """Parse ``field: value`` or ``field=value`` lines into model fields."""
    if uploaded_file is None:
        raise ValueError("Please upload a credit report TXT file.")
    if not uploaded_file.name.lower().endswith(".txt"):
        raise ValueError("Credit report must be a .txt file.")
    text = uploaded_file.getvalue().decode("utf-8", errors="replace")
    values = {}
    for line in text.splitlines():
        match = re.match(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*[:=]\s*(.*?)\s*$", line)
        if match:
            key, value = match.groups()
            key = key.lower()
            if key in CREDIT_REPORT_FIELDS:
                values[key] = value
    missing = [field for field in CREDIT_REPORT_FIELDS if field not in values]
    if missing:
        raise ValueError(f"Credit report is missing required field(s): {', '.join(missing)}")
    return _normalize_credit_values(values)


def _normalize_credit_values(values):
    normalized = dict(values)
    for field in CREDIT_REPORT_FIELDS:
        if field == "earliest_cr_line":
            continue
        if values[field].strip().lower() in {"none", "null", "na", "n/a", ""}:
            normalized[field] = None
        else:
            try:
                normalized[field] = float(values[field].strip().rstrip("%"))
            except ValueError as error:
                raise ValueError(f"Credit report field {field} must be numeric.") from error
    return normalized
