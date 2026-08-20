# Exploratory Data Analysis (EDA) Report

## 1. Overview
This EDA is based on the cleaned `bus_stop_optimization_dataset_15000_cleaned.csv` containing 15,000 synthetically generated urban bus stop profiles.

## 2. Missing Value Analysis
- **Missing Values**: 0 missing values in all features. The dataset is fully populated.

## 3. Passenger Demand Distributions
- **Passenger_Count**:
  - Mean: ~60 passengers
  - Range: 20 to 100 passengers
  - The distribution is uniform, indicating a synthesized spread of low to high-demand scenarios.
- **Boarding**:
  - Mean: ~20 passengers
  - Range: 5 to 50
- **Alighting**:
  - Mean: ~20 passengers
  - Range: 5 to 40

## 4. Traffic & Road Analysis
- **Traffic Level**: Categorical distribution is perfectly even across `Low`, `Moderate`, and `High`.
- **Road Width**: 
  - Mean: ~12 meters
  - Range: 6 to 24 meters
  - Most roads easily accommodate a bus (which typically needs >3-3.5m per lane).

## 5. Frequency & Stop Spacing
- **Bus Frequency**: 
  - Mean: ~15 mins
  - Range: 5 to 30 mins
- **Waiting Time**:
  - Mean: ~10 mins
  - Range: 2 to 20 mins
- **Distance to Next Stop**: 
  - Mean: 1,250 meters
  - Range: 300 to 3,000 meters
  - This spacing aligns well with urban transport standards (usually ~400m to 1km).

## 6. Correlation Analysis & Feature Relationships
- `Passenger_Count` is perfectly explained by the sum of `Boarding` + `Alighting` + existing bus load, showing consistent synthetic generation.
- No significant internal multicollinearity among environmental features (Traffic, Road Width, Distance), which is ideal for a suitability algorithm.

## 7. Geographic Visualization
- **Latitude Range**: 13.00 to 13.08
- **Longitude Range**: 77.50 to 77.65
- *Note*: These coordinates correspond roughly to Bengaluru, India. Plotting these confirms they form a grid or linear paths within this bounding box.

## 8. Existing Target Leakage Analysis
As established in the Phase 1 Audit, the `Optimal_Stop` binary flag was fully compromised by target leakage (Corr(Optimal_Stop, Passenger_Count) = 0.81). It has been successfully removed in Phase 2 to ensure true multi-factor analysis can occur without bias.
