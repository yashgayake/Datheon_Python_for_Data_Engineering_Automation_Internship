
# Task 3: Relational Database Auto-Ingestion & Upsert Engine

## Overview
A Python SQLite ingestion module that loads cleaned sales data into a relational database using batch inserts, primary-key constraints, upserts, and transaction-safe operations.

## Features
- Creates a structured SQLite table.
- Uses order_id as the primary key.
- Validates the incoming dataset before ingestion.
- Processes records in batches.
- Inserts new records and updates existing records on conflict.
- Uses parameterized SQL statements.
- Uses transaction rollback on failure.
- Generates an ingestion report.
- Verifies table schema, record counts, and data integrity.

## Technologies
- Python 3
- SQLite
- Pandas
- SQL

## Run Instructions
Run these commands from the project root:

```bash
python task2/generate_dirty_data.py
python task2/clean_data.py
python task3/db_loader.py
python task3/verify_db.py
```

## Output
- `sales.db`: SQLite database.
- `ingestion_report.json`: ingestion and validation summary.

## Database Schema
The `sales` table stores order ID, customer, amount, order date, city, and creation/update timestamps.

## Upsert Behavior
The `order_id` primary key identifies existing records. If an incoming record has the same ID, its business fields are updated instead of creating another row.

## Author
Yash Vikas Gayake
