import os
import pandas as pd

# ===== Paths =====
RAW_DATA_PATH = os.path.join("..", "data", "raw")
CLEAN_DATA_PATH = os.path.join("..", "data", "clean")

print(f"📂 Loading raw CSV files from {RAW_DATA_PATH}")

# ===== Load raw data =====
providers = pd.read_csv(os.path.join(RAW_DATA_PATH, "providers_data.csv"))
receivers = pd.read_csv(os.path.join(RAW_DATA_PATH, "receivers_data.csv"))
food_listings = pd.read_csv(
    os.path.join(RAW_DATA_PATH, "food_listings_data.csv"),
    parse_dates=["Expiry_Date"],
    dayfirst=False
)
claims = pd.read_csv(
    os.path.join(RAW_DATA_PATH, "claims_data.csv"),
    parse_dates=["Timestamp"],
    dayfirst=True
)

# ===== Print raw data shapes =====
print("\n📊 Raw Data Shapes:")
print("   Providers:", providers.shape)
print("   Receivers:", receivers.shape)
print("   Food Listings:", food_listings.shape)
print("   Claims:", claims.shape)

print("\n🧹 Cleaning data...")

# ===== Cleaning =====

# Remove duplicates
providers.drop_duplicates(inplace=True)
receivers.drop_duplicates(inplace=True)
food_listings.drop_duplicates(inplace=True)
claims.drop_duplicates(inplace=True)

# Keep only rows with positive quantity
food_listings = food_listings[food_listings["Quantity"] > 0]

# Simulate current date as Jan 1, 2025 (for expiry filtering)
simulated_today = pd.Timestamp("2025-01-01")
cutoff_date = simulated_today - pd.Timedelta(days=30)

print(f"\nSimulated Today: {simulated_today}")
print(f"Cutoff Date (30 days before simulated today): {cutoff_date}")

# Keep only items not expired more than 30 days ago (relative to simulated_today)
food_listings = food_listings[food_listings["Expiry_Date"] >= cutoff_date]

# Drop rows missing critical info
food_listings.dropna(subset=["Food_Name", "Location"], inplace=True)

# ===== Save cleaned CSVs =====
print(f"\n💾 Saving cleaned CSV files to {CLEAN_DATA_PATH}")
os.makedirs(CLEAN_DATA_PATH, exist_ok=True)

providers_path = os.path.join(CLEAN_DATA_PATH, "providers_clean.csv")
receivers_path = os.path.join(CLEAN_DATA_PATH, "receivers_clean.csv")
food_listings_path = os.path.join(CLEAN_DATA_PATH, "food_listings_clean.csv")
claims_path = os.path.join(CLEAN_DATA_PATH, "claims_clean.csv")

providers.to_csv(providers_path, index=False)
receivers.to_csv(receivers_path, index=False)
food_listings.to_csv(food_listings_path, index=False)
claims.to_csv(claims_path, index=False)

# ===== Print shapes of cleaned data =====
print("\n📊 Clean Data Shapes:")
print("   Providers Clean:", pd.read_csv(providers_path).shape)
print("   Receivers Clean:", pd.read_csv(receivers_path).shape)
print("   Food Listings Clean:", pd.read_csv(food_listings_path).shape)
print("   Claims Clean:", pd.read_csv(claims_path).shape)

print("\n🎯 ETL completed successfully!")
