"""
Data Cleaning Utilities for Business Entity Resolution.
Safely cleans text, handles missing values, and prepares raw fields for normalization.
"""

import re
import pandas as pd
import numpy as np

NULL_STRINGS = {"nan", "null", "none", "n/a", "na", "undefined", "nil", "-", "."}

def clean_missing_value(val) -> str:
    """
    Safely handle missing or null values.
    Returns an empty string instead of misleading strings like 'nan' or 'None'.
    """
    if val is None or pd.isna(val):
        return ""
    if isinstance(val, (float, int)):
        if np.isnan(val) if isinstance(val, float) else False:
            return ""
        return str(val).strip()
    
    s = str(val).strip()
    if s.lower() in NULL_STRINGS:
        return ""
    return s

def clean_text(text: str) -> str:
    """
    Cleans raw text: removes multiple spaces, unprintable characters,
    and trims surrounding whitespace.
    """
    val = clean_missing_value(text)
    if not val:
        return ""
    # Replace non-breaking spaces and control characters
    val = re.sub(r'[\r\n\t]+', ' ', val)
    val = re.sub(r'\s+', ' ', val)
    return val.strip()

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans all string columns in a dataframe safely.
    """
    cleaned = df.copy()
    for col in cleaned.columns:
        cleaned[col] = cleaned[col].apply(clean_missing_value)
    return cleaned
