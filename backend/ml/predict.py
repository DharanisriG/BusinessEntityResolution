"""
ML Prediction Module for Business Entity Resolution.
Loads trained model and generates match probabilities and confidence scores for candidate pairs.
"""

import os
from typing import Dict, Any, List, Optional
import numpy as np
import joblib

from backend.config import MODEL_PATH, FEATURE_COLUMNS, DEFAULT_MATCH_THRESHOLD
from backend.matching.scoring import compute_heuristic_score, generate_match_evidence
from backend.ml.features import extract_pairwise_features

_CACHED_MODEL = None

def get_ml_model():
    """
    Loads and caches the trained RandomForest model.
    """
    global _CACHED_MODEL
    if _CACHED_MODEL is None and MODEL_PATH.exists():
        try:
            _CACHED_MODEL = joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"Warning: Could not load ML model from {MODEL_PATH}: {e}")
            _CACHED_MODEL = None
    return _CACHED_MODEL

def predict_pair_match(rec1: Dict[str, Any], rec2: Dict[str, Any], custom_threshold: Optional[float] = None) -> Dict[str, Any]:
    """
    Scores a pair of records using ML model with heuristic calibration.
    Returns full explainability details, confidence score (0-100), and match flag.
    """
    features = extract_pairwise_features(rec1, rec2)
    model = get_ml_model()
    
    threshold = custom_threshold if custom_threshold is not None else DEFAULT_MATCH_THRESHOLD
    
    if model is not None:
        try:
            feat_vector = np.array([[features[col] for col in FEATURE_COLUMNS]])
            # Probability of match (class 1)
            probs = model.predict_proba(feat_vector)[0]
            ml_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
            ml_score = ml_prob * 100.0
            
            # Combine ML score with heuristic safeguard
            heuristic_score = compute_heuristic_score(features)
            # Balanced score: 70% ML, 30% rule-based
            combined_score = round(0.70 * ml_score + 0.30 * heuristic_score, 2)
            
            # Boost for exact signals
            if features.get("exact_phone_match") == 1.0 or features.get("exact_email_match") == 1.0:
                combined_score = max(combined_score, 90.0)
        except Exception as e:
            combined_score = compute_heuristic_score(features)
    else:
        combined_score = compute_heuristic_score(features)
        
    evidence = generate_match_evidence(rec1, rec2, features, combined_score)
    evidence["is_match"] = bool(combined_score >= threshold)
    evidence["record_id_1"] = rec1.get("source_record_id")
    evidence["record_id_2"] = rec2.get("source_record_id")
    evidence["source_1"] = rec1.get("source", "Source1")
    evidence["source_2"] = rec2.get("source", "Source2")
    evidence["business_name_1"] = rec1.get("business_name", "")
    evidence["business_name_2"] = rec2.get("business_name", "")
    
    return evidence
