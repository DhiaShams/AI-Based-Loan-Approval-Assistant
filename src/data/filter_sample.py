import pandas as pd

RAW_PATH = "data/raw/loan_data.csv"
OUTPUT_PATH = "data/interim/loans_sample_v1.csv"

CORE_COLUMNS = [
    "id", "loan_amnt", "term", "int_rate", "installment",
    "grade", "sub_grade", "emp_length", "home_ownership", "annual_inc",
    "verification_status", "issue_d", "loan_status", "purpose",
     "dti", "delinq_2yrs", "earliest_cr_line",
    "fico_range_low", "fico_range_high", "inq_last_6mths",
    "mths_since_last_delinq", "mths_since_last_record", "open_acc",
    "pub_rec", "revol_bal", "revol_util", "total_acc",
    "initial_list_status", "application_type", "acc_now_delinq",
    "tot_coll_amt", "tot_cur_bal", "mort_acc", "pub_rec_bankruptcies",
    "tax_liens",
]

RESOLVED_STATUSES = ["Fully Paid", "Charged Off"]
SAMPLE_SIZE = 75_000
RANDOM_STATE = 42
CHUNK_SIZE = 100_000


def load_filtered():
    chunks = []
    reader = pd.read_csv(
        RAW_PATH,
        usecols=CORE_COLUMNS,
        chunksize=CHUNK_SIZE,
        dtype=str,             # avoid per-column type inference across chunks
        on_bad_lines="skip",   # safety net for any stray malformed row
    )
    total_kept = 0
    for i, chunk in enumerate(reader):
        filtered = chunk[chunk["loan_status"].isin(RESOLVED_STATUSES)]
        total_kept += len(filtered)
        if not filtered.empty:
            chunks.append(filtered)
        print(f"Chunk {i+1}: {len(chunk)} rows read, {total_kept} kept so far")
    return pd.concat(chunks, ignore_index=True)


def stratified_sample(df, n=SAMPLE_SIZE):
    if len(df) <= n:
        return df
    frac = n / len(df)
    parts = [
        group.sample(frac=frac, random_state=RANDOM_STATE)
        for _, group in df.groupby("loan_status")
    ]
    return pd.concat(parts, ignore_index=True)


def main():
    print("Loading and filtering raw data...")
    df = load_filtered()
    print(f"Resolved loans found: {len(df):,}")

    df_sample = stratified_sample(df)
    print(f"Sample size: {len(df_sample):,}")
    print(df_sample["loan_status"].value_counts())

    df_sample.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()