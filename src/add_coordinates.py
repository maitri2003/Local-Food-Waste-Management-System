import os, json, time
import pandas as pd
from geopy.geocoders import Nominatim

CLEAN_DATA_PATH = os.path.join("..", "data", "clean")
FOOD_CSV = os.path.join(CLEAN_DATA_PATH, "food_listings_clean.csv")
CACHE_FILE = os.path.join("..", "data", "geocode_cache.json")

print("📥 Loading cleaned food listings...")
df = pd.read_csv(FOOD_CSV)

# Normalize columns
df.columns = df.columns.str.lower()

# Ensure latitude/longitude columns exist
if "latitude" not in df.columns:  df["latitude"] = pd.NA
if "longitude" not in df.columns: df["longitude"] = pd.NA

# Load / init cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}

geolocator = Nominatim(user_agent="food_waste_app")

def geocode_once(addr: str):
    if not isinstance(addr, str) or not addr.strip():
        return None, None
    key = addr.strip().lower()
    if key in cache and cache[key] is not None:
        return cache[key].get("lat"), cache[key].get("lng")
    try:
        loc = geolocator.geocode(addr)
        if loc:
            cache[key] = {"lat": loc.latitude, "lng": loc.longitude}
            return loc.latitude, loc.longitude
        cache[key] = None
        return None, None
    except Exception:
        return None, None

# Fill missing coords
rows_before = len(df)
to_fill = df[df["latitude"].isna() | df["longitude"].isna()]
print(f"🧭 Geocoding rows needing coordinates: {len(to_fill)}")

for idx, row in to_fill.iterrows():
    lat, lng = geocode_once(str(row.get("location", "")))
    if lat is not None and lng is not None:
        df.at[idx, "latitude"] = lat
        df.at[idx, "longtitude"] = lng
    time.sleep(1)  # be polite to the free service

# Save cache
os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
with open(CACHE_FILE, "w", encoding="utf-8") as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

# Persist back to clean CSV
df.to_csv(FOOD_CSV, index=False)
print("✅ Coordinates saved to clean CSV:", FOOD_CSV)

print("📊 Coordinate availability:",
      f"{df['latitude'].notna().sum()} / {rows_before} rows have latitude")

