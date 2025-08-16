
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

st.set_page_config(page_title="EV Market Insights", layout="wide")

@st.cache_data
def load_data():
    geo = pd.read_csv("ev_geo_data.csv")
    concerns = pd.read_csv("ev_concerns_sample.csv")
    return geo, concerns

geo, concerns = load_data()

st.title("🔌 EV Market Insights Dashboard")
st.caption("Predictive EV sales by geography + buyer concern signals (mock demo dataset)")

# Sidebar filters (Austin-first default)
state_opts = ["ALL"] + sorted(geo['state'].unique())

# Default to Texas on first load if available
default_state = "TX" if "TX" in state_opts else "ALL"
state_index = state_opts.index(default_state) if default_state in state_opts else 0
state = st.sidebar.selectbox("Select state", options=state_opts, index=state_index, key="state_select")

# Build city options based on selected state, default to Austin if TX
if state != "ALL":
    city_options_raw = sorted(geo[geo['state'] == state]['city'].unique())
else:
    city_options_raw = sorted(geo['city'].unique())
city_opts = ["ALL"] + city_options_raw

default_city = "Austin" if state == "TX" and "Austin" in city_opts else "ALL"
city_index = city_opts.index(default_city) if default_city in city_opts else 0
city = st.sidebar.selectbox("Select city", options=city_opts, index=city_index, key="city_select")

df = geo.copy()
if state != "ALL":
    df = df[df["state"] == state]
if city != "ALL":
    df = df[df["city"] == city]

# Metrics
total_pred_sales = int(df["predicted_ev_sales_next_12m"].sum())
avg_income = int(df["median_income"].mean())
avg_stations = int(df["charging_stations"].mean())

c1, c2, c3 = st.columns(3)
c1.metric("Predicted EV sales (next 12m)", f"{total_pred_sales:,}")
c2.metric("Median income (avg)", f"${avg_income:,}")
c3.metric("Charging stations (avg)", f"{avg_stations:,}")

# Map: circles sized by predicted sales
st.subheader("Geographic opportunity map")
layer = pdk.Layer(
    "ScatterplotLayer",
    df,
    get_position=["lon", "lat"],
    get_radius="predicted_ev_sales_next_12m",
    radius_scale=5,
    radius_min_pixels=3,
    radius_max_pixels=60,
    get_fill_color=[30, 144, 255, 160],
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=float(df["lat"].mean()) if len(df) else 39.5,
    longitude=float(df["lon"].mean()) if len(df) else -98.35,
    zoom=8 if city != "ALL" else (5 if state != "ALL" else 3.5),
    pitch=0
)

st.pydeck_chart(pdk.Deck(map_style=None, initial_view_state=view_state, layers=[layer],
                         tooltip={"text": "ZIP: {zip}\nCity: {city}\nPredicted sales: {predicted_ev_sales_next_12m}"}))

# Top ZIPs table + download
st.subheader("Top ZIP codes by predicted EV sales")
top_k = st.sidebar.slider("Top ZIPs to highlight", 3, 10, 5, key="topk_slider")
top_df = df[["zip","city","state","population","median_income","charging_stations","predicted_ev_sales_next_12m"]]\
            .sort_values("predicted_ev_sales_next_12m", ascending=False).head(top_k)\
            .rename(columns={
                "zip":"ZIP","city":"City","state":"State",
                "population":"Population","median_income":"Median income",
                "charging_stations":"Charging stations","predicted_ev_sales_next_12m":"Predicted sales (12m)"
            })
st.dataframe(top_df, use_container_width=True)

# Download button for Top ZIPs
csv_bytes = top_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Top ZIPs (CSV)",
    data=csv_bytes,
    file_name="top_zips.csv",
    mime="text/csv"
)

# Concerns
st.subheader("Buyer concerns & sentiment")
conc = concerns.copy()
if state != "ALL":
    conc = conc[conc["state"] == state]
if city != "ALL":
    conc = conc[conc["city"] == city]

conc_agg = conc.groupby("concern", as_index=False).agg(
    mention_count=("mention_count","sum"),
    avg_sentiment=("avg_sentiment","mean")
).sort_values("mention_count", ascending=False)

c_bar, c_kpi = st.columns([2,1])
with c_bar:
    st.bar_chart(conc_agg.set_index("concern")["mention_count"], use_container_width=True)
with c_kpi:
    st.write("**Avg sentiment by concern** (−1 to +1)")
    st.dataframe(conc_agg[["concern","avg_sentiment"]].round(2), use_container_width=True)

# Simple, rule-based recommendations
st.subheader("Business recommendations")
recs = []
if len(top_df):
    z = top_df.iloc[0]
    recs.append(f"Prioritize campaign in **ZIP {z['ZIP']} ({z['City']}, {z['State']})** with predicted **{int(z['Predicted sales (12m)'])}** sales.")
if len(conc_agg):
    top_concern = conc_agg.iloc[0]["concern"]
    recs.append(f"Address **{top_concern.lower()}** in targeted messaging; it's the most discussed barrier in the selected region.")
if (df["charging_stations"].mean() < 80) and (df["median_income"].mean() > 80000):
    recs.append("Partner with charging providers: high income but below-average charging density suggests infra-driven lift.")
if df["ev_share"].mean() < 0.12:
    recs.append("Run education webinars with dealerships to build buyer confidence and improve dealer knowledge scores.")

if not recs:
    recs = ["Maintain current strategy; no strong constraints detected. Continue monitoring sentiment and infra density."]

for r in recs:
    st.markdown(f"- {r}")

st.divider()
with st.expander("ℹ️ About this demo / BI talking points", expanded=False):
    st.markdown(
        """
        **Purpose:** Identify *where* to focus EV campaigns and *what* buyer barriers to address.

        **Data signals (mock):** Demographics (population, income), ICE vs EV share, charging density, and aggregated concern mentions.

        **How to use:** Filter by state/city → review *Top ZIPs* + *concerns* → use recommendations for campaign briefs.

        **BI angle:** This can back a Power BI/Tableau dashboard. Replace CSVs with AFDC/Census feeds; add XGBoost/Prophet for forecasting.

        **Next steps:** Enrich with incentive data, charger gap analysis, and cohort retention to estimate CLV uplift.
        """
    )

st.caption("Note: Mock dataset for interview demo. Replace CSVs with real sources post-interview.")

st.set_page_config(page_title="EV Market Insights – Subash", layout="wide")
st.caption("By Subash Shrestha • Data Science & BI • Austin, TX")
