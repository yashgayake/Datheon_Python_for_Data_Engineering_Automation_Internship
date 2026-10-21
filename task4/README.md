
# Task 4: Scheduled End-to-End ETL Pipeline with Alerting

## Overview
An automated Python pipeline that extracts paginated website data, transforms and validates a sales dataset, and loads the cleaned records into SQLite.

## Features
- Extracts data from a practice website.
- Cleans sales records using Task 2 scripts.
- Loads records using SQLite upserts.
- Uses database transactions.
- Writes timestamped execution logs.
- Generates a JSON summary report.
- Supports repeated scheduled execution.
- Records errors and marks failed runs.

## Technologies
Python 3, Requests, BeautifulSoup4, Pandas, SQLite, Logging.

## Run once
From the project root:

```bash
python task4/pipeline.py
```

## Run on a schedule
From the project root:

```bash
python task4/scheduler.py
```

Stop the scheduler with Ctrl+C.

For testing, set a shorter interval in PowerShell:

```powershell
$env:ETL_INTERVAL_SECONDS = "60"
python task4/scheduler.py
```

## Outputs
- `data/pipeline_extracted_books.json`
- `task2/clean_sales.csv`
- `task3/sales.db`
- `task4/pipeline_report.json`
- `task4/logs/pipeline.log`
- `task4/logs/scheduler.log`

## Notifications
The current implementation generates a local JSON summary and persistent logs. Email/webhook delivery can be configured separately using credentials stored in environment variables.

## Author
Yash Vikas Gayake
