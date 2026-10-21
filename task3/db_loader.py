
import json
import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent
PROJECT_DIR = BASE_DIR.parent
INPUT_FILE = PROJECT_DIR / "task2" / "clean_sales.csv"
DB_FILE = BASE_DIR / "sales.db"
BATCH_SIZE = 100


def create_schema(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            order_id TEXT PRIMARY KEY,
            customer TEXT NOT NULL,
            amount REAL NOT NULL CHECK (amount >= 0),
            order_date TEXT NOT NULL,
            city TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)


def load_data():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Clean dataset not found: {INPUT_FILE}\n"
            "Run task2/clean_data.py first."
        )

    df = pd.read_csv(INPUT_FILE, dtype={"order_id": str})

    required = ["order_id", "customer", "amount", "order_date", "city"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[required].copy()

    # Validate before inserting into the database.
    if df.isna().any().any():
        raise ValueError("Dataset contains missing required values.")

    df["order_id"] = df["order_id"].astype(str).str.strip()
    df["customer"] = df["customer"].astype(str).str.strip()
    df["city"] = df["city"].astype(str).str.strip()
    df["amount"] = pd.to_numeric(df["amount"], errors="raise")
    df["order_date"] = pd.to_datetime(
        df["order_date"], errors="raise"
    ).dt.strftime("%Y-%m-%d")

    if (df["amount"] < 0).any():
        raise ValueError("Negative amounts are not allowed.")

    if (df["order_id"] == "").any():
        raise ValueError("Empty order IDs are not allowed.")

    if df["order_id"].duplicated().any():
        raise ValueError("Duplicate order IDs in input dataset.")

    rows = list(df.itertuples(index=False, name=None))
    inserted_or_updated = 0

    # A context manager commits on success and rolls back on failure.
    with sqlite3.connect(DB_FILE) as connection:
        create_schema(connection)

        query = """
            INSERT INTO sales (
                order_id, customer, amount, order_date, city
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(order_id) DO UPDATE SET
                customer = excluded.customer,
                amount = excluded.amount,
                order_date = excluded.order_date,
                city = excluded.city,
                updated_at = CURRENT_TIMESTAMP
        """

        for start in range(0, len(rows), BATCH_SIZE):
            batch = rows[start:start + BATCH_SIZE]
            connection.executemany(query, batch)
            inserted_or_updated += len(batch)

        total = connection.execute(
            "SELECT COUNT(*) FROM sales"
        ).fetchone()[0]

        invalid_rows = connection.execute("""
            SELECT COUNT(*) FROM sales
            WHERE order_id IS NULL
               OR customer IS NULL
               OR amount < 0
               OR order_date IS NULL
               OR city IS NULL
        """).fetchone()[0]

        report = {
            "source_file": str(INPUT_FILE.name),
            "database": str(DB_FILE.name),
            "input_rows": len(rows),
            "rows_processed": inserted_or_updated,
            "total_rows_in_database": total,
            "invalid_rows": invalid_rows,
            "schema_created": True,
            "upsert_enabled": True,
            "validation": "PASS" if invalid_rows == 0 else "FAIL"
        }

    report_file = BASE_DIR / "ingestion_report.json"
    report_file.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8"
    )

    print(json.dumps(report, indent=4))

    if invalid_rows:
        raise ValueError("Database verification found invalid rows.")


if __name__ == "__main__":
    load_data()
