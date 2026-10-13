"""
Unit Tests for Matching, Blocking, Scoring, and Clustering Modules.
"""

import pytest
from backend.preprocessing.normalization import normalize_record
from backend.matching.exact_matching import check_exact_matches
from backend.matching.fuzzy_matching import calculate_string_similarity, compute_record_similarities
from backend.matching.blocking import generate_blocking_keys, get_candidate_pairs
from backend.matching.scoring import compute_heuristic_score, get_confidence_tier
from backend.matching.clustering import DisjointSetUnion, cluster_and_canonicalize_entities

def test_exact_matching():
    r1 = normalize_record({
        "source_record_id": "S1_001",
        "business_name": "Apex Tech Solutions Pvt Ltd",
        "phone": "415-123-4567",
        "email": "contact@apex.com",
        "website": "https://apex.com",
        "city": "San Francisco"
    })
    r2 = normalize_record({
        "source_record_id": "S2_001",
        "business_name": "Apex Tech Solutions Private Limited",
        "phone": "+1 415 123 4567",
        "email": "contact@apex.com",
        "website": "http://www.apex.com",
        "city": "San Francisco"
    })
    exact = check_exact_matches(r1, r2)
    assert exact["exact_phone_match"] is True
    assert exact["exact_email_match"] is True
    assert exact["exact_website_match"] is True
    assert exact["exact_city_name_match"] is True
    assert exact["has_strong_exact_match"] is True

def test_fuzzy_matching_similarities():
    score_typo = calculate_string_similarity("Apex Technologies", "Apex Technlogies", method="token_sort")
    assert score_typo >= 0.90
    
    score_abbrev = calculate_string_similarity("Private Limited", "Pvt Ltd", method="token_set")
    assert score_abbrev >= 0.50

def test_blocking_keys():
    rec = normalize_record({
        "source_record_id": "S1_001",
        "business_name": "Apex Technology Solutions",
        "city": "San Francisco",
        "country": "USA",
        "email": "contact@apextech.com",
        "phone": "(415) 123-4567"
    })
    keys = generate_blocking_keys(rec)
    assert any("name_pfx:ape" in k for k in keys)
    assert any("domain:apextech.com" in k for k in keys)
    assert any("geo:san francisco_usa" in k for k in keys)

def test_disjoint_set_union():
    elements = ["A", "B", "C", "D", "E"]
    dsu = DisjointSetUnion(elements)
    dsu.union("A", "B")
    dsu.union("B", "C")
    dsu.union("D", "E")
    
    assert dsu.find("A") == dsu.find("C")
    assert dsu.find("D") == dsu.find("E")
    assert dsu.find("A") != dsu.find("D")

def test_canonical_clustering():
    r1 = normalize_record({
        "source_record_id": "S1_01",
        "business_name": "Beacon Financial Advisory Inc.",
        "address": "100 Broadway, Ste 200",
        "city": "New York",
        "phone": "212-555-0199",
        "email": "contact@beaconfa.com",
        "website": "https://www.beaconfa.com"
    })
    r2 = normalize_record({
        "source_record_id": "S2_01",
        "business_name": "beacon financial advisory",
        "address": "100 broadway # 200",
        "city": "New York",
        "phone": "+1 212 555 0199",
        "email": "info@BEACONFA.COM",
        "website": "http://beaconfa.com"
    })
    matched_pairs = [{
        "record_id_1": "S1_01",
        "record_id_2": "S2_01",
        "confidence_score": 98.5,
        "is_match": True
    }]
    entities = cluster_and_canonicalize_entities([r1, r2], matched_pairs)
    assert len(entities) == 1
    ent = entities[0]
    assert ent["records_count"] == 2
    assert ent["duplicate_count"] == 1
    assert "Beacon Financial Advisory" in ent["canonical_name"]
