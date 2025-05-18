# 🏘️ Undervalued Streets - UK Property Insights

This Streamlit dashboard uses real UK property sales data to identify streets where the **average house price is significantly lower than the district median** — highlighting potentially undervalued investment opportunities.

## 🚀 Features

- 🔍 **Filter by district**, transaction count, price range, and % below median
- ⭐ **Save favourite streets** for later viewing
- 🗺️ **"See on Map"** button to visualise property location
- 📍 Expandable **local insights**: schools, hospitals, train stations, future developments, and HMO licensing
- 💾 All processing is local and instant — no waiting

## 📦 Folder Contents

```bash
.
├── app.py                     # Main Streamlit app
├── zoopla_streets_enriched.csv  # Preprocessed data file with lat/lon and % Difference
├── requirements.txt           # Dependencies
└── README.md                  # This file
