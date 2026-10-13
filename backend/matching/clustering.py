"""
Entity Clustering and Canonical Representation Module.
Groups matched pairwise records into resolved business entities using Connected Components
and constructs the most complete, high-quality Canonical Entity profile.
"""

from collections import defaultdict
from typing import List, Dict, Any, Set, Tuple
import numpy as np

class DisjointSetUnion:
    """Disjoint Set Union (Union-Find) with path compression and rank heuristic."""
    def __init__(self, elements: List[str]):
        self.parent = {e: e for e in elements}
        self.rank = {e: 0 for e in elements}
        
    def find(self, item: str) -> str:
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]
        
    def union(self, item1: str, item2: str):
        root1 = self.find(item1)
        root2 = self.find(item2)
        if root1 != root2:
            if self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            elif self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1

def select_best_canonical_value(values: List[str], field_type: str = "text") -> str:
    """
    Selects the most complete, clean, and representative value from a list of candidates.
    """
    # Filter non-empty
    valid = [v.strip() for v in values if v and v.strip() and v.strip().lower() not in {"nan", "null", "none"}]
    if not valid:
        return ""
    
    if field_type == "name":
        # Prefer title cased, longest informative name
        def name_quality(n):
            score = len(n)
            if any(c.isupper() for c in n) and any(c.islower() for c in n):
                score += 10 # Title/mixed case
            if "Private Limited" in n or "Corporation" in n or "Technologies" in n:
                score += 15 # Full formal expansion
            return score
        return max(valid, key=name_quality)
        
    elif field_type == "email":
        # Prefer lowercase standard contact/info email
        return min(valid, key=lambda x: (0 if "contact@" in x.lower() or "info@" in x.lower() else 1, len(x)))
        
    elif field_type == "website":
        # Prefer https with www
        def web_quality(w):
            score = len(w)
            if w.startswith("https://"):
                score += 20
            if "www." in w:
                score += 10
            return score
        return max(valid, key=web_quality)
        
    elif field_type == "phone":
        # Prefer standard international formatted with +
        return max(valid, key=lambda x: (1 if "+" in x else 0, len(x)))
        
    elif field_type == "address":
        # Prefer longest, most descriptive address with Suite/Road expanded
        return max(valid, key=len)
        
    else:
        # Most frequent or longest
        return max(valid, key=lambda v: (valid.count(v), len(v)))

def cluster_and_canonicalize_entities(
    records: List[Dict[str, Any]], 
    matched_pairs: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Clusters records into unique business entities and generates canonical representations.
    """
    rec_by_id = {r["source_record_id"]: r for r in records}
    record_ids = list(rec_by_id.keys())
    
    # 1. Group records via DSU
    dsu = DisjointSetUnion(record_ids)
    
    # Track confidence scores per pair
    pair_scores = {}
    for pair in matched_pairs:
        if pair.get("is_match", False):
            r1_id = pair["record_id_1"]
            r2_id = pair["record_id_2"]
            if r1_id in rec_by_id and r2_id in rec_by_id:
                dsu.union(r1_id, r2_id)
                pair_key = (min(r1_id, r2_id), max(r1_id, r2_id))
                pair_scores[pair_key] = pair.get("confidence_score", 0.0)

    # 2. Collect clusters
    clusters_map = defaultdict(list)
    for rid in record_ids:
        root = dsu.find(rid)
        clusters_map[root].append(rec_by_id[rid])

    # 3. Build Canonical Entities
    canonical_entities = []
    # Sort clusters by size descending, then by name
    sorted_cluster_roots = sorted(clusters_map.keys(), key=lambda root: len(clusters_map[root]), reverse=True)
    
    for idx, root in enumerate(sorted_cluster_roots, 1):
        cluster_records = clusters_map[root]
        ent_id = f"ENT{idx:04d}"
        
        # Collect candidate values for each attribute
        names = [r.get("business_name", "") for r in cluster_records]
        addresses = [r.get("address", "") for r in cluster_records]
        cities = [r.get("city", "") for r in cluster_records]
        states = [r.get("state", "") for r in cluster_records]
        countries = [r.get("country", "") for r in cluster_records]
        phones = [r.get("phone", "") for r in cluster_records]
        emails = [r.get("email", "") for r in cluster_records]
        websites = [r.get("website", "") for r in cluster_records]
        sources = list(set([r.get("source", "Unknown") for r in cluster_records]))
        
        # Determine average confidence for cluster
        cluster_rids = [r["source_record_id"] for r in cluster_records]
        cluster_confidences = []
        for i in range(len(cluster_rids)):
            for j in range(i + 1, len(cluster_rids)):
                k = (min(cluster_rids[i], cluster_rids[j]), max(cluster_rids[i], cluster_rids[j]))
                if k in pair_scores:
                    cluster_confidences.append(pair_scores[k])
                    
        avg_conf = round(float(np.mean(cluster_confidences)), 1) if cluster_confidences else (100.0 if len(cluster_records) == 1 else 90.0)
        
        canonical_name = select_best_canonical_value(names, "name") or "Unnamed Entity"
        canonical_addr = select_best_canonical_value(addresses, "address")
        canonical_city = select_best_canonical_value(cities, "city")
        canonical_state = select_best_canonical_value(states, "state")
        canonical_country = select_best_canonical_value(countries, "country")
        canonical_phone = select_best_canonical_value(phones, "phone")
        canonical_email = select_best_canonical_value(emails, "email")
        canonical_website = select_best_canonical_value(websites, "website")

        canonical_entities.append({
            "entity_id": ent_id,
            "canonical_name": canonical_name,
            "address": canonical_addr,
            "city": canonical_city,
            "state": canonical_state,
            "country": canonical_country,
            "phone": canonical_phone,
            "email": canonical_email,
            "website": canonical_website,
            "records_count": len(cluster_records),
            "duplicate_count": max(0, len(cluster_records) - 1),
            "sources": sources,
            "confidence": avg_conf,
            "records": cluster_records
        })
        
    return canonical_entities
