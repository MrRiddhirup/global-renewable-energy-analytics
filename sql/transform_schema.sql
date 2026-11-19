DROP TABLE IF EXISTS Fact_Energy_Metrics;
CREATE TABLE Fact_Energy_Metrics AS
SELECT
    TRIM(Country_Code) AS Country_Code,
    TRIM(Country_Name) AS Country_Name,
    TRIM(Region) AS Region,
    TRIM(Income_Group) AS Income_Group,
    CAST(Year AS INTEGER) AS Year,
    TRIM(Sector) AS Sector,
    COALESCE(Total_Primary_Energy_TWh, 0.0) AS Total_Primary_Energy_TWh,
    COALESCE(Renewable_Generation_TWh, 0.0) AS Renewable_Generation_TWh,
    COALESCE(Fossil_Generation_TWh, 0.0) AS Fossil_Generation_TWh,
    COALESCE(Grid_Capacity_GW, 0.0) AS Grid_Capacity_GW,
    COALESCE(CO2_Emissions_Mt, 0.0) AS CO2_Emissions_Mt,
    COALESCE(Green_Capex_USD_M, 0.0) AS Green_Capex_USD_M,
    COALESCE(Energy_Import_Dependency_Pct, 0.0) AS Energy_Import_Dependency_Pct,
    COALESCE(Industrial_GDP_Share_Pct, 0.0) AS Industrial_GDP_Share_Pct,
    CASE
        WHEN Total_Primary_Energy_TWh <= 0 THEN 'Emerging (<15%)'
        WHEN (Renewable_Generation_TWh * 1.0 / Total_Primary_Energy_TWh) < 0.15 THEN 'Emerging (<15%)'
        WHEN (Renewable_Generation_TWh * 1.0 / Total_Primary_Energy_TWh) < 0.40 THEN 'Transitioning (15%-40%)'
        WHEN (Renewable_Generation_TWh * 1.0 / Total_Primary_Energy_TWh) < 0.70 THEN 'Advanced (40%-70%)'
        ELSE 'Green Leader (>70%)'
    END AS Transition_Phase
FROM Raw_Energy_Metrics
GROUP BY Country_Code, Year, Sector;

DROP TABLE IF EXISTS Dim_Country;
CREATE TABLE Dim_Country AS
SELECT DISTINCT Country_Code, Country_Name, Region, Income_Group
FROM Fact_Energy_Metrics;

DROP TABLE IF EXISTS Dim_Time;
CREATE TABLE Dim_Time AS
SELECT DISTINCT Year, DATE(Year || '-12-31') AS Date_End
FROM Fact_Energy_Metrics
ORDER BY Year;
