
"""
Data Cleaning Utilities for Business Entity Resolution.
Safely cleans text, handles missing values, and prepares raw fields
for normalization.
"""

import re

import numpy as np
import pandas as pd


NULL_STRINGS = {
    "nan", "null", "none", "n/a", "na",
    "undefined", "nil", "-", "."
}


def clean_missing_value(val) -> str:
    """
    Convert missing values into empty strings.
    Preserve valid values as strings.
    """
    if val is None:
        return ""

    if pd.isna(val):
        return ""

    text = str(val).strip()

    if text.lower() in NULL_STRINGS:
        return ""

    return text


def clean_text(text) -> str:
    """
    Clean text by removing control characters and normalizing whitespace.
    """
    value = clean_missing_value(text)

    if not value:
        return ""

    # Replace non-breaking spaces with normal spaces.
    value = value.replace("\u00a0", " ")

    # Remove control characters such as tabs and newlines.
    value = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", value)

    # Replace repeated whitespace with a single space.
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean all columns in a DataFrame without modifying the original.

    Text columns are whitespace-normalized.
    Missing values and common null strings become empty strings.
    """
    cleaned = df.copy()

    for col in cleaned.columns:
        cleaned[col] = cleaned[col].apply(clean_text)

    return cleaned
