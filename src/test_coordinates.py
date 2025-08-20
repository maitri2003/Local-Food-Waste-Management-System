import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///../data/food_waste.db")
df = pd.read_sql("SELECT Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type, latitude, longitude FROM food_listings LIMIT 5", engine)
print(df)
