import streamlit as st
import sqlite3
import pandas as pd
import folium
from streamlit_folium import st_folium

DB_PATH = "../data/food_waste.db"

# ----------------- Utility Functions -----------------

def run_query(query, params=()):
    """Run a query and return results as DataFrame"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def execute_query(query, params=()):
    """Execute INSERT/UPDATE/DELETE"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()

# ----------------- Sidebar Navigation -----------------
st.sidebar.title("🍽️ Local Food Waste Management System")
menu = st.sidebar.radio("Navigate", 
                        ["Dashboard", "CRUD Operations", "SQL Insights", "Contact"])

# ----------------- Dashboard -----------------
if menu == "Dashboard":
    st.title("📊 Food Waste Management Dashboard")

    # Load food listings
    df = run_query("SELECT * FROM food_listings")

    if df.empty:
        st.warning("No food listings available.")
    else:
        # Normalize column names for safety
        df.columns = df.columns.str.lower()

        # Sidebar filters
        provider_filter = st.sidebar.multiselect(
            "Filter by Provider Type", df["provider_type"].unique()
        )
        food_filter = st.sidebar.multiselect(
            "Filter by Food Type", df["food_type"].unique()
        )
        city_filter = st.sidebar.text_input("Filter by City")

        filtered = df.copy()
        if provider_filter:
            filtered = filtered[filtered["provider_type"].isin(provider_filter)]
        if food_filter:
            filtered = filtered[filtered["food_type"].isin(food_filter)]
        if city_filter:
            filtered = filtered[filtered["location"].str.contains(city_filter, case=False, na=False)]

        st.dataframe(filtered)

        # Map visualization
        if "latitude" in filtered.columns and "longitude" in filtered.columns:
            m = folium.Map(
                location=[filtered["latitude"].mean(), filtered["longitude"].mean()],
                zoom_start=11
            )
            for _, row in filtered.iterrows():
                if pd.notnull(row["latitude"]) and pd.notnull(row["longitude"]):
                    popup_text = f"{row['food_name']} ({row['quantity']})"
                    folium.Marker(
                        location=[row["latitude"], row["longitude"]],
                        popup=popup_text
                    ).add_to(m)
            st_folium(m, width=700, height=500)
        else:
            st.info("No coordinates available for mapping.")

