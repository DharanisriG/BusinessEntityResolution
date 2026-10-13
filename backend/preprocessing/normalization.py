"""
Data Normalization Module for Business Entity Resolution.
Provides standardizing transformers for business names, addresses, phone numbers,
emails, websites, and geographical locations.
"""

import re
from typing import Dict, Any, Optional
from backend.config import LEGAL_SUFFIXES, ADDRESS_ABBREVIATIONS
from backend.preprocessing.cleaning import clean_missing_value, clean_text

# State abbreviation mapping (US states)
US_STATES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
    "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS", "missouri": "MO",
    "montana": "MT", "nebraska": "NE", "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
    "new mexico": "NM", "new york": "NY", "north carolina": "NC", "north dakota": "ND", "ohio": "OH",
    "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
    "virginia": "VA", "washington": "WA", "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY"
}

def normalize_business_name(name: str) -> str:
    """
    Normalizes a business name:
    - Lowercase & trim
    - Standardize acronyms (e.g. A.B.C. -> abc)
    - Replace & with and
    - Normalize legal entity suffixes (e.g. Pvt Ltd -> private limited)
    - Remove punctuation & extra whitespace
    """
    text = clean_missing_value(name).lower()
    if not text:
        return ""
    
    # Handle acronyms with dots: e.g. "a.b.c." -> "abc"
    text = re.sub(r'\b([a-z])\.([a-z])\.([a-z])?\b', lambda m: m.group(0).replace('.', ''), text)
    text = re.sub(r'\b([a-z])\.([a-z])\b', lambda m: m.group(0).replace('.', ''), text)
    
    # Replace & with 'and'
    text = re.sub(r'\s*&\s*', ' and ', text)
    
    # Remove unwanted special characters, keeping alphanumeric and spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    words = text.split()
    
    # Normalize common abbreviations and legal suffixes
    norm_words = []
    i = 0
    while i < len(words):
        # Check two-word phrases like "pvt ltd" or "private limited"
        if i + 1 < len(words):
            two_word = f"{words[i]} {words[i+1]}"
            if two_word in LEGAL_SUFFIXES:
                norm_words.append(LEGAL_SUFFIXES[two_word])
                i += 2
                continue
        # Check single words
        word = words[i]
        if word in LEGAL_SUFFIXES:
            norm_words.append(LEGAL_SUFFIXES[word])
        else:
            norm_words.append(word)
        i += 1
        
    result = " ".join(norm_words)
    return re.sub(r'\s+', ' ', result).strip()

def extract_core_business_name(name: str) -> str:
    """
    Strips legal suffixes completely to leave only the distinct core business name.
    Useful for soundex / blocking prefixes and core exact matches.
    """
    norm = normalize_business_name(name)
    if not norm:
        return ""
    
    # Strip known suffixes from end
    tokens = norm.split()
    suffixes_to_strip = {"private", "limited", "incorporated", "llc", "corporation", "company", "public", "gmbh", "sa"}
    while tokens and tokens[-1] in suffixes_to_strip:
        tokens.pop()
    
    return " ".join(tokens).strip()

def normalize_address(address: str) -> str:
    """
    Normalizes street address:
    - Lowercase & trim
    - Standardize abbreviations (rd -> road, st -> street, apt -> apartment, etc.)
    - Strip symbols like #, ,, .
    - Collapse extra whitespace
    """
    text = clean_missing_value(address).lower()
    if not text:
        return ""
    
    # Standardize #, suite, apt
    text = text.replace("#", " suite ")
    text = re.sub(r'[^\w\s]', ' ', text)
    
    words = text.split()
    norm_words = []
    for w in words:
        if w in ADDRESS_ABBREVIATIONS:
            norm_words.append(ADDRESS_ABBREVIATIONS[w])
        else:
            norm_words.append(w)
            
    return re.sub(r'\s+', ' ', " ".join(norm_words)).strip()

def normalize_phone(phone: str) -> str:
    """
    Normalizes phone numbers to uniform digit strings.
    - Strips all non-digit characters
    - Strips US leading '1' country code if 11 digits to match 10-digit formats
    """
    raw = clean_missing_value(phone)
    if not raw:
        return ""
    
    digits = re.sub(r'\D', '', raw)
    if not digits:
        return ""
    
    # Standardize US 11-digit numbers starting with 1 to 10-digit
    if len(digits) == 11 and digits.startswith("1"):
        return digits[1:]
    
    # Standardize India 91 prefix if 12 digits (e.g. 919876543210 -> 9876543210)
    if len(digits) == 12 and digits.startswith("91"):
        return digits[2:]
        
    return digits

