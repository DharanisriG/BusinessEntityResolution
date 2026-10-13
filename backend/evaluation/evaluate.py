"""
Evaluation Metrics Module for Business Entity Resolution.
Calculates Accuracy, Precision, Recall, F1-Score, and Confusion Matrix against Ground Truth.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add project root to sys.path for direct script execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from backend.config import TRAIN_DIR, TEST_DIR

from backend.utils.data_loader import load_and_normalize_dataset
from backend.ml.predict import predict_pair_match

def evaluate_resolution_pipeline(
    dataset_dir: Path = TEST_DIR, 
    prefix: str = "test",
    threshold: float = 60.0
) -> Dict[str, Any]:
    """
    Evaluates the full resolution pipeline against ground truth for a given dataset split.
    """
    dataset_dir = Path(dataset_dir)
    gt_file = dataset_dir / f"{prefix}_ground_truth.tsv"
    
    if not gt_file.exists():
        # Fallback to train if test ground truth isn't present
        gt_file = TRAIN_DIR / "train_ground_truth.tsv"
        dataset_dir = TRAIN_DIR
        prefix = "train"
        
    records, _ = load_and_normalize_dataset(dataset_dir, prefix=prefix)
    rec_by_id = {r["source_record_id"]: r for r in records}
    
    gt_df = pd.read_csv(gt_file, sep="\t", dtype=str)
    
    y_true = []
    y_pred = []
    y_scores = []
    
    for _, row in gt_df.iterrows():
        r1_id = row["record_id_1"]
        r2_id = row["record_id_2"]
        label = int(row["is_match"])
        
        if r1_id in rec_by_id and r2_id in rec_by_id:
            pred_res = predict_pair_match(rec_by_id[r1_id], rec_by_id[r2_id], custom_threshold=threshold)
            score = pred_res["confidence_score"]
            pred_match = 1 if score >= threshold else 0
            
            y_true.append(label)
            y_pred.append(pred_match)
            y_scores.append(score)
            
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    cm = confusion_matrix(y_true, y_pred).tolist()
    
    tn, fp = cm[0][0], cm[0][1]
    fn, tp = cm[1][0], cm[1][1]
    
    # Calculate threshold curve for interactive UI
    threshold_analysis = []
    for test_thresh in [30, 40, 50, 60, 70, 80, 90]:
        preds = [1 if s >= test_thresh else 0 for s in y_scores]
        p = precision_score(y_true, preds, zero_division=0)
        r = recall_score(y_true, preds, zero_division=0)
        f = f1_score(y_true, preds, zero_division=0)
        threshold_analysis.append({
            "threshold": test_thresh,
            "precision": round(float(p) * 100, 1),
            "recall": round(float(r) * 100, 1),
            "f1_score": round(float(f) * 100, 1)
        })
        
    return {
        "dataset_evaluated": f"{prefix.upper()} dataset ({len(y_true)} pairs)",
        "threshold_used": threshold,
        "metrics": {
            "accuracy": round(acc * 100, 2),
            "precision": round(prec * 100, 2),
            "recall": round(rec * 100, 2),
            "f1_score": round(f1 * 100, 2),
            "true_positives": int(tp),
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "total_pairs": len(y_true)
        },
        "confusion_matrix": {
            "matrix": [
                [int(tn), int(fp)],
                [int(fn), int(tp)]
            ],
            "labels": ["Non-Match (0)", "Match (1)"]
        },
        "threshold_analysis": threshold_analysis,
        "tradeoff_explanation": "Entity resolution balances Precision (avoiding false merges of distinct businesses) and Recall (avoiding missed duplicates of the same business). Higher thresholds prioritize Precision, while lower thresholds maximize Recall."
    }

if __name__ == "__main__":
    res = evaluate_resolution_pipeline()
    print("Evaluation Results:", res)
