"""
GIS (Geographic Information System) utilities.

Provides spatial calculations and feature derivation from raw coordinates
using the Haversine formula and nearest-neighbour interpolation.
"""
import logging
import math
from typing import Dict

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Number of nearest stops used for feature interpolation
_K_NEAREST: int = 3

# Default walking distance when no better estimate is available (metres)
_DEFAULT_WALKING_DISTANCE_M: float = 200.0


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance in metres between two geographic points.

    Args:
        lat1: Latitude of point 1 (decimal degrees).
        lon1: Longitude of point 1 (decimal degrees).
        lat2: Latitude of point 2 (decimal degrees).
        lon2: Longitude of point 2 (decimal degrees).

    Returns:
        Distance in metres.
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * math.asin(math.sqrt(a)) * 6_371_000  # Earth radius in metres


def derive_features_from_coordinates(lat: float, lon: float, df: pd.DataFrame) -> Dict:
    """
    Derive bus stop features for an arbitrary coordinate by interpolating from
    the K nearest existing stops in the dataset.

    Warning:
        The returned values are *estimated* from neighbouring stops.  They
        should be treated as proximity-based approximations, not ground truth.
        The API response marks such results as ``Analysis_Type="Derived"``.

    Args:
        lat: Target latitude.
        lon: Target longitude.
        df:  DataFrame of known bus stops (must contain Latitude, Longitude,
             and all feature columns).

    Returns:
        Dict of derived feature values suitable for passing to
        ``predict_suitability``.
    """
    if df.empty:
        logger.warning("derive_features_from_coordinates called with an empty DataFrame.")
        raise ValueError("Bus stop dataset is empty — cannot derive features.")

    distances = df.apply(
        lambda row: haversine_distance(lat, lon, row["Latitude"], row["Longitude"]),
        axis=1,
    )

    nearest_indices = distances.nsmallest(_K_NEAREST).index
    nearest_stops = df.loc[nearest_indices]
    dist_to_nearest_m = round(float(distances[nearest_indices[0]]), 2)

    logger.debug(
        "Nearest stop distance for (%.4f, %.4f): %.2f m", lat, lon, dist_to_nearest_m
    )

    derived: Dict = {
        "Passenger_Count": int(nearest_stops["Passenger_Count"].mean()),
        "Boarding": int(nearest_stops["Boarding"].mean()),
        "Alighting": int(nearest_stops["Alighting"].mean()),
        "Road_Width": round(float(nearest_stops["Road_Width"].mean()), 1),
        "Walking_Distance_m": _DEFAULT_WALKING_DISTANCE_M,
        "Distance_to_Next_Stop_m": dist_to_nearest_m,
        "Traffic_Level": nearest_stops["Traffic_Level"].mode()[0],
        "Bus_Frequency": int(nearest_stops["Bus_Frequency"].mean()),
        "Waiting_Time_min": int(nearest_stops["Waiting_Time_min"].mean()),
        "Occupancy_pct": round(float(nearest_stops["Occupancy_pct"].mean()), 1),
    }

    return derived
