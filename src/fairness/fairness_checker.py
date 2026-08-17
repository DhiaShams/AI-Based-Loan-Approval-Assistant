"""Generic fairness evaluation tools for grouped model metrics."""

from __future__ import annotations

from typing import Iterable, Sequence

import pandas as pd
from sklearn.metrics import confusion_matrix


def compute_group_fairness(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    group_labels: Sequence[str],
) -> pd.DataFrame:
    """Return fairness metrics by protected group for a binary prediction task."""
    df = pd.DataFrame({"y_true": y_true, "y_pred": y_pred, "group": group_labels})
    metrics: list[dict] = []

    for group_name, group_df in df.groupby("group"):
        true_labels = group_df["y_true"].to_numpy()
        pred_labels = group_df["y_pred"].to_numpy()

        tn, fp, fn, tp = confusion_matrix(true_labels, pred_labels, labels=[0, 1]).ravel()

        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        fpr = fp / (fp + tn) if (fp + tn) else 0.0
        fnr = fn / (fn + tp) if (fn + tp) else 0.0
        tpr = tp / (tp + fn) if (tp + fn) else 0.0
        selection_rate = (pred_labels == 1).mean()

        metrics.append(
            {
                "group": group_name,
                "precision": float(precision),
                "recall": float(recall),
                "false_positive_rate": float(fpr),
                "false_negative_rate": float(fnr),
                "true_positive_rate": float(tpr),
                "selection_rate": float(selection_rate),
                "support": int(len(group_df)),
            }
        )

    return pd.DataFrame(metrics)
