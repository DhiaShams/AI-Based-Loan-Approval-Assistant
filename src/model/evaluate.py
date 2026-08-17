"""Model evaluation utilities for loan default prediction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_curve, roc_auc_score, roc_curve

ROOT_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT_DIR / "models" / "loan_default_model.joblib"
DATA_PATH = ROOT_DIR / "data" / "processed" / "loans_clean_v1.csv"
METRICS_PATH = ROOT_DIR / "reports" / "metrics" / "model_metrics.json"
FIGURES_PATH = ROOT_DIR / "reports" / "figures"


def evaluate_saved_model(model_path: Path = MODEL_PATH) -> Dict[str, Any]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "Cleaned data is required for evaluation. Run python src/data/clean.py first."
        )
    if not model_path.exists():
        raise FileNotFoundError(
            "Trained model was not found. Run python src/model/train.py first."
        )

    df = pd.read_csv(DATA_PATH)
    target = "default_flag"
    X = df.drop(columns=[target])
    y = df[target].astype(int)

    model = joblib.load(model_path)
    y_prob = model.predict_proba(X)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    tn, fp, fn, tp = confusion_matrix(y, y_pred).ravel()
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    roc_auc = roc_auc_score(y, y_prob)

    metrics = {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(roc_auc),
        "false_approvals": int(fp),
        "false_rejections": int(fn),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
    }

    FIGURES_PATH.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(6, 6))
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Random")
    fpr, tpr, _ = roc_curve(y, y_prob)
    plt.plot(fpr, tpr, label=f"ROC-AUC = {roc_auc:.3f}")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_PATH / "roc_curve.png", dpi=150)
    plt.close()

    precision_curve, recall_curve, _ = precision_recall_curve(y, y_prob)
    plt.figure(figsize=(6, 6))
    plt.plot(recall_curve, precision_curve, label="Precision-Recall Curve")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_PATH / "precision_recall_curve.png", dpi=150)
    plt.close()

    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    print(evaluate_saved_model())
