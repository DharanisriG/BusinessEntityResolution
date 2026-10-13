"""
Data Loading Utilities for Business Entity Resolution.
Safely loads TSV and CSV files with robust column validation and encoding handling.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
from backend.preprocessing.cleaning import clean_dataframe
from backend.preprocessing.normalization import normalize_record

REQUIRED_COLUMNS = ["business_name"]
STANDARD_COLUMNS = [
    "source_record_id", "business_name", "address", "city", "state", "country", "phone", "email", "website"
]

COLUMN_SYNONYMS = {
    "id": "source_record_id",
    "record_id": "source_record_id",
    "source_id": "source_record_id",
    "company_name": "business_name",
    "company": "business_name",
    "name": "business_name",
    "entity_name": "business_name",
    "street": "address",
    "street_address": "address",
    "addr": "address",
    "telephone": "phone",
    "phone_number": "phone",
    "contact_number": "phone",
    "mail": "email",
    "email_address": "email",
    "url": "website",
    "web": "website",
    "web_url": "website",
    "site": "website"
}

def load_table_file(file_path_or_buffer, default_source_name: str = "Source") -> Tuple[pd.DataFrame, List[str]]:
    """
    Loads a TSV or CSV file into a standardized DataFrame.
    Returns (cleaned_dataframe, detected_warnings).
    """
    warnings = []
    
    # Try reading as TSV, then CSV
    df = None
    try:
        # Check if tab-delimited
        df = pd.read_csv(file_path_or_buffer, sep="\t", dtype=str, keep_default_na=False)
        if len(df.columns) <= 1:
            if hasattr(file_path_or_buffer, "seek"):
                file_path_or_buffer.seek(0)
            df = pd.read_csv(file_path_or_buffer, sep=",", dtype=str, keep_default_na=False)
    except Exception as e:
        if hasattr(file_path_or_buffer, "seek"):
            file_path_or_buffer.seek(0)
        df = pd.read_csv(file_path_or_buffer, sep=None, engine="python", dtype=str, keep_default_na=False)

    # Standardize column names (lowercase & stripped)
    renamed = {}
    for col in df.columns:
        norm_col = str(col).strip().lower()
        if norm_col in COLUMN_SYNONYMS:
            renamed[col] = COLUMN_SYNONYMS[norm_col]
        else:
            renamed[col] = norm_col
    df = df.rename(columns=renamed)
    
    # Validate required columns
    if "business_name" not in df.columns:
        raise ValueError("The uploaded file is missing the required column 'business_name'. Detected columns: " + ", ".join(df.columns))
        
    # Ensure source_record_id exists
    if "source_record_id" not in df.columns:
        df["source_record_id"] = [f"{default_source_name}_{i+1:04d}" for i in range(len(df))]
        warnings.append("Missing 'source_record_id' column: Auto-generated unique IDs.")
        
    # Ensure standard schema fields exist
    for std_col in STANDARD_COLUMNS:
        if std_col not in df.columns:
            df[std_col] = ""
            
    df["source"] = default_source_name
    df = clean_dataframe(df)
    return df, warnings

def load_sources_from_dir(directory_path: Path, prefix: str = "train") -> Dict[str, pd.DataFrame]:
    """
    Loads all source TSV files from a directory (e.g. train_source1.tsv, train_source2.tsv).
    """
    sources = {}
    dir_p = Path(directory_path)
    if not dir_p.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
        
    for p in sorted(dir_p.glob(f"{prefix}_source*.tsv")):
        source_name = p.stem.replace(f"{prefix}_", "").title() # e.g. 'Source1'
        df, _ = load_table_file(p, default_source_name=source_name)
        sources[source_name] = df
        
    return sources

def load_and_normalize_dataset(directory_path: Path, prefix: str = "train") -> Tuple[List[Dict[str, Any]], Dict[str, pd.DataFrame]]:
    """
    Loads all source files and produces a unified list of normalized records.
    """
    sources_dict = load_sources_from_dir(directory_path, prefix=prefix)
    all_normalized_records = []
    
    for src_name, df in sources_dict.items():
        for _, row in df.iterrows():
            rec_dict = row.to_dict()
            rec_dict["source"] = src_name
            norm_rec = normalize_record(rec_dict)
            norm_rec["source"] = src_name
            all_normalized_records.append(norm_rec)
            
    return all_normalized_records, sources_dict