def normalize_email(email: str) -> str:
    """
    Normalizes email addresses:
    - Lowercase & strip whitespace
    - Validates presence of @
    """
    raw = clean_missing_value(email).lower().strip()
    if not raw or "@" not in raw:
        return ""
    # Remove surrounding spaces or trailing dots
    return raw.strip(". ")

def extract_email_domain(email: str) -> str:
    """
    Extracts the domain portion of an email.
    """
    norm = normalize_email(email)
    if norm and "@" in norm:
        return norm.split("@")[-1].strip()
    return ""

def normalize_website(website: str) -> str:
    """
    Normalizes web URL to domain + path format:
    - Lowercase
    - Strip http://, https://, ftp://
    - Strip leading www.
    - Strip trailing slashes, index.html, query strings
    """
    raw = clean_missing_value(website).lower().strip()
    if not raw:
        return ""
    
    # Strip protocol
    url = re.sub(r'^(https?://|ftp://)', '', raw)
    # Strip www.
    url = re.sub(r'^www\.', '', url)
    # Strip query parameters and anchors
    url = re.sub(r'[?#].*$', '', url)
    # Strip trailing slashes
    url = url.strip('/')
    return url

def extract_domain(website: str) -> str:
    """
    Extracts purely the top-level host/domain from a website URL.
    """
    norm = normalize_website(website)
    if not norm:
        return ""
    return norm.split('/')[0]

def normalize_city(city: str) -> str:
    """
    Normalizes city name.
    """
    text = clean_missing_value(city).lower().strip()
    return re.sub(r'[^a-z0-9\s]', '', text)

def normalize_state(state: str) -> str:
    """
    Normalizes state names to standardized 2-letter codes or clean lowercased names.
    """
    raw = clean_missing_value(state).strip()
    if not raw:
        return ""
    
    lower = raw.lower()
    if lower in US_STATES:
        return US_STATES[lower]
    
    if len(raw) == 2 and raw.isupper():
        return raw
        
    return lower

def normalize_country(country: str) -> str:
    """
    Normalizes country names (e.g. USA, United States -> USA).
    """
    raw = clean_missing_value(country).lower().strip()
    if raw in {"usa", "us", "united states", "united states of america"}:
        return "usa"
    if raw in {"uk", "united kingdom", "great britain", "england"}:
        return "uk"
    if raw in {"in", "ind", "india"}:
        return "india"
    if raw in {"de", "deu", "germany", "deutschland"}:
        return "germany"
    if raw in {"ca", "can", "canada"}:
        return "canada"
    if raw in {"au", "aus", "australia"}:
        return "australia"
    return raw

def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a single business record dictionary.
    Returns both original and normalized fields for explainability and processing.
    """
    return {
        "source_record_id": str(record.get("source_record_id", "")).strip(),
        "business_name": clean_missing_value(record.get("business_name", "")),
        "address": clean_missing_value(record.get("address", "")),
        "city": clean_missing_value(record.get("city", "")),
        "state": clean_missing_value(record.get("state", "")),
        "country": clean_missing_value(record.get("country", "")),
        "phone": clean_missing_value(record.get("phone", "")),
        "email": clean_missing_value(record.get("email", "")),
        "website": clean_missing_value(record.get("website", "")),
        
        # Normalized representations
        "norm_name": normalize_business_name(record.get("business_name", "")),
        "core_name": extract_core_business_name(record.get("business_name", "")),
        "norm_address": normalize_address(record.get("address", "")),
        "norm_city": normalize_city(record.get("city", "")),
        "norm_state": normalize_state(record.get("state", "")),
        "norm_country": normalize_country(record.get("country", "")),
        "norm_phone": normalize_phone(record.get("phone", "")),
        "norm_email": normalize_email(record.get("email", "")),
        "email_domain": extract_email_domain(record.get("email", "")),
        "norm_website": normalize_website(record.get("website", "")),
        "web_domain": extract_domain(record.get("website", ""))
    }
