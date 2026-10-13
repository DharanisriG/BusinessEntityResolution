"""
Machine Learning Training Pipeline for Business Entity Resolution.
Trains a RandomForestClassifier on ground-truth pairwise features and saves model artifacts.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root to sys.path for direct script execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.model_selection import cross_val_score, StratifiedKFold
import joblib

from backend.config import TRAIN_DIR, MODELS_DIR, MODEL_PATH, METADATA_PATH, FEATURE_COLUMNS

from backend.utils.data_loader import load_and_normalize_dataset, load_table_file
from backend.ml.features import extract_pairwise_features

def train_entity_resolution_model(train_dir: Path = TRAIN_DIR) -> dict:
    """
    Trains and persists the entity resolution ML model using ground-truth data.
    """
    print(f"Loading training data from: {train_dir}")
    train_dir = Path(train_dir)
    
    # 1. Load normalized records
    records, sources = load_and_normalize_dataset(train_dir, prefix="train")
    rec_by_id = {r["source_record_id"]: r for r in records}
    print(f"Loaded {len(records)} records from {len(sources)} sources.")
    
    # 2. Load ground truth
    gt_path = train_dir / "train_ground_truth.tsv"
    if not gt_path.exists():
        raise FileNotFoundError(f"Ground truth file not found at: {gt_path}")
        
    gt_df = pd.read_csv(gt_path, sep="\t", dtype=str)
    print(f"Loaded {len(gt_df)} ground truth pairs.")
    
    # 3. Extract pairwise feature vectors
    X_rows = []
    y_labels = []
    
    for _, row in gt_df.iterrows():
        r1_id = row["record_id_1"]
        r2_id = row["record_id_2"]
        label = int(row["is_match"])
        
        if r1_id in rec_by_id and r2_id in rec_by_id:
            feats = extract_pairwise_features(rec_by_id[r1_id], rec_by_id[r2_id])
            vector = [feats[col] for col in FEATURE_COLUMNS]
            X_rows.append(vector)
            y_labels.append(label)
            
    X = np.array(X_rows)
    y = np.array(y_labels)
    
    print(f"Extracted features for {len(X)} pairs. Positive class: {sum(y)}, Negative class: {len(y) - sum(y)}")
    
    # 4. Train Random Forest model
    clf = RandomForestClassifier(
        n_estimators=120,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        class_weight="balanced"
    )
    
    # Stratified K-Fold Cross Validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_f1_scores = cross_val_score(clf, X, y, cv=cv, scoring="f1")
    cv_acc_scores = cross_val_score(clf, X, y, cv=cv, scoring="accuracy")
    
    print(f"5-Fold CV F1: {np.mean(cv_f1_scores):.4f} (+/- {np.std(cv_f1_scores):.4f})")
    print(f"5-Fold CV Accuracy: {np.mean(cv_acc_scores):.4f} (+/- {np.std(cv_acc_scores):.4f})")
    
    # Fit on all training data
    clf.fit(X, y)
    y_pred = clf.predict(X)
    
    acc = float(accuracy_score(y, y_pred))
    prec = float(precision_score(y, y_pred, zero_division=0))
    rec = float(recall_score(y, y_pred, zero_division=0))
    f1 = float(f1_score(y, y_pred, zero_division=0))
    cm = confusion_matrix(y, y_pred).tolist() # [[TN, FP], [FN, TP]]
    
    # Feature importances
    importances = {
        col: round(float(imp), 4) 
        for col, imp in zip(FEATURE_COLUMNS, clf.feature_importances_)
    }
    sorted_importances = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))
    
    # 5. Save model and metadata
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved to: {MODEL_PATH}")
    
    metadata = {
        "model_type": "RandomForestClassifier",
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "training_samples": len(X),
        "positive_pairs": int(sum(y)),
        "negative_pairs": int(len(y) - sum(y)),
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "cv_f1_mean": round(float(np.mean(cv_f1_scores)), 4),
            "cv_accuracy_mean": round(float(np.mean(cv_acc_scores)), 4),
            "confusion_matrix": {
                "true_negatives": cm[0][0],
                "false_positives": cm[0][1],
                "false_negatives": cm[1][0],
                "true_positives": cm[1][1]
            }
        },
        "feature_importances": sorted_importances,
        "feature_columns": FEATURE_COLUMNS
    }
    
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to: {METADATA_PATH}")
    
    return metadata

if __name__ == "__main__":
    train_entity_resolution_model()
