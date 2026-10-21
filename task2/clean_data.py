
import json
import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "dirty_sales.csv"
OUTPUT_CSV = BASE_DIR / "clean_sales.csv"
OUTPUT_JSON = BASE_DIR / "clean_sales.json"
REPORT_FILE = BASE_DIR / "quality_report.txt"

REQUIRED_COLUMNS = [
    "order_id", "customer", "amount", "order_date", "city"
]


def normalize_currency(value):
    """Convert currency strings into numeric amounts."""
    if pd.isna(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    text = re.sub(r"(?i)INR|Rs\.?|₹", "", text)
    text = text.replace(",", "").strip()

    try:
        return float(text)
    except ValueError:
        return None


def clean_data():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"{INPUT_FILE} not found. Run generate_dirty_data.py first."
        )

    df = pd.read_csv(INPUT_FILE)
    original_rows = len(df)
    original_columns = list(df.columns)

    # Normalize column names.
    df.columns = df.columns.str.strip().str.lower()

    # Schema validation: required columns must exist.
    missing_columns = [
        col for col in REQUIRED_COLUMNS if col not in df.columns
    ]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Remove fully duplicated records.
    exact_duplicates = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # Normalize text columns and missing-value markers.
    for col in ["customer", "city"]:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace(
            {"": pd.NA, "nan": pd.NA, "None": pd.NA, "null": pd.NA}
        )

    # Standardize customer capitalization.
    df["customer"] = df["customer"].str.title()
    df["city"] = df["city"].str.title()

    # Normalize currency and date values.
    df["amount"] = df["amount"].apply(normalize_currency)
    df["order_date"] = pd.to_datetime(
        df["order_date"], errors="coerce", dayfirst=True
    )

    # Convert order IDs to strings and clean whitespace.
    df["order_id"] = df["order_id"].astype("string").str.strip()

    # Missing data policy:
    # Keep records, flag invalid/missing values in the quality report.
    # Do not invent customer names, dates, or amounts.
    missing_before = df[REQUIRED_COLUMNS].isna().sum().to_dict()

    # Enforce types and consistent date representation.
    df["amount"] = df["amount"].astype("Float64")
    df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")
    df["order_date"] = df["order_date"].astype("string")

    # Flag records that fail required-field or business-rule validation.
    invalid_amount = df["amount"].isna() | (df["amount"] < 0)
    invalid_order_date = df["order_date"].isna() | (
        df["order_date"].astype("string").str.lower().isin(["<na>", "nat", ""])
    )
    invalid_required = df[REQUIRED_COLUMNS].isna().any(axis=1)

    invalid_rows = invalid_required | invalid_amount | invalid_order_date
    rejected_rows = df[invalid_rows].copy()
    clean_df = df[~invalid_rows].copy()

    # Final schema checks on accepted records.
    schema_valid = (
        clean_df.columns.tolist() == REQUIRED_COLUMNS
        and clean_df["order_id"].notna().all()
        and clean_df["customer"].notna().all()
        and clean_df["amount"].notna().all()
        and (clean_df["amount"] >= 0).all()
        and clean_df["order_date"].notna().all()
        and clean_df["city"].notna().all()
    )

    clean_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    clean_df.to_json(
        OUTPUT_JSON, orient="records", indent=4, force_ascii=False
    )

    # Create an automated quality report.
    report = [
        "AUTOMATED DATA CLEANING - QUALITY REPORT",
        "=" * 45,
        f"Input file: {INPUT_FILE.name}",
        f"Original rows: {original_rows}",
        f"Exact duplicate rows removed: {exact_duplicates}",
        f"Rows after duplicate removal: {len(df)}",
        f"Accepted clean rows: {len(clean_df)}",
        f"Rejected rows: {len(rejected_rows)}",
        f"Schema validation: {'PASS' if schema_valid else 'FAIL'}",
        "",
        "Missing values after normalization (before rejection):",
    ]

    report.extend(
        f"- {column}: {count}"
        for column, count in missing_before.items()
    )

    report.extend([
        "",
        "Cleaning rules:",
        "- Trimmed whitespace and standardized text capitalization.",
        "- Normalized currency strings to numeric amounts.",
        "- Standardized valid dates to YYYY-MM-DD.",
        "- Invalid dates and missing required values were rejected.",
        "- Negative amounts were rejected by business-rule validation.",
        "",
        f"Clean CSV: {OUTPUT_CSV.name}",
        f"Clean JSON: {OUTPUT_JSON.name}",
        f"Schema validation result: {'PASS' if schema_valid else 'FAIL'}",
    ])

    REPORT_FILE.write_text("\n".join(report), encoding="utf-8")

    print("\n".join(report))
    print("\nRejected records:")
    print(rejected_rows.to_string(index=False) if not rejected_rows.empty else "None")

    if not schema_valid:
        raise ValueError("Final schema validation failed.")


if __name__ == "__main__":
    clean_data()
