"""
Configuration and constants for Business Entity Resolution System.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
TRAIN_DIR = DATASET_DIR / "train"
TEST_DIR = DATASET_DIR / "test"
MODELS_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Default model path
MODEL_PATH = MODELS_DIR / "entity_resolution_rf.joblib"
METADATA_PATH = MODELS_DIR / "model_metadata.json"

# Resolution Thresholds (0-100 scale)
CONFIDENCE_TIERS = {
    "VERY_HIGH": {"min": 90.0, "max": 100.0, "label": "Very High Confidence", "status": "Match"},
    "HIGH": {"min": 75.0, "max": 89.99, "label": "High Confidence", "status": "Match"},
    "POSSIBLE": {"min": 60.0, "max": 74.99, "label": "Possible Match", "status": "Potential Match"},
    "LOW": {"min": 40.0, "max": 59.99, "label": "Low Confidence", "status": "Review Required"},
    "UNLIKELY": {"min": 0.0, "max": 39.99, "label": "Unlikely Match", "status": "Non-Match"},
}

# Default decision threshold for clustering pairs
DEFAULT_MATCH_THRESHOLD = 60.0

# Feature column names
FEATURE_COLUMNS = [
    "name_token_sort_ratio",
    "name_token_set_ratio",
    "name_levenshtein_ratio",
    "address_similarity",
    "city_similarity",
    "state_match",
    "country_match",
    "phone_similarity",
    "email_similarity",
    "website_similarity",
    "exact_name_match",
    "exact_phone_match",
    "exact_email_match",
    "exact_website_match",
    "exact_city_name_match"
]

# Legal suffix dictionary for business name normalization
LEGAL_SUFFIXES = {
    "pvt ltd": "private limited",
    "pvt. ltd.": "private limited",
    "pvt. ltd": "private limited",
    "pvt.ltd": "private limited",
    "pvt ltd.": "private limited",
    "private ltd": "private limited",
    "ltd": "limited",
    "ltd.": "limited",
    "inc": "incorporated",
    "inc.": "incorporated",
    "llc": "llc",
    "llc.": "llc",
    "corp": "corporation",
    "corp.": "corporation",
    "co": "company",
    "co.": "company",
    "co., ltd.": "company limited",
    "plc": "public limited company",
    "gmbh": "gmbh",
    "sa": "sa",
    "technologies": "tech",
    "technology": "tech",
    "solutions": "solutions",
    "enterprises": "enterprises",
    "international": "intl",
    "intl.": "intl",
    "group": "group",
    "grp": "group",
    "holdings": "holdings",
    "systems": "systems",
    "services": "services",
    "laboratories": "labs",
    "lab": "labs"
}

# Address abbreviation dictionary
ADDRESS_ABBREVIATIONS = {
    "rd": "road",
    "rd.": "road",
    "st": "street",
    "st.": "street",
    "str": "street",
    "ave": "avenue",
    "ave.": "avenue",
    "blvd": "boulevard",
    "blvd.": "boulevard",
    "hwy": "highway",
    "pkwy": "parkway",
    "dr": "drive",
    "dr.": "drive",
    "ln": "lane",
    "ln.": "lane",
    "ste": "suite",
    "ste.": "suite",
    "apt": "apartment",
    "apt.": "apartment",
    "fl": "floor",
    "fl.": "floor",
    "bldg": "building",
    "bldg.": "building",
    "pl": "place",
    "pl.": "place",
    "ctr": "center",
    "sq": "square"
}
