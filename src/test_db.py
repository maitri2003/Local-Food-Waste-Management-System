import pandas as pd
from sqlalchemy import create_engine

# Connect to database
engine = create_engine("sqlite:///../data/food_waste.db")

# Show tables (SQLite specific query)
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", engine)
print("📋 Tables in DB:")
print(tables)

# Show sample data from each table
for table in ["providers", "receivers", "food_listings", "claims"]:
    print(f"\n--- {table.upper()} ---")
    df = pd.read_sql(f"SELECT * FROM {table} LIMIT 5", engine)
    print(df)
