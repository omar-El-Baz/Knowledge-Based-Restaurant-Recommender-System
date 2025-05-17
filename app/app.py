# app/app.py
import streamlit as st
import pandas as pd

# ----- Load data -----
df = pd.read_csv("data/zomato_cleaned.csv")

# Use the engineered single-cuisine column if it exists; fall back to “cuisines”
CUISINE_COL = "primary_cuisine" if "primary_cuisine" in df.columns else "cuisines"

# ----- Page title -----
st.title("🍽️ Knowledge-Based Restaurant Recommender")

# ----- Sidebar : user preferences -----
st.sidebar.header("Filter your preferences")

# Cuisine selector
selected_cuisines = st.sidebar.multiselect(
    "Choose cuisine(s):",
    options=sorted(df[CUISINE_COL].dropna().unique())
)

# City selector
selected_city = st.sidebar.selectbox(
    "Choose city:",
    options=sorted(df["city"].dropna().unique())
)

# Budget selector (low / medium / high)
selected_budget = st.sidebar.radio(
    "Choose budget:",
    options=sorted(df["cost_bucket"].dropna().unique())
)

# ----- Filter + rank (very simple version) -----
def simple_filter_rank(data, cuisines, city, budget, top_n=10):
    filtered = data.copy()

    # Apply filters one by one
    if cuisines:
        filtered = filtered[filtered[CUISINE_COL].isin(cuisines)]
    if city:
        filtered = filtered[filtered["city"] == city]
    if budget:
        filtered = filtered[filtered["cost_bucket"] == budget]

    if filtered.empty:
        return filtered

    # Cheap “score” = rating * log(votes+1)
    filtered = filtered.assign(
        score=lambda x: x["rating"] * (x["votes"] + 1).pow(0.25)
    ).sort_values("score", ascending=False)

    return filtered.head(top_n)[
        ["restaurant_name", CUISINE_COL, "cost", "rating", "votes", "city"]
    ]

# ----- Show recommendations -----
if st.sidebar.button("Find restaurants"):
    results = simple_filter_rank(df, selected_cuisines, selected_city, selected_budget)

    st.subheader("Recommended Restaurants")

    if results.empty:
        st.warning("No restaurants match your preferences.")
    else:
        for _, row in results.iterrows():
            st.markdown(f"### {row['restaurant_name']}")
            st.markdown(f"- **Cuisine**: {row[CUISINE_COL].title()}")
            st.markdown(f"- **Cost for two**: ₹{int(row['cost'])}")
            st.markdown(f"- **Rating**: {row['rating']} ⭐ ({int(row['votes'])} votes)")
            st.markdown(f"- **City**: {row['city']}")
            st.markdown("---")
