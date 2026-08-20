import os
import joblib
import pandas as pd

from lightgbm import LGBMClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/processed/loans_clean_v1.csv"

MODEL_PATH = "models/lightgbm.pkl"
METRICS_PATH = "reports/lightgbm_metrics.csv"
PREDICTIONS_PATH = "reports/lightgbm_predictions.csv"
IMPORTANCE_PATH = "reports/lightgbm_feature_importance.csv"

os.makedirs("models", exist_ok=True)
os.makedirs("reports", exist_ok=True)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("Loading cleaned dataset...")

df = pd.read_csv(DATA_PATH)

print(f"\nRows: {len(df):,}")
print(f"Columns: {len(df.columns)}")


# ============================================================
# 2. TARGET
# ============================================================

TARGET = "default_flag"

y = df[TARGET]

print("\nTarget distribution:")
print(y.value_counts())

print("\nTarget proportions:")
print(y.value_counts(normalize=True))


# ============================================================
# 3. REMOVE TARGET / RAW DATE / GRADE FEATURES
# ============================================================

DROP_COLUMNS = [
    TARGET,
    "issue_d",
    "earliest_cr_line",

    # Removed according to your current LightGBM setup
    "grade_encoded",
    "sub_grade_encoded"
]

X = df.drop(
    columns=DROP_COLUMNS,
    errors="ignore"
)


print(f"\nFeatures used: {X.shape[1]}")

print("\nFeatures:")
print(X.columns.tolist())


# ============================================================
# 4. CONVERT BOOLEAN FEATURES
# ============================================================

boolean_features = X.select_dtypes(
    include=["bool"]
).columns.tolist()

if boolean_features:

    print("\nConverting Boolean features to 0/1:")

    print(boolean_features)

    X[boolean_features] = X[
        boolean_features
    ].astype("int8")


# ============================================================
# 5. CHECK NON-NUMERIC FEATURES
# ============================================================

non_numeric = X.select_dtypes(
    exclude=["number"]
).columns.tolist()

if non_numeric:

    print("\nRemaining non-numeric columns:")
    print(non_numeric)

    raise ValueError(
        "Non-numeric columns remain in the dataset."
    )

print("\nAll LightGBM features are numeric.")


# ============================================================
# 6. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTrain size:", len(X_train))
print("Test size :", len(X_test))


# ============================================================
# 7. CLASS IMBALANCE
# ============================================================

negative = (y_train == 0).sum()
positive = (y_train == 1).sum()

scale_pos_weight = negative / positive

print("\nClass distribution:")
print("Non-default:", negative)
print("Default:", positive)

print(
    "scale_pos_weight:",
    scale_pos_weight
)


# ============================================================
# 8. LIGHTGBM MODEL
# ============================================================

model = LGBMClassifier(
    n_estimators=1500,
    learning_rate=0.02,

    num_leaves=31,
    max_depth=6,
    min_child_samples=40,

    subsample=0.9,
    colsample_bytree=0.9,

    min_split_gain=0.05,

    reg_alpha=0.1,
    reg_lambda=3.0,

    scale_pos_weight=scale_pos_weight,

    objective="binary",
    metric="auc",

    random_state=42,
    n_jobs=-1,
    verbosity=-1
)

# ============================================================
# 9. TRAIN
# ============================================================

print("\nTraining LightGBM...")

model.fit(
    X_train,
    y_train
)

print("Training completed.")


# ============================================================
# 10. PREDICTIONS
# ============================================================

y_pred = model.predict(X_test)

y_prob = model.predict_proba(
    X_test
)[:, 1]


# ============================================================
# 11. EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    y_prob
)


# ============================================================
# 12. PRINT RESULTS
# ============================================================

print("\n")
print("=" * 55)
print("LIGHTGBM RESULTS")
print("=" * 55)

print(f"Accuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")
print(f"ROC-AUC   : {roc_auc:.4f}")


# ============================================================
# 13. CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    y_pred
)

print("\nConfusion Matrix:")
print(cm)


# ============================================================
# 14. CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Non-default",
            "Default"
        ],
        zero_division=0
    )
)


# ============================================================
# 15. SAVE PREDICTIONS
# ============================================================

predictions = X_test.copy()

predictions["actual_default"] = y_test.values

predictions["predicted_default"] = y_pred

predictions["default_probability"] = y_prob

predictions.to_csv(
    PREDICTIONS_PATH,
    index=False
)


# ============================================================
# 16. SAVE METRICS
# ============================================================

metrics = pd.DataFrame([{

    "model": "LightGBM",

    "accuracy": accuracy,

    "precision": precision,

    "recall": recall,

    "f1_score": f1,

    "roc_auc": roc_auc

}])

metrics.to_csv(
    METRICS_PATH,
    index=False
)


# ============================================================
# 17. FEATURE IMPORTANCE
# ============================================================

feature_importance = pd.DataFrame({

    "feature": X.columns,

    "importance": model.feature_importances_

})

feature_importance = feature_importance.sort_values(
    by="importance",
    ascending=False
)

feature_importance.to_csv(
    IMPORTANCE_PATH,
    index=False
)


# ============================================================
# 18. SAVE MODEL
# ============================================================

joblib.dump(
    model,
    MODEL_PATH
)


# ============================================================
# 19. FINAL OUTPUT
# ============================================================

print("\nFiles saved:")

print(f"Model       : {MODEL_PATH}")

print(f"Metrics     : {METRICS_PATH}")

print(f"Predictions : {PREDICTIONS_PATH}")

print(f"Importance  : {IMPORTANCE_PATH}")
