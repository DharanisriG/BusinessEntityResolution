"""
Matching and Confidence Scoring Module.
Combines exact matches, fuzzy similarities, and ML predictions into a 0-100 confidence score
with full explainability evidence.
"""

from typing import Dict, Any, Tuple
from backend.config import CONFIDENCE_TIERS, DEFAULT_MATCH_THRESHOLD

def get_confidence_tier(score: float) -> Dict[str, str]:
    """
    Returns the confidence tier label and resolution status for a 0-100 score.
    """
    for key, tier in CONFIDENCE_TIERS.items():
        if score >= tier["min"] and score <= tier["max"]:
            return {
                "tier_key": key,
                "label": tier["label"],
                "status": tier["status"]
            }
    if score > 100.0:
        return {"tier_key": "VERY_HIGH", "label": "Very High Confidence", "status": "Match"}
    return {"tier_key": "UNLIKELY", "label": "Unlikely Match", "status": "Non-Match"}

def compute_heuristic_score(features: Dict[str, float]) -> float:
    """
    Weighted heuristic score calculator (0.0 to 100.0) based on domain rules.
    Used for calibration and as fallback if ML model is absent.
    """
    # Base weights
    weights = {
        "name_token_sort_ratio": 0.35,
        "name_token_set_ratio": 0.10,
        "address_similarity": 0.15,
        "city_similarity": 0.08,
        "phone_similarity": 0.12,
        "email_similarity": 0.10,
        "website_similarity": 0.10
    }
    
    score = sum(features.get(k, 0.0) * w for k, w in weights.items()) * 100.0
    
    # Bonuses for strong exact matches
    if features.get("exact_phone_match", 0.0) == 1.0 and features.get("name_token_sort_ratio", 0.0) >= 0.6:
        score = max(score, 92.0)
    if features.get("exact_email_match", 0.0) == 1.0 and features.get("name_token_sort_ratio", 0.0) >= 0.5:
        score = max(score, 94.0)
    if features.get("exact_website_match", 0.0) == 1.0 and features.get("name_token_sort_ratio", 0.0) >= 0.7:
        score = max(score, 93.0)
    if features.get("exact_city_name_match", 0.0) == 1.0:
        score = max(score, 96.0)
        
    return min(100.0, max(0.0, round(score, 2)))

def generate_match_evidence(rec1: Dict[str, Any], rec2: Dict[str, Any], features: Dict[str, float], final_score: float) -> Dict[str, Any]:
    """
    Produces structured, human-readable explainability evidence.
    """
    tier = get_confidence_tier(final_score)
    is_match = final_score >= DEFAULT_MATCH_THRESHOLD
    
    evidence_points = []
    if features.get("name_token_sort_ratio", 0.0) >= 0.8:
        evidence_points.append(f"High business name similarity ({int(features['name_token_sort_ratio']*100)}%)")
    elif features.get("name_token_sort_ratio", 0.0) >= 0.6:
        evidence_points.append(f"Moderate business name similarity ({int(features['name_token_sort_ratio']*100)}%)")
    
    if features.get("exact_phone_match", 0.0) == 1.0:
        evidence_points.append("Identical normalized phone number")
    elif features.get("phone_similarity", 0.0) >= 0.8:
        evidence_points.append("Matching phone number suffix")
        
    if features.get("exact_email_match", 0.0) == 1.0:
        evidence_points.append("Identical contact email")
    elif features.get("email_similarity", 0.0) >= 0.8:
        evidence_points.append("Matching company email domain")
        
    if features.get("exact_website_match", 0.0) == 1.0:
        evidence_points.append("Matching official website / web domain")
        
    if features.get("city_similarity", 0.0) >= 0.9 and features.get("country_match", 0.0) == 1.0:
        evidence_points.append(f"Co-located in the same city ({rec1.get('city') or rec2.get('city')})")

    return {
        "confidence_score": final_score,
        "tier": tier["label"],
        "status": tier["status"],
        "is_match": is_match,
        "similarity_breakdown": {
            "business_name_similarity": round(features.get("name_token_sort_ratio", 0.0) * 100, 1),
            "address_similarity": round(features.get("address_similarity", 0.0) * 100, 1),
            "city_similarity": round(features.get("city_similarity", 0.0) * 100, 1),
            "phone_similarity": round(features.get("phone_similarity", 0.0) * 100, 1),
            "email_similarity": round(features.get("email_similarity", 0.0) * 100, 1),
            "website_similarity": round(features.get("website_similarity", 0.0) * 100, 1),
            "country_match": bool(features.get("country_match", 0.0) == 1.0),
            "exact_phone_match": bool(features.get("exact_phone_match", 0.0) == 1.0),
            "exact_email_match": bool(features.get("exact_email_match", 0.0) == 1.0),
            "exact_website_match": bool(features.get("exact_website_match", 0.0) == 1.0)
        },
        "evidence_summary": evidence_points if evidence_points else ["Low attribute similarity across all fields"]
    }
