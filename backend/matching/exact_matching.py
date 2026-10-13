"""
Exact Matching Module for Business Entity Resolution.
Checks for exact identity matches on normalized high-precision fields
(e.g. Phone, Email, Domain, Core Business Name + City).
"""

from typing import Dict, Any

def check_exact_matches(rec1: Dict[str, Any], rec2: Dict[str, Any]) -> Dict[str, bool]:
    """
    Evaluates exact match signals between two normalized records.
    Returns boolean flags for each exact field match.
    """
    p1, p2 = rec1.get("norm_phone", ""), rec2.get("norm_phone", "")
    exact_phone = bool(p1 and p2 and p1 == p2)
    
    e1, e2 = rec1.get("norm_email", ""), rec2.get("norm_email", "")
    exact_email = bool(e1 and e2 and e1 == e2)
    
    d1, d2 = rec1.get("web_domain", ""), rec2.get("web_domain", "")
    exact_domain = bool(d1 and d2 and d1 == d2)
    
    w1, w2 = rec1.get("norm_website", ""), rec2.get("norm_website", "")
    exact_website = bool(w1 and w2 and w1 == w2) or exact_domain
    
    n1, n2 = rec1.get("norm_name", ""), rec2.get("norm_name", "")
    exact_name = bool(n1 and n2 and n1 == n2)
    
    c1, c2 = rec1.get("norm_city", ""), rec2.get("norm_city", "")
    exact_city = bool(c1 and c2 and c1 == c2)
    
    exact_city_name = bool(exact_name and exact_city)
    
    # Core name match (without legal suffixes)
    cn1, cn2 = rec1.get("core_name", ""), rec2.get("core_name", "")
    exact_core_name = bool(cn1 and cn2 and cn1 == cn2)

    return {
        "exact_phone_match": exact_phone,
        "exact_email_match": exact_email,
        "exact_website_match": exact_website,
        "exact_name_match": exact_name,
        "exact_core_name_match": exact_core_name,
        "exact_city_match": exact_city,
        "exact_city_name_match": exact_city_name,
        "has_strong_exact_match": bool(exact_phone or exact_email or exact_domain or exact_city_name)
    }
