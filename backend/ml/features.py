"""
Feature Engineering for Business Entity Resolution.
Transforms a pair of candidate records into a numerical feature vector for ML modeling.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

from backend.config import FEATURE_COLUMNS
from backend.matching.fuzzy_matching import compute_record_similarities
from backend.matching.exact_matching import check_exact_matches

def extract_pairwise_features(rec1: Dict[str, Any], rec2: Dict[str, Any]) -> Dict[str, float]:
    """
    Extracts all numerical features for a single candidate record pair.
    """
    fuzzy_sims = compute_record_similarities(rec1, rec2)
    exact_flags = check_exact_matches(rec1, rec2)
    
    features = {
        "name_token_sort_ratio": fuzzy_sims["name_token_sort_ratio"],
        "name_token_set_ratio": fuzzy_sims["name_token_set_ratio"],
        "name_levenshtein_ratio": fuzzy_sims["name_levenshtein_ratio"],
        "address_similarity": fuzzy_sims["address_similarity"],
        "city_similarity": fuzzy_sims["city_similarity"],
        "state_match": fuzzy_sims["state_match"],
        "country_match": fuzzy_sims["country_match"],
        "phone_similarity": fuzzy_sims["phone_similarity"],
        "email_similarity": fuzzy_sims["email_similarity"],
        "website_similarity": fuzzy_sims["website_similarity"],
        "exact_name_match": 1.0 if exact_flags["exact_name_match"] else 0.0,
        "exact_phone_match": 1.0 if exact_flags["exact_phone_match"] else 0.0,
        "exact_email_match": 1.0 if exact_flags["exact_email_match"] else 0.0,
        "exact_website_match": 1.0 if exact_flags["exact_website_match"] else 0.0,
        "exact_city_name_match": 1.0 if exact_flags["exact_city_name_match"] else 0.0,
    }
    return features

def build_feature_dataframe(pairs: List[tuple]) -> pd.DataFrame:
    """
    Builds a DataFrame of feature vectors for a list of (rec1, rec2) tuples.
    """
    rows = []
    for r1, r2 in pairs:
        feats = extract_pairwise_features(r1, r2)
        feats["record_id_1"] = r1.get("source_record_id")
        feats["record_id_2"] = r2.get("source_record_id")
        rows.append(feats)
        
    return pd.DataFrame(rows)
