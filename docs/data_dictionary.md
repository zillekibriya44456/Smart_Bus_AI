# Data Dictionary

## 1. Synthetic Dataset: `bus_stop_optimization_dataset_15000.csv`

| Column Name | Data Type | Description | Issues / Notes |
|---|---|---|---|
| Passenger_ID | int64 | Unique ID for passenger | |
| Stop_ID | string | Identifier for the bus stop | |
| Latitude | float64 | Geographic latitude | |
| Longitude | float64 | Geographic longitude | |
| Boarding | int64 | Number of passengers boarding | Correlated with Optimal_Stop |
| Alighting | int64 | Number of passengers alighting | |
| Passenger_Count | int64 | Total passenger demand | Highly correlated with Optimal_Stop |
| Time | string | Time of day | |
| Day | string | Day of the week | |
| Weather | string | Weather conditions | |
| Traffic_Level | string | Categorical traffic severity | |
| Road_Width | int64 | Width of road in meters | |
| Population_Density | int64 | Local population density | |
| Land_Use | string | Type of local area (Residential, Commercial, etc.) | |
| Distance_to_Next_Stop_m | int64 | Distance to the next bus stop in meters | |
| Bus_Frequency | int64 | Frequency of buses arriving | |
| Waiting_Time_min | int64 | Average waiting time | |
| Bus_Dwell_Time_sec | int64 | Time bus spends at the stop | |
| Walking_Distance_m | int64 | Pedestrian access distance | |
| Occupancy_pct | int64 | Bus occupancy percentage | |
| Peak_Hour | string | Yes/No flag for peak hours | |
| Bus_Route | string | Route identifier | |
| Optimal_Stop | string | Yes/No synthetic target label | **DO NOT USE (Target Leakage)** |

---

## 2. Real-world Dataset: `jaydwip das bus optimization data.xlsx`

| Column Name | Data Type | Description | Issues / Notes |
|---|---|---|---|
| Unnamed: 0 | N/A | Empty column | To be dropped |
| Bus_Stop_Name | string | Name of the bus stop | |
| Unnamed: 2 | N/A | Empty column | To be dropped |
| Sequence | string/numeric | Sequence of stop | Contains invalid strings |
| Latitude_Est | string/numeric| Geographic latitude | Contains invalid strings |
| Longitude_Est | string/numeric| Geographic longitude | Contains invalid strings |
| Road_Width_m | string/numeric| Width of the road | Contains invalid strings |
| Distance_to_Next_Stop_m | string/numeric| Distance to next stop | Contains invalid strings |
| Boarding | string/numeric| Passengers boarding | Contains invalid strings |
| Alighting | string/numeric| Passengers alighting | Contains invalid strings |
| Passenger_Count | string/numeric| Total passenger demand | Contains invalid strings |
| Peak_Hour_Passengers | string/numeric| Peak hour demand | Contains invalid strings |
| Traffic_Level | string | Categorical traffic level | |
| School_Nearby | string/numeric| Proximity flag | Contains invalid strings |
| College_Nearby | string/numeric| Proximity flag | Contains invalid strings |
| Industry_Nearby | string/numeric| Proximity flag | Contains invalid strings |
| Hospital_Nearby | string/numeric| Proximity flag | Contains invalid strings |
| Residential_Nearby | string/numeric| Proximity flag | Contains invalid strings |
| Commercial_Nearby | string/numeric| Proximity flag | Contains invalid strings |
| Bus_Shelter | string | Yes/No | |
| Seating | string | Yes/No | |
| Street_Lighting | string | Yes/No | |
| Footpath | string | Yes/No | |
| Zebra_Crossing | string | Yes/No | |
| Bus_Bay | string | Yes/No | |
| Walking_Distance_m | string/numeric| Pedestrian access distance | Contains invalid strings |
| Waiting_Time_min | string/numeric| Wait time | Contains invalid strings |
| Dwell_Time_sec | string/numeric| Dwell time | Contains invalid strings |
| Population_Density_persons_km2 | string/numeric| Population density | Contains invalid strings |
| Land_Use | string | Zone category | |
| Safety_Score_0_100 | string/numeric| Existing safety score | Contains invalid strings |
| Accessibility_Score_0_100 | string/numeric| Existing accessibility score | Contains invalid strings |
| Optimal_Stop | string | Synthetic Target | To be dropped/ignored |
| Data_Status | string | Notes on data source | |
