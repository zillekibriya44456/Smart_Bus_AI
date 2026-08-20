# Data Audit Report

## 1. Executive Summary

This report documents the initial data audit performed on the two provided datasets:
1. `bus_stop_optimization_dataset_15000.csv` (Synthetic/Large Dataset)
2. `jaydwip das bus optimization data.xlsx` (Small/Real-world Sample)

**Critical Finding**: There is severe **target leakage** in the `bus_stop_optimization_dataset_15000.csv` dataset. The target variable `Optimal_Stop` appears to be synthetically generated using a direct hardcoded threshold rule based on `Passenger_Count` and `Boarding`.

---

## 2. Dataset 1: `bus_stop_optimization_dataset_15000.csv`

### General Information
- **Rows**: 15,000
- **Columns**: 23
- **Data Types**: 
  - Numeric: 14 columns
  - Categorical: 9 columns
- **Missing Values**: 0 missing values across all columns.
- **Duplicates**: 0 duplicate rows.

### Descriptive Statistics (Numeric)
- **Passenger_Count**: Ranges from 20 to 100.
- **Walking_Distance_m**: Ranges from 50 to 500m.
- **Occupancy_pct**: Ranges from 20% to 100%.

### Target Leakage Analysis (CRITICAL)
The target variable `Optimal_Stop` is highly correlated with simple passenger metrics:
- **Correlation with Passenger_Count**: `0.81`
- **Correlation with Boarding**: `0.57`

**Averages by Optimal_Stop:**
- **Optimal_Stop = No**: Average Passenger_Count = 36.2
- **Optimal_Stop = Yes**: Average Passenger_Count = 64.3
- **Optimal_Stop = No**: Average Boarding = 13.4
- **Optimal_Stop = Yes**: Average Boarding = 27.0

**Conclusion**: The `Optimal_Stop` feature was likely generated using a simple mathematical rule (e.g., `IF Passenger_Count > X THEN Yes ELSE No`). Training an ML model on this target is meaningless, as it will just learn this hardcoded rule.

---

## 3. Dataset 2: `jaydwip das bus optimization data.xlsx`

### General Information
- **Sheet**: `Sheet1`
- **Rows**: 24
- **Columns**: 34
- **Data Types**: Most numeric columns (e.g., `Passenger_Count`, `Boarding`, `Alighting`) were parsed as `object` (strings).
- **Missing Values**: Nearly every column has 1 missing value (likely an empty row). `Unnamed: 0` and `Unnamed: 2` have 24 missing values.
- **Duplicates**: 0 duplicate rows.

### Data Inconsistencies & Issues
- **Invalid Data Types**: The presence of string characters in numeric columns (like `Passenger_Count`) caused Pandas to treat them as objects. This indicates either repeated headers inside the data, 'N/A' strings, or special characters.
- **Empty Columns**: Columns like `Unnamed: 0` and `Unnamed: 2` are completely empty or garbage columns.
- **Missing Rows**: There is an empty row or a purely descriptive row that needs to be dropped.

---

## 4. Recommendations & Next Steps

### Data Cleaning Strategy
1. **CSV Dataset**: Use this as the primary dataset but discard the existing `Optimal_Stop` column.
2. **Excel Dataset**: 
   - Drop `Unnamed` columns.
   - Drop the empty/invalid row.
   - Coerce numeric columns to actual numeric types, turning invalid strings into `NaN`, then impute or drop.

### New Suitability Scoring Strategy (Addressing Target Leakage)
Instead of predicting a synthetically leaked `Optimal_Stop` binary flag, we must create a **Multi-Factor Suitability Score (0-100)**:
- **Demand Score (30%)**: Based on `Passenger_Count`, `Boarding`, `Alighting`.
- **Accessibility Score (20%)**: Based on `Walking_Distance_m`, `Distance_to_Next_Stop_m`.
- **Infrastructure Score (20%)**: Based on `Road_Width`, existing `Bus_Shelter`.
- **Traffic/Safety Score (30%)**: Based on `Traffic_Level`, `Occupancy_pct`.

We will then derive `Suitability_Category` from this score (e.g., >80 is Highly Suitable). 

### Final Architecture Proposal
We will implement the requested Phase architecture:
- **Phase 1**: (Completed) Data Audit.
- **Phase 2**: Data Cleaning scripts to fix the Excel issues and standardize the CSV.
- **Phase 3**: EDA generation.
- **Phase 4**: Rule-based Suitability Engine calculating the multi-factor score.
- **Phase 5**: ML models predicting the new `Suitability_Score` (Regression) and `Suitability_Category` (Classification) without target leakage.
- **Phase 6-10**: Building the FastAPI backend and React frontend to expose this logic.
