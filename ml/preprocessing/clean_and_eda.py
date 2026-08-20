"""
Data preprocessing and EDA script for the Smart Bus Stop dataset.

Usage (from the project root):
    python ml/preprocessing/clean_and_eda.py

Outputs:
    data/cleaned/bus_stop_optimization_dataset_15000_cleaned.csv
    data/cleaned/jaydwip_das_bus_optimization_data_cleaned.csv
    scratch/eda_stats.json
"""
import json
import logging
import os
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Paths (relative to project root, never absolute) ──────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_CSV    = PROJECT_ROOT / "data" / "raw" / "bus_stop_optimization_dataset_15000.csv"
RAW_EXCEL  = PROJECT_ROOT / "data" / "raw" / "jaydwip das bus optimization data.xlsx"
CLEAN_CSV  = PROJECT_ROOT / "data" / "cleaned" / "bus_stop_optimization_dataset_15000_cleaned.csv"
CLEAN_EXCEL= PROJECT_ROOT / "data" / "cleaned" / "jaydwip_das_bus_optimization_data_cleaned.csv"
EDA_JSON   = PROJECT_ROOT / "scratch" / "eda_stats.json"


def clean_csv() -> pd.DataFrame:
    """Clean the primary 15,000-row CSV dataset."""
    logger.info("--- Cleaning CSV Dataset ---")
    df = pd.read_csv(RAW_CSV)
    initial_rows = len(df)

    # Drop Optimal_Stop to prevent target leakage
    if "Optimal_Stop" in df.columns:
        df = df.drop(columns=["Optimal_Stop"])
        logger.info("Dropped 'Optimal_Stop' to prevent target leakage.")

    # Validate latitude/longitude ranges
    invalid_coords = df[
        (df["Latitude"] < -90) | (df["Latitude"] > 90) |
        (df["Longitude"] < -180) | (df["Longitude"] > 180)
    ]
    if not invalid_coords.empty:
        logger.info("Dropping %d rows with invalid coordinates.", len(invalid_coords))
        df = df.drop(invalid_coords.index)

    # Drop rows with negative passenger counts
    invalid_pax = df[df["Passenger_Count"] < 0]
    if not invalid_pax.empty:
        logger.info("Dropping %d rows with negative Passenger_Count.", len(invalid_pax))
        df = df.drop(invalid_pax.index)

    CLEAN_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_CSV, index=False)
    logger.info(
        "CSV cleaning complete: %d → %d rows (dropped %d).",
        initial_rows, len(df), initial_rows - len(df),
    )
    return df


def clean_excel() -> pd.DataFrame:
    """Clean the supplementary Excel dataset."""
    logger.info("--- Cleaning Excel Dataset ---")
    df = pd.read_excel(RAW_EXCEL)
    initial_rows = len(df)

    # Remove unnamed columns (Excel artefacts)
    unnamed_cols = [c for c in df.columns if "Unnamed" in str(c)]
    df = df.drop(columns=unnamed_cols)
    if unnamed_cols:
        logger.info("Dropped unnamed columns: %s", unnamed_cols)

    # Drop rows where Bus_Stop_Name is missing
    if "Bus_Stop_Name" in df.columns:
        before = len(df)
        df = df.dropna(subset=["Bus_Stop_Name"])
        if len(df) < before:
            logger.info("Dropped %d rows with missing Bus_Stop_Name.", before - len(df))

    # Remove repeated header rows
    if "Passenger_Count" in df.columns:
        repeated = df[df["Passenger_Count"] == "Passenger_Count"]
        if not repeated.empty:
            logger.info("Dropping %d repeated header rows.", len(repeated))
            df = df.drop(repeated.index)

    # Coerce numeric columns
    numeric_cols = [
        "Latitude_Est", "Longitude_Est", "Road_Width_m", "Distance_to_Next_Stop_m",
        "Boarding ", "Alighting", "Passenger_Count", "Peak_Hour_Passengers",
        "Walking_Distance_m", "Waiting_Time_min", "Dwell_Time_sec",
        "Population_Density_persons_km2", "Safety_Score_0_100", "Accessibility_Score_0_100",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Validate coords in Excel dataset
    if "Latitude_Est" in df.columns and "Longitude_Est" in df.columns:
        invalid_coords = df[
            (df["Latitude_Est"] < -90) | (df["Latitude_Est"] > 90) |
            (df["Longitude_Est"] < -180) | (df["Longitude_Est"] > 180)
        ]
        if not invalid_coords.empty:
            logger.info("Dropping %d rows with invalid coords.", len(invalid_coords))
            df = df.drop(invalid_coords.index)

    CLEAN_EXCEL.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_EXCEL, index=False)
    logger.info(
        "Excel cleaning complete: %d → %d rows (dropped %d).",
        initial_rows, len(df), initial_rows - len(df),
    )
    return df


def generate_eda(df_csv: pd.DataFrame, df_excel: pd.DataFrame) -> None:
    """Compute and persist EDA statistics to JSON."""
    logger.info("--- Generating EDA Stats ---")

    eda_stats: dict = {
        "csv": {
            "missing": df_csv.isnull().sum().to_dict(),
            "passenger_demand": df_csv["Passenger_Count"].describe().to_dict(),
            "boarding": df_csv["Boarding"].describe().to_dict(),
            "alighting": df_csv["Alighting"].describe().to_dict(),
            "traffic_dist": df_csv["Traffic_Level"].value_counts().to_dict(),
            "road_width": df_csv["Road_Width"].describe().to_dict(),
            "bus_freq": df_csv["Bus_Frequency"].describe().to_dict(),
            "waiting_time": df_csv["Waiting_Time_min"].describe().to_dict(),
        }
    }

    num_df = df_csv.select_dtypes(include=[np.number])
    eda_stats["csv"]["correlations"] = num_df.corr().to_dict()

    EDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(EDA_JSON, "w", encoding="utf-8") as f:
        json.dump(eda_stats, f, indent=2)

    logger.info("EDA stats written to %s", EDA_JSON)


if __name__ == "__main__":
    df_c = clean_csv()
    df_e = clean_excel()
    generate_eda(df_c, df_e)
