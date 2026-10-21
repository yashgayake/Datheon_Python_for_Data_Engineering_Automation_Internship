
# Task 2: Automated Data Cleaning and Schema Transformation

## Overview
A Python and Pandas data-cleaning pipeline that transforms inconsistent sales records into validated, production-style tabular data.

## Features
- Handles missing and null values.
- Normalizes currency strings into numeric values.
- Converts valid dates to YYYY-MM-DD.
- Removes exact duplicate records.
- Standardizes text capitalization and whitespace.
- Validates required columns and data types.
- Rejects records with missing required fields, invalid dates, or negative amounts.
- Exports cleaned CSV and JSON files.
- Generates an automated data-quality report.

## Technologies
- Python 3
- Pandas
- JSON
- CSV

## Run Instructions
From the project root:

```bash
python -m pip install pandas
python task2/generate_dirty_data.py
python task2/clean_data.py
```

## Input
`dirty_sales.csv` contains deliberately inconsistent sample sales data.

## Output
- `clean_sales.csv`
- `clean_sales.json`
- `quality_report.txt`

## Validation Policy
Records with missing required fields, invalid dates, or negative amounts are excluded from the clean output and reported as rejected. Missing values are not replaced with fabricated business information.

## Author
Yash Vikas Gayake
