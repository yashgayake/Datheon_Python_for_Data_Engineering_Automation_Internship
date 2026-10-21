
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_FILE = BASE_DIR / "sales.db"


def verify_database():
    if not DB_FILE.exists():
        raise FileNotFoundError(
            "Database not found. Run task3/db_loader.py first."
        )

    with sqlite3.connect(DB_FILE) as connection:
        connection.row_factory = sqlite3.Row

        tables = connection.execute("""
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'sales'
        """).fetchall()

        if not tables:
            raise AssertionError("sales table does not exist.")

        columns = connection.execute(
            "PRAGMA table_info(sales)"
        ).fetchall()

        column_names = [column["name"] for column in columns]
        expected = [
            "order_id", "customer", "amount",
            "order_date", "city", "created_at", "updated_at"
        ]

        missing = [name for name in expected if name not in column_names]
        if missing:
            raise AssertionError(f"Missing columns: {missing}")

        total = connection.execute(
            "SELECT COUNT(*) FROM sales"
        ).fetchone()[0]

        duplicate_ids = connection.execute("""
            SELECT COUNT(*) FROM (
                SELECT order_id
                FROM sales
                GROUP BY order_id
                HAVING COUNT(*) > 1
            )
        """).fetchone()[0]

        invalid = connection.execute("""
            SELECT COUNT(*) FROM sales
            WHERE order_id IS NULL OR customer IS NULL
               OR amount IS NULL OR amount < 0
               OR order_date IS NULL OR city IS NULL
        """).fetchone()[0]

        sample = connection.execute("""
            SELECT order_id, customer, amount, order_date, city
            FROM sales
            ORDER BY order_id
            LIMIT 5
        """).fetchall()

    print("DATABASE VERIFICATION REPORT")
    print("=" * 35)
    print(f"Table exists: {'PASS' if tables else 'FAIL'}")
    print(f"Schema validation: {'PASS' if not missing else 'FAIL'}")
    print(f"Total records: {total}")
    print(f"Duplicate primary keys: {duplicate_ids}")
    print(f"Invalid records: {invalid}")
    print("\nSample records:")

    for row in sample:
        print(dict(row))

    assert duplicate_ids == 0, "Duplicate primary keys found."
    assert invalid == 0, "Invalid records found."
    assert not missing, f"Missing schema columns: {missing}"

    print("\nAll database verification checks passed.")


if __name__ == "__main__":
    verify_database()
