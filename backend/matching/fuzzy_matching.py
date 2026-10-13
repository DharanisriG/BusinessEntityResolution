"""
Fuzzy Matching Module for Business Entity Resolution using RapidFuzz.
Calculates normalized similarity scores (0.0 to 1.0) across all record attributes.
"""

from typing import Dict, Any
from rapidfuzz import fuzz
from backend.preprocessing.cleaning import clean_missing_value

def calculate_string_similarity(str1: str, str2: str, method: str = "token_sort") -> float:
    """
    Computes normalized similarity between two strings (0.0 to 1.0).
    Handles missing/empty strings safely by returning 0.0.
    """
    s1 = clean_missing_value(str1)
    s2 = clean_missing_value(str2)
    
    if not s1 or not s2:
        return 0.0
    
    if s1 == s2:
        return 1.0
        
    if method == "token_sort":
        score = fuzz.token_sort_ratio(s1, s2)
    elif method == "token_set":
        score = fuzz.token_set_ratio(s1, s2)
    elif method == "partial":
        score = fuzz.partial_ratio(s1, s2)
    elif method == "ratio":
        score = fuzz.ratio(s1, s2)
    else:
        score = fuzz.token_sort_ratio(s1, s2)
        
    return round(float(score) / 100.0, 4)

def compute_record_similarities(rec1: Dict[str, Any], rec2: Dict[str, Any]) -> Dict[str, float]:
    """
    Computes all fuzzy similarity metrics between two normalized records.
    Returns a dictionary of normalized similarity scores in [0.0, 1.0].
    """
    # Business name similarities
    name1 = rec1.get("norm_name", "") or rec1.get("business_name", "")
    name2 = rec2.get("norm_name", "") or rec2.get("business_name", "")
    
    name_sort_ratio = calculate_string_similarity(name1, name2, method="token_sort")
    name_set_ratio = calculate_string_similarity(name1, name2, method="token_set")
    name_levenshtein = calculate_string_similarity(name1, name2, method="ratio")
    
    # Address similarity (token_set_ratio handles extra words like 'Suite 200' effectively)
    addr1 = rec1.get("norm_address", "") or rec1.get("address", "")
    addr2 = rec2.get("norm_address", "") or rec2.get("address", "")
    addr_similarity = calculate_string_similarity(addr1, addr2, method="token_set")
    
    # City, State, Country similarities
    city1 = rec1.get("norm_city", "") or rec1.get("city", "")
    city2 = rec2.get("norm_city", "") or rec2.get("city", "")
    city_similarity = calculate_string_similarity(city1, city2, method="ratio")
    
    state1 = rec1.get("norm_state", "") or rec1.get("state", "")
    state2 = rec2.get("norm_state", "") or rec2.get("state", "")
    state_match = 1.0 if (state1 and state2 and state1 == state2) else (0.0 if (state1 and state2) else 0.5)
    
    cntry1 = rec1.get("norm_country", "") or rec1.get("country", "")
    cntry2 = rec2.get("norm_country", "") or rec2.get("country", "")
    country_match = 1.0 if (cntry1 and cntry2 and cntry1 == cntry2) else (0.0 if (cntry1 and cntry2) else 0.5)
    
    # Phone similarity (normalized digits)
    phone1 = rec1.get("norm_phone", "")
    phone2 = rec2.get("norm_phone", "")
    if phone1 and phone2:
        if phone1 == phone2:
            phone_similarity = 1.0
        elif phone1[-7:] == phone2[-7:]:  # Suffix 7-digit match
            phone_similarity = 0.9
        else:
            phone_similarity = calculate_string_similarity(phone1, phone2, method="ratio")
    else:
        phone_similarity = 0.0
        
    # Email similarity
    email1 = rec1.get("norm_email", "")
    email2 = rec2.get("norm_email", "")
    dom1 = rec1.get("email_domain", "")
    dom2 = rec2.get("email_domain", "")
    
    if email1 and email2:
        if email1 == email2:
            email_similarity = 1.0
        elif dom1 and dom2 and dom1 == dom2:
            email_similarity = 0.85
        else:
            email_similarity = calculate_string_similarity(email1, email2, method="ratio")
    elif dom1 and dom2 and dom1 == dom2:
        email_similarity = 0.8
    else:
        email_similarity = 0.0
        
    # Website similarity
    web1 = rec1.get("norm_website", "")
    web2 = rec2.get("norm_website", "")
    wdom1 = rec1.get("web_domain", "")
    wdom2 = rec2.get("web_domain", "")
    
    if web1 and web2:
        if web1 == web2:
            website_similarity = 1.0
        elif wdom1 and wdom2 and wdom1 == wdom2:
            website_similarity = 0.9
        else:
            website_similarity = calculate_string_similarity(web1, web2, method="ratio")
    elif wdom1 and wdom2 and wdom1 == wdom2:
        website_similarity = 0.85
    else:
        website_similarity = 0.0

    return {
        "name_token_sort_ratio": name_sort_ratio,
        "name_token_set_ratio": name_set_ratio,
        "name_levenshtein_ratio": name_levenshtein,
        "address_similarity": addr_similarity,
        "city_similarity": city_similarity,
        "state_match": state_match,
        "country_match": country_match,
        "phone_similarity": phone_similarity,
        "email_similarity": email_similarity,
        "website_similarity": website_similarity
    }
