from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd

np.random.seed(42)

base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / "data"
data_dir.mkdir(exist_ok=True)

countries = [
    ("NOR", "Norway", "Europe", "High Income", 0.96, 150, 45),
    ("ISL", "Iceland", "Europe", "High Income", 0.99, 20, 3.5),
    ("DEU", "Germany", "Europe", "High Income", 0.52, 3200, 620),
    ("USA", "United States", "North America", "High Income", 0.24, 25000, 4800),
    ("CHN", "China", "Asia-Pacific", "Upper Middle Income", 0.32, 42000, 11400),
    ("IND", "India", "Asia-Pacific", "Lower Middle Income", 0.22, 10500, 2800),
    ("BRA", "Brazil", "Latin America", "Upper Middle Income", 0.85, 3600, 460),
    ("JPN", "Japan", "Asia-Pacific", "High Income", 0.23, 4800, 1050),
    ("GBR", "United Kingdom", "Europe", "High Income", 0.45, 1900, 320),
    ("ZAF", "South Africa", "Sub-Saharan Africa", "Upper Middle Income", 0.11, 1400, 430),
]

years = range(2012, 2027)
sectors = ["Residential", "Industrial", "Commercial", "Transport", "Grid Utility"]
mults = {"Industrial": 1.6, "Grid Utility": 1.4, "Transport": 1.1, "Residential": 0.6, "Commercial": 0.5}

rows = []
for i in range(142):
    c = countries[i % len(countries)]
    code = c[0] if i < len(countries) else f"C{100 + i}"
    name = c[1] if i < len(countries) else f"{c[1]}_Zone_{i}"
    region, income, ren_base = c[2], c[3], c[4]
    energy_base, co2_base = c[5] / 5.0, c[6] / 5.0

    for yr in years:
        offset = yr - 2012
        ren_share = min(0.99, max(0.01, ren_base * (1 + 0.045 * offset) + np.random.normal(0, 0.015)))
        for sec in sectors:
            m = mults[sec]
            total_e = round(energy_base * m * (1 + 0.02 * offset) * np.random.uniform(0.92, 1.08), 2)
            ren_e = round(total_e * ren_share, 2)
            fos_e = round(total_e - ren_e, 2)
            grid_gw = round((total_e / 8.76) * np.random.uniform(1.8, 2.4), 2)
            co2_factor = 1 - (0.025 * offset) if ren_share > 0.40 else 1 + (0.015 * offset)
            co2 = round(max(0.5, co2_base * m * co2_factor * np.random.uniform(0.9, 1.1)), 2)
            capex = round((ren_e * 1.85) * (1 + 0.06 * offset) * np.random.uniform(0.8, 1.3), 2)
            imp = round(min(95.0, max(2.0, (1 - ren_share) * 65 + np.random.normal(0, 8))), 1)
            gdp = round(np.random.uniform(18.0, 42.0), 1)
            rows.append([code, name, region, income, yr, sec, total_e, ren_e, fos_e, grid_gw, co2, capex, imp, gdp])

cols = [
    "Country_Code", "Country_Name", "Region", "Income_Group", "Year", "Sector",
    "Total_Primary_Energy_TWh", "Renewable_Generation_TWh", "Fossil_Generation_TWh",
    "Grid_Capacity_GW", "CO2_Emissions_Mt", "Green_Capex_USD_M",
    "Energy_Import_Dependency_Pct", "Industrial_GDP_Share_Pct"
]

df = pd.DataFrame(rows, columns=cols)

df = pd.concat([df, df.sample(frac=0.012, random_state=42)], ignore_index=True)
messy = df.sample(frac=0.08, random_state=42).index
df.loc[messy, "Country_Name"] = "  " + df.loc[messy, "Country_Name"].str.lower() + "  "
df.loc[messy, "Region"] = df.loc[messy, "Region"].str.upper()
df.loc[df.sample(frac=0.04, random_state=10).index, "Green_Capex_USD_M"] = np.nan
df.loc[df.sample(frac=0.03, random_state=20).index, "CO2_Emissions_Mt"] = np.nan

df.to_csv(data_dir / "GETER_2026_Raw_Dataset.csv", index=False)
with sqlite3.connect(data_dir / "energy_warehouse.db") as conn:
    df.to_sql("Raw_Energy_Metrics", conn, if_exists="replace", index=False)

print("Done! CSV and SQLite database created.")
