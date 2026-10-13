"""
Unit Tests for FastAPI REST Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    assert "<!DOCTYPE html>" in res.text or "Business Entity Resolution" in res.text


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "model_loaded" in data

def test_statistics_endpoint():
    res = client.get("/statistics")
    assert res.status_code == 200
    data = res.json()
    assert data["total_records"] > 0
    assert data["unique_entities"] > 0
    assert "records_per_source" in data
    assert "confidence_distribution" in data

def test_entities_endpoint():
    res = client.get("/entities?page=1&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "entities" in data
    assert len(data["entities"]) > 0
    
    first_ent = data["entities"][0]
    ent_id = first_ent["entity_id"]
    
    # Test single entity lookup
    res_single = client.get(f"/entities/{ent_id}")
    assert res_single.status_code == 200
    assert res_single.json()["entity_id"] == ent_id

def test_results_endpoint():
    res = client.get("/results?page=1&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    if data["results"]:
        first = data["results"][0]
        assert "confidence_score" in first
        assert "similarity_breakdown" in first
        assert "evidence_summary" in first

def test_evaluation_endpoint():
    res = client.get("/evaluation?dataset=test&threshold=60")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert data["metrics"]["accuracy"] > 90
    assert "confusion_matrix" in data

def test_upload_endpoint():
    tsv_content1 = (
        "source_record_id\tbusiness_name\taddress\tcity\tstate\tcountry\tphone\temail\twebsite\n"
        "UP_01\tTest Acme Corp\t123 Test St\tAustin\tTX\tUSA\t512-555-0100\tinfo@testacme.com\thttps://testacme.com\n"
    )
    tsv_content2 = (
        "source_record_id\tbusiness_name\taddress\tcity\tstate\tcountry\tphone\temail\twebsite\n"
        "UP_02\tTest Acme Corporation\t123 Test Street\tAustin\tTX\tUSA\t(512) 555-0100\tcontact@testacme.com\twww.testacme.com\n"
    )
    files = {
        "source1": ("source1.tsv", tsv_content1, "text/tab-separated-values"),
        "source2": ("source2.tsv", tsv_content2, "text/tab-separated-values")
    }
    res = client.post("/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["total_records"] == 2

def test_compare_endpoint():
    payload = {
        "record1": {
            "source_record_id": "T1",
            "business_name": "Apex Technology Solutions Pvt Ltd",
            "address": "100 Market St, Suite 500",
            "city": "San Francisco",
            "state": "California",
            "country": "USA",
            "phone": "+1 415 123-4567",
            "email": "info@apextech.com",
            "website": "https://www.apextech.com"
        },
        "record2": {
            "source_record_id": "T2",
            "business_name": "apex technology solutions private limited",
            "address": "100 Market Street #500",
            "city": "San Francisco",
            "state": "CA",
            "country": "USA",
            "phone": "(415) 123-4567",
            "email": "contact@apextech.com",
            "website": "http://apextech.com"
        },
        "threshold": 60.0
    }
    res = client.post("/compare", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["result"]["is_match"] is True
    assert data["result"]["confidence_score"] >= 80.0
    assert "similarity_breakdown" in data["result"]
    assert "evidence_summary" in data["result"]

def test_export_endpoints():
    # Export entities CSV
    res_ent_csv = client.get("/export/entities?format=csv")
    assert res_ent_csv.status_code == 200
    assert "text/csv" in res_ent_csv.headers["content-type"]
    assert "entity_id" in res_ent_csv.text

    # Export entities JSON
    res_ent_json = client.get("/export/entities?format=json")
    assert res_ent_json.status_code == 200
    assert isinstance(res_ent_json.json(), list)

    # Export results CSV
    res_res_csv = client.get("/export/results?format=csv")
    assert res_res_csv.status_code == 200
    assert "text/csv" in res_res_csv.headers["content-type"]
    assert "record_id_1" in res_res_csv.text

    # Export results JSON
    res_res_json = client.get("/export/results?format=json")
    assert res_res_json.status_code == 200
    assert isinstance(res_res_json.json(), list)

def test_review_endpoint():
    # Fetch existing results
    res = client.get("/results?page=1&limit=5")
    assert res.status_code == 200
    data = res.json()
    if data["results"]:
        pair = data["results"][0]
        r1 = pair["record_id_1"]
        r2 = pair["record_id_2"]
        
        # Confirm pair
        review_res = client.post("/review", json={"record_id_1": r1, "record_id_2": r2, "action": "confirm"})
        assert review_res.status_code == 200
        assert review_res.json()["status"] == "success"

