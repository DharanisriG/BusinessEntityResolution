"""
Blocking Module for Business Entity Resolution.
Reduces pairwise comparison space from O(N^2) to candidate pairs using multiple indexing keys.
"""

from collections import defaultdict
from typing import List, Dict, Any, Set, Tuple

def generate_blocking_keys(record: Dict[str, Any]) -> List[str]:
    """
    Generates indexing keys for a record across diverse blocking strategies:
    1. First 3 characters of core business name
    2. First word of normalized business name
    3. City + Country
    4. Email domain
    5. Phone suffix (last 7 digits)
    """
    keys = []
    
    # Strategy 1: Core name prefix (3 chars)
    core = record.get("core_name", "") or record.get("norm_name", "")
    if core and len(core) >= 3:
        keys.append(f"name_pfx:{core[:3].lower()}")
        
    # Strategy 2: First word of name
    tokens = core.split()
    if tokens:
        keys.append(f"first_word:{tokens[0].lower()}")
        
    # Strategy 3: City + Country
    city = record.get("norm_city", "")
    country = record.get("norm_country", "")
    if city and country:
        keys.append(f"geo:{city}_{country}")
    elif city:
        keys.append(f"city:{city}")
        
    # Strategy 4: Email domain
    domain = record.get("email_domain", "") or record.get("web_domain", "")
    if domain and domain not in {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com"}:
        keys.append(f"domain:{domain}")
        
    # Strategy 5: Phone suffix (last 7 digits)
    phone = record.get("norm_phone", "")
    if phone and len(phone) >= 7:
        keys.append(f"phone_sfx:{phone[-7:]}")
        
    return keys

def get_candidate_pairs(records: List[Dict[str, Any]], use_blocking: bool = True) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
    """
    Generates unique candidate pairs for comparison.
    If use_blocking is True, groups records using multi-strategy blocking keys.
    If use_blocking is False, evaluates all cross-source pairs.
    """
    n = len(records)
    if n <= 1:
        return []

    # Map record_id to record
    rec_by_id = {r.get("source_record_id", str(i)): r for i, r in enumerate(records)}
    record_ids = list(rec_by_id.keys())
    
    candidate_id_pairs: Set[Tuple[str, str]] = set()

    if use_blocking:
        # Multi-index blocking
        blocks = defaultdict(list)
        for r in records:
            rid = r.get("source_record_id")
            for key in generate_blocking_keys(r):
                blocks[key].append(rid)
                
        for key, rids in blocks.items():
            # If block has at least 2 records and is not an overly broad global bucket (> 70% of total)
            if 1 < len(rids) < max(10, int(n * 0.7)):
                for i in range(len(rids)):
                    for j in range(i + 1, len(rids)):
                        r1_id = rids[i]
                        r2_id = rids[j]
                        s1 = rec_by_id[r1_id].get("source", r1_id[:2])
                        s2 = rec_by_id[r2_id].get("source", r2_id[:2])
                        if s1 != s2 or not s1:
                            pair = (min(r1_id, r2_id), max(r1_id, r2_id))
                            candidate_id_pairs.add(pair)
    else:
        for i in range(n):
            for j in range(i + 1, n):
                r1_id = record_ids[i]
                r2_id = record_ids[j]
                s1 = rec_by_id[r1_id].get("source", r1_id[:2])
                s2 = rec_by_id[r2_id].get("source", r2_id[:2])
                if s1 != s2 or not s1:
                    pair = (min(r1_id, r2_id), max(r1_id, r2_id))
                    candidate_id_pairs.add(pair)

    return [(rec_by_id[p[0]], rec_by_id[p[1]]) for p in candidate_id_pairs]

