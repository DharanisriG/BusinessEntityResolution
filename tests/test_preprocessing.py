"""
Unit Tests for Data Preprocessing and Normalization.
"""

import pytest
from backend.preprocessing.cleaning import clean_missing_value, clean_text
from backend.preprocessing.normalization import (
    normalize_business_name,
    extract_core_business_name,
    normalize_address,
    normalize_phone,
    normalize_email,
    extract_email_domain,
    normalize_website,
    extract_domain,
    normalize_record
)

def test_missing_values_safe_cleaning():
    assert clean_missing_value(None) == ""
    assert clean_missing_value("nan") == ""
    assert clean_missing_value("None") == ""
    assert clean_missing_value("null") == ""
    assert clean_missing_value("n/a") == ""
    assert clean_missing_value("  ") == ""
    assert clean_missing_value("Valid Company") == "Valid Company"

def test_business_name_normalization():
    # Test legal suffix standardization
    name1 = "ABC Technologies Pvt. Ltd."
    name2 = "abc technologies private limited"
    assert normalize_business_name(name1) == normalize_business_name(name2)
    
    # Test abbreviation & acronyms
    assert normalize_business_name("A.B.C. Technologies") == "abc tech"
    assert normalize_business_name("Apex Solutions & Co.") == "apex solutions and company"
    
    # Test core name extraction
    assert extract_core_business_name("ABC Technologies Pvt Ltd") == "abc tech"
    assert extract_core_business_name("Global Data Enterprises LLC") == "global data enterprises"


def test_address_normalization():
    addr1 = "123 Market St., Suite 400"
    addr2 = "123 Market Street # 400"
    n1 = normalize_address(addr1)
    n2 = normalize_address(addr2)
    assert "market street" in n1
    assert "suite 400" in n1
    assert n1 == n2

    assert normalize_address("456 MG Rd.") == "456 mg road"
    assert normalize_address("789 Innovation Blvd, Apt 2B") == "789 innovation boulevard apartment 2b"

def test_phone_normalization():
    p1 = "(415) 555-1234"
    p2 = "+1 415-555-1234"
    p3 = "415.555.1234"
    p4 = "415 555 1234"
    
    n1 = normalize_phone(p1)
    n2 = normalize_phone(p2)
    n3 = normalize_phone(p3)
    n4 = normalize_phone(p4)
    
    assert n1 == "4155551234"
    assert n1 == n2 == n3 == n4

    # International phone
    assert normalize_phone("+91 98765 43210") == "9876543210"

def test_email_normalization():
    e1 = "  CONTACT@ApexTech.COM "
    e2 = "contact@apextech.com"
    assert normalize_email(e1) == e2
    assert extract_email_domain(e1) == "apextech.com"
    assert normalize_email("invalid_email") == ""

def test_website_normalization():
    w1 = "https://www.apextech.com/about?ref=123"
    w2 = "http://apextech.com/"
    w3 = "www.apextech.com"
    
    assert normalize_website(w1) == "apextech.com/about"
    assert normalize_website(w2) == "apextech.com"
    assert normalize_website(w3) == "apextech.com"
    assert extract_domain(w1) == "apextech.com"
    assert extract_domain(w2) == "apextech.com"

def test_record_normalization():
    raw = {
        "source_record_id": "S1_001",
        "business_name": "Apex Technology Solutions Pvt Ltd",
        "address": "100 Market St, Ste 500",
        "city": "San Francisco",
        "state": "California",
        "country": "USA",
        "phone": "+1 (415) 123-4567",
        "email": "INFO@APEXTECH.COM",
        "website": "https://www.apextech.com"
    }
    norm = normalize_record(raw)
    assert norm["norm_name"] == "apex tech solutions private limited"
    assert norm["norm_city"] == "san francisco"
    assert norm["norm_state"] == "CA"
    assert norm["norm_country"] == "usa"
    assert norm["norm_phone"] == "4151234567"
    assert norm["norm_email"] == "info@apextech.com"
    assert norm["web_domain"] == "apextech.com"

