"""
Bus stop location optimizer.

Generates a grid of candidate coordinates within a search radius,
filters out positions too close to existing stops, scores remaining
candidates with the ML model, and returns the top results.
"""
import logging
import math
from typing import Any, Dict, List, Tuple

import pandas as pd

from .engine import analyze_factors
from .gis import haversine_distance, derive_features_from_coordinates
from .ml_service import predict_suitability

logger = logging.getLogger(__name__)

# Number of top candidates to return
_TOP_N: int = 5

# Grid step size in metres (controls resolution vs. performance)
_DEFAULT_GRID_STEP_M: int = 200


def generate_grid_candidates(
    center_lat: float,
    center_lon: float,
    radius_km: float,
    grid_step_m: int = _DEFAULT_GRID_STEP_M,
) -> List[Tuple[float, float]]:
    """
    Generate a uniform grid of (lat, lon) candidates within a circular radius.

    Args:
        center_lat:  Centre latitude in decimal degrees.
        center_lon:  Centre longitude in decimal degrees.
        radius_km:   Search radius in kilometres.
        grid_step_m: Distance between grid points in metres.

    Returns:
        List of (latitude, longitude) tuples inside the radius.
    """
    candidates: List[Tuple[float, float]] = []
    lat_degree_m = 111_320.0
    lon_degree_m = 40_075_000.0 * math.cos(math.radians(center_lat)) / 360.0

    radius_m = radius_km * 1_000
    lat_step = grid_step_m / lat_degree_m
    lon_step = grid_step_m / lon_degree_m
    steps = int(radius_m / grid_step_m)

    for i in range(-steps, steps + 1):
        for j in range(-steps, steps + 1):
            cand_lat = center_lat + (i * lat_step)
            cand_lon = center_lon + (j * lon_step)
            dist = haversine_distance(center_lat, center_lon, cand_lat, cand_lon)
            if dist <= radius_m:
                candidates.append((cand_lat, cand_lon))

    logger.debug(
        "Generated %d grid candidates for (%.4f, %.4f) r=%.1f km",
        len(candidates), center_lat, center_lon, radius_km,
    )
    return candidates


def optimize_bus_stops(
    center_lat: float,
    center_lon: float,
    radius_km: float,
    df: pd.DataFrame,
    min_distance_existing_m: int = 200,
) -> List[Dict[str, Any]]:
    """
    Find the top candidate locations for a new bus stop within a given radius.

    Steps:
      1. Generate a grid of candidate coordinates.
      2. Filter out candidates too close to existing stops.
      3. Derive features and score each valid candidate.
      4. Return the top _TOP_N results ranked by suitability score.

    Args:
        center_lat:             Search area centre latitude.
        center_lon:             Search area centre longitude.
        radius_km:              Search radius in kilometres.
        df:                     DataFrame of existing bus stops.
        min_distance_existing_m: Minimum distance from any existing stop (metres).

    Returns:
        List of result dicts, each containing Latitude, Longitude,
        Suitability_Score, Suitability_Category, Positive_Factors,
        Negative_Factors, and Derived_Features.
    """
    candidates = generate_grid_candidates(center_lat, center_lon, radius_km)
    logger.info(
        "Optimizing %d candidates around (%.4f, %.4f) r=%.1f km",
        len(candidates), center_lat, center_lon, radius_km,
    )

    valid_candidates: List[Tuple[float, float]] = []
    for cand_lat, cand_lon in candidates:
        distances = df.apply(
            lambda row: haversine_distance(cand_lat, cand_lon, row["Latitude"], row["Longitude"]),
            axis=1,
        )
        if distances.min() >= min_distance_existing_m:
            valid_candidates.append((cand_lat, cand_lon))

    logger.info(
        "%d valid candidates after proximity filter (min_dist=%d m)",
        len(valid_candidates), min_distance_existing_m,
    )

    results: List[Dict[str, Any]] = []
    for cand_lat, cand_lon in valid_candidates:
        derived_data = derive_features_from_coordinates(cand_lat, cand_lon, df)
        score, category = predict_suitability(derived_data)
        pos, neg = analyze_factors(derived_data)

        results.append({
            "Latitude": cand_lat,
            "Longitude": cand_lon,
            "Suitability_Score": score,
            "Suitability_Category": category,
            "Positive_Factors": pos,
            "Negative_Factors": neg,
            "Derived_Features": derived_data,
        })

    results.sort(key=lambda x: x["Suitability_Score"], reverse=True)
    return results[:_TOP_N]
