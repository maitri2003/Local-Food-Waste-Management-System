import os, sqlite3
import pandas as pd

CLEAN_DATA_PATH = os.path.join("..", "data", "clean")
DB_PATH = os.path.join("..", "data", "food_waste.db")

tables = {
    "providers":     "providers_clean.csv",
    "receivers":     "receivers_clean.csv",
    "food_listings": "food_listings_clean.csv",
    "claims":        "claims_clean.csv",
}

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
conn = sqlite3.connect(DB_PATH)

for table, fname in tables.items():
    path = os.path.join(CLEAN_DATA_PATH, fname)
    if not os.path.exists(path):
        print(f"⚠️  Missing clean file: {path} — skipping.")
        continue

    df = pd.read_csv(path)
    df.columns = df.columns.str.lower()  # enforce lowercase in DB
    print(f"⬆️  Loading {table}: {df.shape} -> {DB_PATH}")
    df.to_sql(table, conn, if_exists="replace", index=False)

conn.close()
print("🎯 Load complete.")
