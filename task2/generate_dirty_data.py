
import pandas as pd
from pathlib import Path

OUTPUT = Path(__file__).parent / "dirty_sales.csv"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

data = [
    {"order_id": "101", "customer": " Rahul ", "amount": "₹1,200.00", "order_date": "21/10/2026", "city": "Pune"},
    {"order_id": "102", "customer": "PRIYA", "amount": "Rs. 850", "order_date": "2026-10-20", "city": "Mumbai"},
    {"order_id": "103", "customer": None, "amount": "500", "order_date": "19-10-2026", "city": "Pune"},
    {"order_id": "104", "customer": "Amit", "amount": None, "order_date": "2026/10/18", "city": "Nashik"},
    {"order_id": "105", "customer": "Sneha", "amount": "₹2,400", "order_date": "invalid-date", "city": "Pune"},
    {"order_id": "106", "customer": "Rahul", "amount": "1200", "order_date": "21/10/2026", "city": "Pune"},
    {"order_id": "107", "customer": " neha ", "amount": "Rs 750.50", "order_date": "17/10/2026", "city": "Nagpur"},
    {"order_id": "108", "customer": "Karan", "amount": "-200", "order_date": "16/10/2026", "city": "Mumbai"},
    {"order_id": "109", "customer": "Meera", "amount": "1,000", "order_date": "15/10/2026", "city": "Pune"},
    {"order_id": "110", "customer": "Vijay", "amount": "₹0", "order_date": "14/10/2026", "city": "Aurangabad"},
    {"order_id": "111", "customer": "Priya", "amount": "850", "order_date": "2026-10-20", "city": "Mumbai"},
    {"order_id": "112", "customer": "Arjun", "amount": "₹3,250.75", "order_date": "13/10/2026", "city": None},
]

df = pd.DataFrame(data)
df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")

print(f"Dirty dataset created: {OUTPUT}")
print(f"Total rows: {len(df)}")
print("\nSample data:")
print(df.head())