# ----------------- CRUD Operations -----------------
elif menu == "CRUD Operations":
    st.title("📝 CRUD Operations")

    crud_action = st.radio("Choose Action", ["Add", "Update", "Delete"])

    # Add Food Listing
    if crud_action == "Add":
        st.subheader("➕ Add Food Listing")
        food_name = st.text_input("Food Name")
        quantity = st.number_input("Quantity", min_value=1)
        expiry_date = st.date_input("Expiry Date")
        provider_id = st.number_input("Provider ID", min_value=1)
        provider_type = st.text_input("Provider Type")
        location = st.text_input("Location")
        food_type = st.text_input("Food Type")
        meal_type = st.text_input("Meal Type")

        if st.button("Add Food"):
            query = """
                INSERT INTO food_listings 
                (food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            execute_query(query, (food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type))
            st.success("Food listing added successfully!")

    # Update Food Listing
    elif crud_action == "Update":
        st.subheader("✏️ Update Food Listing")
        food_id = st.number_input("Enter Food ID to Update", min_value=1)
        new_qty = st.number_input("New Quantity", min_value=1)
        if st.button("Update"):
            query = "UPDATE food_listings SET quantity = ? WHERE food_id = ?"
            execute_query(query, (new_qty, food_id))
            st.success(f"Food listing {food_id} updated!")

    # Delete Food Listing
    elif crud_action == "Delete":
        st.subheader("🗑️ Delete Food Listing")
        food_id = st.number_input("Enter Food ID to Delete", min_value=1)
        if st.button("Delete"):
            query = "DELETE FROM food_listings WHERE food_id = ?"
            execute_query(query, (food_id,))
            st.warning(f"Food listing {food_id} deleted!")

# ----------------- SQL Insights -----------------
elif menu == "SQL Insights":
    st.title("📈 SQL Powered Insights")

    queries = {
    # ---------------- Food Providers & Receivers ----------------
    "1. Providers & Receivers by City": """
        SELECT City, 
               (SELECT COUNT(*) FROM providers p WHERE p.City = r.City) AS total_providers,
               COUNT(*) AS total_receivers
        FROM receivers r
        GROUP BY City
    """,

    "2. Top Contributing Provider Type": """
        SELECT provider_type, SUM(quantity) AS total_food
        FROM food_listings
        GROUP BY provider_type
        ORDER BY total_food DESC
        LIMIT 1
    """,

    "3. Provider Contacts by City": """
        SELECT Name, Type, City, Contact
        FROM providers
        ORDER BY City
    """,

    "4. Top Receivers by Claims": """
        SELECT r.Name, COUNT(c.Claim_ID) AS total_claims
        FROM receivers r
        JOIN claims c ON r.Receiver_ID = c.Receiver_ID
        GROUP BY r.Receiver_ID, r.Name
        ORDER BY total_claims DESC
        LIMIT 10
    """,

    # ---------------- Food Listings & Availability ----------------
    "5. Total Quantity of Food Available": """
        SELECT SUM(quantity) AS total_available_food
        FROM food_listings
        WHERE expiry_date >= DATE('now')
    """,

    "6. City with Highest Listings": """
        SELECT location AS City, COUNT(*) AS total_listings
        FROM food_listings
        GROUP BY location
        ORDER BY total_listings DESC
        LIMIT 1
    """,

    "7. Most Common Food Types": """
        SELECT food_type, COUNT(*) AS count_type
        FROM food_listings
        GROUP BY food_type
        ORDER BY count_type DESC
        LIMIT 5
    """,

    # ---------------- Claims & Distribution ----------------
    "8. Claims per Food Item": """
        SELECT f.food_name, COUNT(c.Claim_ID) AS total_claims
        FROM claims c
        JOIN food_listings f ON f.food_id = c.Food_ID
        GROUP BY f.food_id, f.food_name
        ORDER BY total_claims DESC
    """,

    "9. Provider with Most Successful Claims": """
        SELECT p.Name, COUNT(c.Claim_ID) AS successful_claims
        FROM claims c
        JOIN food_listings f ON f.food_id = c.Food_ID
        JOIN providers p ON p.Provider_ID = f.provider_id
        WHERE c.Status = 'Completed'
        GROUP BY p.Provider_ID, p.Name
        ORDER BY successful_claims DESC
        LIMIT 1
    """,

    "10. Claims Status Distribution": """
        SELECT Status, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS percentage
        FROM claims
        GROUP BY Status
    """,

    # ---------------- Analysis & Insights ----------------
    "11. Avg Quantity Claimed per Receiver": """
        SELECT r.Name, AVG(f.quantity) AS avg_claimed
        FROM claims c
        JOIN receivers r ON r.Receiver_ID = c.Receiver_ID
        JOIN food_listings f ON f.food_id = c.Food_ID
        GROUP BY r.Receiver_ID, r.Name
    """,

    "12. Most Claimed Meal Type": """
        SELECT f.meal_type, COUNT(c.Claim_ID) AS total_claims
        FROM claims c
        JOIN food_listings f ON f.food_id = c.Food_ID
        GROUP BY f.meal_type
        ORDER BY total_claims DESC
        LIMIT 1
    """,

    "13. Total Food Donated by Each Provider": """
        SELECT p.Name, SUM(f.quantity) AS total_donated
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.provider_id
        GROUP BY p.Provider_ID, p.Name
        ORDER BY total_donated DESC
    """,

      "14. Top Cities by Total Donated Food": """
        SELECT f.location AS City, SUM(f.quantity) AS total_food
        FROM food_listings f
        GROUP BY f.location
        ORDER BY total_food DESC
        LIMIT 5
    """,

    "15. Providers with No Donations": """
        SELECT p.Name, p.City, p.Contact
        FROM providers p
        LEFT JOIN food_listings f ON p.Provider_ID = f.provider_id
        WHERE f.food_id IS NULL
    """
}


    for title, query in queries.items():
        st.subheader(title)
        result = run_query(query)
        st.dataframe(result)

# ----------------- Contact Providers & Receivers -----------------
elif menu == "Contact":
    st.title("📞 Contact Providers & Receivers")

    contact_choice = st.radio("Choose whom to contact", ["Providers", "Receivers"])

    if contact_choice == "Providers":
        city = st.text_input("Enter City to filter providers")
        query = "SELECT name, type, city, contact FROM providers"
        if city:
            query += " WHERE city LIKE ?"
            df = run_query(query, (f"%{city}%",))
        else:
            df = run_query(query)
        st.subheader("Available Providers")
        st.dataframe(df)

        if not df.empty:
            selected_provider = st.selectbox("Select a provider to view details", df["name"].unique())
            details = df[df["name"] == selected_provider].iloc[0]
            st.markdown(f"""
                **Name:** {details['name']}  
                **Type:** {details['type']}  
                **City:** {details['city']}  
                **Contact:** 📱 {details['contact']}  
            """)

    elif contact_choice == "Receivers":
        city = st.text_input("Enter City to filter receivers")
        query = "SELECT name, type, city, contact FROM receivers"
        if city:
            query += " WHERE city LIKE ?"
            df = run_query(query, (f"%{city}%",))
        else:
            df = run_query(query)
        st.subheader("Available Receivers")
        st.dataframe(df)

        if not df.empty:
            selected_receiver = st.selectbox("Select a receiver to view details", df["name"].unique())
            details = df[df["name"] == selected_receiver].iloc[0]
            st.markdown(f"""
                **Name:** {details['name']}  
                **Type:** {details['type']}  
                **City:** {details['city']}  
                **Contact:** 📱 {details['contact']}  
            """)
