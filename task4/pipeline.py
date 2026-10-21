
import json
import logging
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
TASK2 = ROOT / "task2"
TASK3 = ROOT / "task3"
TASK4 = ROOT / "task4"
DATA_DIR = ROOT / "data"

LOG_DIR = TASK4 / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "pipeline.log"
REPORT_FILE = TASK4 / "pipeline_report.json"
DB_FILE = TASK3 / "sales.db"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
    force=True,
)

logger = logging.getLogger("etl_pipeline")


def extract():
    """Extract book listings from the practice website."""
    logger.info("STEP 1: Extraction started")

    url = "https://books.toscrape.com/catalogue/page-1.html"
    books = []

    with requests.Session() as session:
        session.headers.update({
            "User-Agent": "StudentETLPipeline/1.0"
        })

        for page in range(1, 6):
            response = session.get(url, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            items = soup.select("article.product_pod")
            if not items:
                break

            for item in items:
                title = item.select_one("h3 a")
                price = item.select_one(".price_color")
                rating = item.select_one("p.star-rating")

                if title is None or price is None:
                    continue

                rating_classes = rating.get("class", []) if rating else []
                rating_value = next(
                    (value for value in rating_classes
                     if value != "star-rating"),
                    "Unknown",
                )

                books.append({
                    "title": title.get("title", title.get_text(strip=True)),
                    "price": price.get_text(strip=True),
                    "rating": rating_value,
                    "page": page,
                })

            next_link = soup.select_one("li.next a")
            if next_link is None:
                break

            url = requests.compat.urljoin(url, next_link["href"])
            time.sleep(1)

    if not books:
        raise ValueError("Extraction returned zero records.")

    output = DATA_DIR / "pipeline_extracted_books.json"
    output.write_text(
        json.dumps(books, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    logger.info("Extracted %s book records", len(books))
    return len(books)


def transform():
    """Run Task 2's cleaning and validation."""
    logger.info("STEP 2: Transformation started")

    from importlib.util import spec_from_file_location

    generator_path = TASK2 / "generate_dirty_data.py"
    cleaner_path = TASK2 / "clean_data.py"

    for path in [generator_path, cleaner_path]:
        if not path.exists():
            raise FileNotFoundError(f"Required Task 2 file missing: {path}")

    # Generate the sample dataset, then clean it.
    for script in [generator_path, cleaner_path]:
        import subprocess

        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"{script.name} failed:\n{result.stdout}\n{result.stderr}"
            )

        logger.info("%s completed", script.name)

    output = TASK2 / "clean_sales.csv"
    if not output.exists():
        raise FileNotFoundError("Clean sales CSV was not generated.")

    df = pd.read_csv(output)

    logger.info("Cleaned dataset contains %s rows", len(df))
    return len(df)


def load():
    """Load the cleaned sales dataset using a transactional upsert."""
    logger.info("STEP 3: Database loading started")

    csv_file = TASK2 / "clean_sales.csv"
    if not csv_file.exists():
        raise FileNotFoundError(f"Clean dataset not found: {csv_file}")

    df = pd.read_csv(csv_file, dtype={"order_id": str})
    required = ["order_id", "customer", "amount", "order_date", "city"]

    if any(column not in df.columns for column in required):
        raise ValueError("Input dataset does not match the required schema.")

    df = df[required]
    if df.isna().any().any():
        raise ValueError("Clean dataset contains null values.")
    if df["order_id"].duplicated().any():
        raise ValueError("Duplicate order IDs found.")
    if (pd.to_numeric(df["amount"], errors="raise") < 0).any():
        raise ValueError("Negative amounts are not allowed.")

    TASK3.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_FILE, timeout=30) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                order_id TEXT PRIMARY KEY,
                customer TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                order_date TEXT NOT NULL,
                city TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.executemany("""
            INSERT INTO sales (
                order_id, customer, amount, order_date, city
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(order_id) DO UPDATE SET
                customer = excluded.customer,
                amount = excluded.amount,
                order_date = excluded.order_date,
                city = excluded.city,
                updated_at = CURRENT_TIMESTAMP
        """, [
            (
                str(row.order_id),
                str(row.customer),
                float(row.amount),
                str(row.order_date),
                str(row.city),
            )
            for row in df.itertuples(index=False)
        ])

        count = connection.execute(
            "SELECT COUNT(*) FROM sales"
        ).fetchone()[0]

    logger.info("Database load complete. Total rows: %s", count)
    return count


def run_pipeline():
    started = datetime.now().astimezone()
    logger.info("=" * 55)
    logger.info("ETL PIPELINE STARTED AT %s", started.isoformat())

    report = {
        "started_at": started.isoformat(),
        "status": "FAILED",
        "extracted_records": 0,
        "transformed_records": 0,
        "database_records": 0,
        "error": None,
    }

    try:
        report["extracted_records"] = extract()
        report["transformed_records"] = transform()
        report["database_records"] = load()
        report["status"] = "SUCCESS"

        logger.info("ETL PIPELINE COMPLETED SUCCESSFULLY")

    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
        logger.exception("ETL PIPELINE FAILED")

    finally:
        report["finished_at"] = datetime.now().astimezone().isoformat()
        REPORT_FILE.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        logger.info("Report saved to %s", REPORT_FILE)
        print("\nPIPELINE SUMMARY")
        print(json.dumps(report, indent=2))

    if report["status"] != "SUCCESS":
        raise RuntimeError("Pipeline failed. Check task4/logs/pipeline.log.")

    return report


if __name__ == "__main__":
    run_pipeline()
