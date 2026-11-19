# Global Renewable Energy Transition & Carbon Macro-Analytics (GETER-2026)

Power BI & SQL analytics project for B.Tech CSE (Data Science).

## How to Run
1. `python scripts/etl_pipeline.py` — generates raw data and loads SQLite (`data/energy_warehouse.db`).
2. Run `sql/transform_schema.sql` — creates clean star-schema tables (`Fact_Energy_Metrics`, `Dim_Country`, `Dim_Time`).
3. Open `data/energy_warehouse.db` in Power BI Desktop to model and build the dashboard.
