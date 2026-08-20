import pandas as pd

preds = pd.read_csv("reports/lightgbm_predictions.csv")
fairness_ref = pd.read_csv("data/processed/fairness_reference_v1.csv")

print("Predictions default rate:", preds["actual_default"].mean())
print("Fairness ref default rate:", fairness_ref["default_flag"].mean())