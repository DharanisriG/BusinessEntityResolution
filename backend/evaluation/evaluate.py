import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from backend.config import TRAIN_DIR, TEST_DIR
from backend.utils.data_loader import load_and_normalize_dataset
from backend.ml.predict import predict_pair_match


def evaluate_resolution_pipeline(
    dataset_dir: Path = TEST_DIR,
    prefix: str = "test",
    threshold: float = 60.0,
) -> Dict[str, Any]:
    """Evaluate entity-resolution predictions against ground truth."""

    dataset_dir = Path(dataset_dir)
    gt_file = dataset_dir / f"{prefix}_ground_truth.tsv"

    if not gt_file.exists():
        gt_file = TRAIN_DIR / "train_ground_truth.tsv"
        dataset_dir = TRAIN_DIR
        prefix = "train"

    if not gt_file.exists():
        raise FileNotFoundError(
            f"Ground-truth file not found: {gt_file}"
        )

    records, _ = load_and_normalize_dataset(
        dataset_dir, prefix=prefix
    )
    rec_by_id = {
        record["source_record_id"]: record
        for record in records
    }

    gt_df = pd.read_csv(gt_file, sep="\t", dtype=str)

    required_columns = {
        "record_id_1",
        "record_id_2",
        "is_match",
    }

    missing_columns = required_columns - set(gt_df.columns)
    if missing_columns:
        raise ValueError(
            f"Ground-truth file is missing columns: "
            f"{', '.join(sorted(missing_columns))}"
        )

    y_true = []
    y_pred = []
    y_scores = []

    for _, row in gt_df.iterrows():
        try:
            label = int(row["is_match"])
        except (ValueError, TypeError):
            raise ValueError(
                "Ground-truth labels must be binary (0 or 1)."
            )

        if label not in (0, 1):
            raise ValueError(
                "Ground-truth labels must be binary (0 or 1)."
            )

        r1_id = row["record_id_1"]
        r2_id = row["record_id_2"]

        if r1_id not in rec_by_id or r2_id not in rec_by_id:
            continue

        prediction = predict_pair_match(
            rec_by_id[r1_id],
            rec_by_id[r2_id],
            custom_threshold=threshold,
        )

        score = float(prediction["confidence_score"])
        predicted_label = int(score >= threshold)

        y_true.append(label)
        y_pred.append(predicted_label)
        y_scores.append(score)

    if not y_true:
        raise ValueError(
            "No valid ground-truth pairs found for evaluation."
        )

    y_true = np.array(y_true, dtype=int)
    y_pred = np.array(y_pred, dtype=int)

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(
        y_true, y_pred, zero_division=0
    )
    recall = recall_score(
        y_true, y_pred, zero_division=0
    )
    f1 = f1_score(y_true, y_pred, zero_division=0)

    cm = confusion_matrix(
        y_true, y_pred, labels=[0, 1]
    ).tolist()

    tn, fp = cm[0]
    fn, tp = cm[1]

    threshold_analysis = []

    for test_threshold in [30, 40, 50, 60, 70, 80, 90]:
        predictions = [
            int(score >= test_threshold)
            for score in y_scores
        ]

        threshold_analysis.append({
            "threshold": test_threshold,
            "precision": round(
                precision_score(
                    y_true, predictions, zero_division=0
                ) * 100, 1
            ),
            "recall": round(
                recall_score(
                    y_true, predictions, zero_division=0
                ) * 100, 1
            ),
            "f1_score": round(
                f1_score(
                    y_true, predictions, zero_division=0
                ) * 100, 1
            ),
        })

    return {
        "dataset_evaluated": (
            f"{prefix.upper()} dataset ({len(y_true)} pairs)"
        ),
        "threshold_used": threshold,
        "metrics": {
            "accuracy": round(accuracy * 100, 2),
            "precision": round(precision * 100, 2),
            "recall": round(recall * 100, 2),
            "f1_score": round(f1 * 100, 2),
            "true_positives": int(tp),
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "total_pairs": len(y_true),
        },
        "confusion_matrix": {
            "matrix": [
                [int(tn), int(fp)],
                [int(fn), int(tp)],
            ],
            "labels": ["Non-Match (0)", "Match (1)"],
        },
        "threshold_analysis": threshold_analysis,
        "tradeoff_explanation": (
            "Entity resolution balances Precision (avoiding false "
            "merges of distinct businesses) and Recall (avoiding "
            "missed duplicates of the same business). Higher "
            "thresholds generally prioritize Precision, while "
            "lower thresholds generally increase Recall."
        ),
    }


if __name__ == "__main__":
    result = evaluate_resolution_pipeline()
    print("Evaluation Results:", result)