# EV Market Insights – Interview Demo

A BI-facing demo that predicts EV sales by geography and highlights buyer adoption concerns. Built for a fast interview demo with mock-but-realistic data.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## What to demo
- **Map + Top ZIPs:** Where to focus campaigns (predicted sales next 12 months).
- **Concerns:** What to address in messaging (range anxiety, cost, charging access).
- **Recommendations:** Auto-generated talking points for stakeholders.
- **Download:** Use the **Download Top ZIPs (CSV)** button to export targets for campaign lists.

## Talking track (BI leader)
- **Business first:** We start from the decision—where to invest marketing—and wire up the minimal signals.
- **Actionable now, deeper later:** Demo uses simple scoring/aggregation; ready to swap in AFDC/Census + XGBoost/Prophet.
- **Integrates with BI:** Expose a small API (FastAPI) to serve predictions to Power BI/Tableau. Schedule daily refresh.

## Data
- `ev_geo_data.csv`: ZIP-level demographics, charging density, EV/ICE share, and predicted sales (mock).
- `ev_concerns_sample.csv`: Aggregated mentions & sentiment of common EV barriers (mock).

## Roadmap (post-interview)
1. Replace mock CSVs with real DOE AFDC, Census, and fuel price feeds.
2. Train gradient-boosted models and Prophet for time-series forecasting.
3. Add charger gap analysis & policy impact attribution.
4. Ship as a Cloudflare-friendly API + dashboard (or embed into existing BI).
