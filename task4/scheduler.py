
import logging
import os
import time
from pathlib import Path
from datetime import datetime

from pipeline import run_pipeline

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "scheduler.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
    force=True,
)

INTERVAL_SECONDS = int(os.getenv("ETL_INTERVAL_SECONDS", "86400"))


def main():
    logging.info("Scheduler started. Interval: %s seconds", INTERVAL_SECONDS)
    print(f"Scheduler running. Interval: {INTERVAL_SECONDS} seconds.")
    print("Press Ctrl+C to stop.")

    while True:
        try:
            run_pipeline()
        except Exception:
            logging.exception("Scheduled pipeline run failed.")

        logging.info("Next run in %s seconds", INTERVAL_SECONDS)

        try:
            time.sleep(INTERVAL_SECONDS)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScheduler stopped.")
