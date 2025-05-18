import streamlit as st
import pandas as pd

st.set_page_config(page_title="Undervalued Streets Dashboard", layout="wide")
st.title("🏘️ Undervalued Streets - UK Property Insights")

@st.cache_data
def load_data():
    df = pd.read_csv("zoopla_streets_enriched.csv")
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df["avg_price"] = pd.to_numeric(df["avg_price"], errors="coerce")
    df["district_median"] = pd.to_numeric(df["district_median"], errors="coerce")
    df["% Difference"] = pd.to_numeric(df["% Difference"], errors="coerce")
    df["transaction_count"] = pd.to_numeric(df["transaction_count"], errors="coerce")
    df["district"] = df["District"]
    return df.dropna(subset=["Latitude", "Longitude", "avg_price", "district_median"])

df = load_data()

# Sidebar filters
st.sidebar.header("📊 Filter Results")
districts = ["All"] + sorted(df["district"].dropna().unique())
selected_district = st.sidebar.selectbox("Select District", districts)
min_txn = st.sidebar.slider("Min Transactions", 1, 30, 3)
price_range = st.sidebar.slider("Average Price (£)", 0, 1_000_000, (0, 1_000_000), step=10_000)
pct_diff_range = st.sidebar.slider("% Difference vs Median", 20, 100, (20, 40))

# Apply filters
filtered_df = df.copy()
if selected_district != "All":
    filtered_df = filtered_df[filtered_df["district"] == selected_district]

filtered_df = filtered_df[
    (filtered_df["avg_price"] >= price_range[0]) &
    (filtered_df["avg_price"] <= price_range[1]) &
    (filtered_df["transaction_count"] >= min_txn) &
    (filtered_df["% Difference"] >= pct_diff_range[0]) &
    (filtered_df["% Difference"] <= pct_diff_range[1])
]

# Session state for favourites
if "favourites" not in st.session_state:
    st.session_state.favourites = set()

# Render row card
def show_property_rows(dataframe, allow_fav_toggle=True, tab_id="main"):
    headers = st.columns([4, 2, 2, 1, 1, 1])
    headers[0].markdown("**Street**")
    headers[1].markdown("**Avg Price**")
    headers[2].markdown("**Median**")
    headers[3].markdown("**Sales**")
    headers[4].markdown("**% Diff**")
    headers[5].markdown("**Favourite**")

    for idx, row in dataframe.iterrows():
        row_id = f"{row['postcode']}_{row['street_key'].replace(' ', '_')}_{idx}_{tab_id}"

        st.markdown("---")
        cols = st.columns([4, 2, 2, 1, 1, 1])
        with cols[0]:
            st.markdown(f"**🏘️ {row['street_key']}**")
        with cols[1]:
            st.markdown(f"£{int(row['avg_price']):,}")
        with cols[2]:
            st.markdown(f"£{int(row['district_median']):,}")
        with cols[3]:
            st.markdown(f"{int(row['transaction_count'])} sales")
        with cols[4]:
            st.markdown(f"{row['% Difference']:.1f}%")
        with cols[5]:
            if allow_fav_toggle:
                fav_state = row_id in st.session_state.favourites
                toggle = st.toggle("", value=fav_state, key=f"fav_{row_id}")
                if toggle and not fav_state:
                    st.session_state.favourites.add(row_id)
                elif not toggle and fav_state:
                    st.session_state.favourites.remove(row_id)

        map_key = f"map_{row_id}_btn"
        if st.button("📍 See on Map", key=map_key):
            st.map(pd.DataFrame({"latitude": [row["Latitude"]], "longitude": [row["Longitude"]]}), zoom=12)

        with st.expander("🔎 Local Insights"):
            postcode = row["postcode"].replace(" ", "+")
            bcol1, bcol2, bcol3 = st.columns(3)
            with bcol1:
                st.link_button("🏫 Schools Nearby", f"https://www.google.com/search?q=schools+near+{postcode}")
                st.link_button("🏥 Hospitals Nearby", f"https://www.google.com/search?q=hospitals+near+{postcode}")
            with bcol2:
                st.link_button("🚉 Train Stations", f"https://www.google.com/search?q=train+stations+near+{postcode}")
                st.link_button("🏗️ Developments", f"https://www.google.com/search?q=future+developments+near+{postcode}")
            with bcol3:
                st.link_button("🏘️ HMO Licensing", f"https://www.google.com/search?q=HMO+licensing+{postcode}")

# Tabs
tab1, tab2 = st.tabs(["🔍 All Results", "⭐ Favourites Only"])

with tab1:
    st.markdown("## 📋 All Matching Undervalued Streets")
    st.markdown(f"### 💷 Showing {len(filtered_df)} undervalued streets")
    if not filtered_df.empty:
        show_property_rows(filtered_df, tab_id="main")
    else:
        st.warning("No results found. Try adjusting your filters.")

with tab2:
    fav_keys = list(st.session_state.favourites)
    fav_df = df[df.apply(lambda row: any(f"{row['postcode']}_{row['street_key'].replace(' ', '_')}" in fav_key for fav_key in fav_keys), axis=1)]
    st.markdown("## ⭐ Your Favourited Streets")
    st.markdown(f"### 💾 You have saved {len(fav_df)} favourite streets")
    if not fav_df.empty:
        show_property_rows(fav_df, allow_fav_toggle=False, tab_id="fav")
    else:
        st.info("You haven’t favourited any streets yet.")
