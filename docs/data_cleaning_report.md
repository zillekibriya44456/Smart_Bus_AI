# Data Cleaning Report

## 1. Overview
This document outlines the data cleaning procedures applied to the two raw datasets. The original datasets are strictly preserved in `data/raw/` and all cleaned datasets are saved in `data/cleaned/`.

## 2. Dataset 1: Large Optimization Dataset (CSV)
- **Input**: `data/raw/bus_stop_optimization_dataset_15000.csv`
- **Output**: `data/cleaned/bus_stop_optimization_dataset_15000_cleaned.csv`

### Transformations Applied:
1. **Target Leakage Mitigation**: The `Optimal_Stop` column was explicitly dropped. As discovered in Phase 1, it was synthetically derived from passenger count metrics and constitutes a severe target leak.
2. **Coordinate Validation**: Validated Latitude [-90, 90] and Longitude [-180, 180]. 
3. **Numeric Range Validation**: Validated `Passenger_Count` to ensure non-negative values.

### Quality Summary:
- **Initial Rows**: 15,000
- **Final Rows**: 15,000
- **Dropped Rows**: 0 (all constraints passed).
- **Columns Removed**: 1 (`Optimal_Stop`).

## 3. Dataset 2: Sample Optimization Data (Excel)
- **Input**: `data/raw/jaydwip das bus optimization data.xlsx`
- **Output**: `data/cleaned/jaydwip_das_bus_optimization_data_cleaned.csv`

### Transformations Applied:
1. **Dropped Unnamed/Blank Columns**: Removed `Unnamed: 0` and `Unnamed: 2` which contained no useful data.
2. **Invalid Record Removal**: Dropped 1 empty row where `Bus_Stop_Name` was null.
3. **Repeated Header Removal**: Dropped 1 row containing repeated column names inside the data (e.g., `Passenger_Count` = "Passenger_Count").
4. **Data Type Coercion**: Converted all feature columns (Latitude, Longitude, Width, Distance, Passenger Metrics, wait times) to true numeric types (`float64`). Invalid string characters were converted to `NaN`.

### Quality Summary:
- **Initial Rows**: 24
- **Final Rows**: 22
- **Dropped Rows**: 2 (1 missing name, 1 repeated header).
- **Columns Removed**: 2 (Unnamed cols).

**Note on Immutability**: All logic is wrapped into the reusable `ml/preprocessing/clean_and_eda.py` pipeline. No manual modifications were made to Excel or CSV files.
