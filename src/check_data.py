import pandas as pd
from sqlalchemy import create_engine


import sqlite3
import pandas as pd

engine = create_engine("sqlite:///../data/food_waste.db")
df = pd.read_sql("SELECT * FROM food_listings", engine)
print(len(df), "rows found")
print(df.head())


conn = sqlite3.connect("../data/food_waste.db")

# Check Providers
df_providers = pd.read_sql("SELECT * FROM providers LIMIT 5", conn)
print("Providers Columns:", df_providers.columns.tolist())

# Check Receivers
df_receivers = pd.read_sql("SELECT * FROM receivers LIMIT 5", conn)
print("Receivers Columns:", df_receivers.columns.tolist())

