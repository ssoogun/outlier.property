# Streamlit dashboard for undervalued UK streets
# Run with: streamlit run undervalued_dashboard.py

import streamlit as st
import pandas as pd

# Load processed dataset (assumed to be prepared by backend logic)
df = pd.read_csv("zoopla_ai_flagged_streets.csv")  # Replace with actual filename if different

st.set_page_config(page_title="Undervalued Streets Dashboard", layout="wide")
st.title("🏘️ Undervalued Streets - UK Property Insights")

st.markdown("""
This dashboard uses HM Land Registry data to identify UK streets where the average sale price
is 20% or more below the district median — highlighting areas with potential undervalued deals.
""")

# Sidebar filters
with st.sidebar:
    st.header("📊 Filter Results")
    selected_district = st.multiselect(
        "Filter by District (Postcode)",
        options=sorted(df["district"].dropna().unique()),
        default=[]
    )

    min_txn = st.slider("Minimum Transactions", 1, 20, 3)
    max_price = st.number_input("Max Average Price (£)", value=1000000)

# Apply filters
filtered_df = df.copy()

if selected_district:
    filtered_df = filtered_df[filtered_df["district"].isin(selected_district)]

filtered_df = filtered_df[
    (filtered_df["transaction_count"] >= min_txn) &
    (filtered_df["avg_price"] <= max_price)
]

# Format numeric columns (round + comma)
filtered_df["avg_price"] = filtered_df["avg_price"].round(0).astype(int).map("{:,}".format)
filtered_df["district_median"] = filtered_df["district_median"].round(0).astype(int).map("{:,}".format)

# Display table
st.markdown(f"### 💷 Showing {len(filtered_df)} undervalued streets")

if not filtered_df.empty:
    # Add external hyperlink to Zoopla
    def create_link(postcode):
        return f"[https://www.zoopla.co.uk](https://www.zoopla.co.uk/for-sale/property/?q={postcode})"

    filtered_df["zoopla_link"] = filtered_df["street_key"].apply(lambda s: create_link(s.split("|")[-1].strip()))

    st.dataframe(
        filtered_df[["street_key", "avg_price", "district_median", "transaction_count", "zoopla_link"]]
        .rename(columns={
            "street_key": "Street + Postcode",
            "avg_price": "Avg Price (£)",
            "district_median": "District Median (£)",
            "transaction_count": "Sales Count",
            "zoopla_link": "Live Listings"
        }),
        use_container_width=True
    )
else:
    st.warning("No results found. Try adjusting your filters.")
