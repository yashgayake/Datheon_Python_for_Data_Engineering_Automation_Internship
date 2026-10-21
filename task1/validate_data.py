
import csv
import json
from pathlib import Path

CSV_FILE = Path("data/books.csv")
JSON_FILE = Path("data/books.json")


def validate_data():
    if not CSV_FILE.exists() or not JSON_FILE.exists():
        print("ERROR: CSV or JSON file is missing.")
        return

    with open(JSON_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    required_fields = {"title", "price", "rating", "page"}
    errors = []

    for index, record in enumerate(records, start=1):
        missing = [
            field for field in required_fields
            if not record.get(field)
        ]

        if missing:
            errors.append(f"Record {index}: missing {missing}")

    titles = [record["title"].strip() for record in records]
    duplicate_count = len(titles) - len(set(titles))

    with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as file:
        csv_records = list(csv.DictReader(file))

    print("\n--- DATA VALIDATION REPORT ---")
    print(f"JSON records: {len(records)}")
    print(f"CSV records: {len(csv_records)}")
    print(f"Duplicate titles: {duplicate_count}")
    print(f"Records with missing fields: {len(errors)}")
    print(f"100+ record requirement: {'PASS' if len(records) >= 100 else 'FAIL'}")
    print(f"CSV/JSON count match: {'PASS' if len(records) == len(csv_records) else 'FAIL'}")

    if errors:
        print("\nFirst validation errors:")
        for error in errors[:5]:
            print(error)
    else:
        print("Required fields validation: PASS")


if __name__ == "__main__":
    validate_data()
