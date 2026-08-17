"""Train and save default-risk models for the loan approval project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT_DIR / "data" / "processed" / "loans_clean_v1.csv"
MODEL_PATH = ROOT_DIR / "models" / "loan_default_model.joblib"
METRICS_PATH = ROOT_DIR / "reports" / "metrics"


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric_columns = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = [col for col in X.columns if col not in numeric_columns]

    transformers: List[Tuple[str, object, List[str]]] = []
    if numeric_columns:
        transformers.append(("numeric", StandardScaler(), numeric_columns))
    if categorical_columns:
        transformers.append(("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_columns))

    if not transformers:
        return ColumnTransformer([("identity", "passthrough", X.columns.tolist())], remainder="drop")

    return ColumnTransformer(transformers, remainder="drop")


def build_models() -> Dict[str, object]:
    return {
        "logistic_regression": LogisticRegression(
            class_weight="balanced",
            max_iter=2000,
            random_state=42,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
        ),
        "xgboost": XGBClassifier(
            n_estimators=400,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="binary:logistic",
            eval_metric="logloss",
            scale_pos_weight=1.5,
            random_state=42,
        ),
    }


def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average="binary", zero_division=0
    )
    roc_auc = roc_auc_score(y_test, y_prob)

    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(roc_auc),
    }


def select_best_model(results: Dict[str, Dict[str, float]]) -> str:
    return max(results, key=lambda name: (results[name]["roc_auc"], results[name]["recall"]))


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "Required cleaned dataset not found. Run: python src/data/clean.py"
        )

    df = pd.read_csv(DATA_PATH)
    target = "default_flag"
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in {DATA_PATH}.")

    X = df.drop(columns=[target])
    y = df[target].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    results: Dict[str, Dict[str, float]] = {}
    trained_models: Dict[str, Pipeline] = {}

    for name, estimator in build_models().items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", build_preprocessor(X_train)),
                ("model", estimator),
            ]
        )
        pipeline.fit(X_train, y_train)
        results[name] = evaluate_model(pipeline, X_test, y_test)
        trained_models[name] = pipeline

    best_name = select_best_model(results)
    best_model = trained_models[best_name]

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODEL_PATH)

    METRICS_PATH.mkdir(parents=True, exist_ok=True)
    with (METRICS_PATH / "training_summary.json").open("w", encoding="utf-8") as fh:
        json.dump({"best_model": best_name, "metrics": results}, fh, indent=2)

    print("Model training summary:")
    for name, metrics in results.items():
        print(f"- {name}: {metrics}")
    print(f"Selected model: {best_name}")
    print(f"Saved model to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
