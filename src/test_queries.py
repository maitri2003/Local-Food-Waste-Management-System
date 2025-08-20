import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///../data/food_waste.db")

queries = [
    ("Providers per city", "SELECT city, COUNT(DISTINCT provider_id) AS num_providers FROM providers GROUP BY city;"),
    ("Receivers per city", "SELECT city, COUNT(DISTINCT receiver_id) AS num_receivers FROM receivers GROUP BY city;"),
    ("Top provider type by quantity", "SELECT provider_type, SUM(quantity) AS total_qty FROM food_listings GROUP BY provider_type ORDER BY total_qty DESC LIMIT 1;"),
    ("Contact info (Mumbai)", "SELECT name, contact, address FROM providers WHERE city = 'Mumbai';"),
    ("Receivers with most claims", "SELECT r.receiver_id, r.name, COUNT(c.claim_id) AS claims_count FROM claims c JOIN receivers r ON c.receiver_id = r.receiver_id GROUP BY r.receiver_id ORDER BY claims_count DESC;"),
    ("Total quantity available", "SELECT SUM(quantity) AS total_quantity FROM food_listings;")
]

for title, query in queries:
    print(f"\n--- {title} ---")
    df = pd.read_sql(query, engine)
    print(df)
