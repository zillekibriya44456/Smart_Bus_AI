"""
Corridor Analysis and Optimization service.
"""
import logging
import math
from typing import Any, Dict, List, Tuple

import pandas as pd

from .engine import analyze_factors
from .gis import derive_features_from_coordinates, haversine_distance
from .ml_service import predict_suitability
from .optimization import generate_grid_candidates
from ..models.schemas import CorridorDecision, RelocationCandidate

logger = logging.getLogger(__name__)


def point_to_line_distance(
    lat: float, lon: float,
    start_lat: float, start_lon: float,
    end_lat: float, end_lon: float
) -> float:
    """
    Approximate the shortest distance in metres from a point to a line segment.
    Uses flat-earth projection for local city-scale accuracy.
    """
    # Convert everything to metres relative to start point
    lat_degree_m = 111_320.0
    lon_degree_m = 40_075_000.0 * math.cos(math.radians(start_lat)) / 360.0

    x = (lon - start_lon) * lon_degree_m
    y = (lat - start_lat) * lat_degree_m
    x2 = (end_lon - start_lon) * lon_degree_m
    y2 = (end_lat - start_lat) * lat_degree_m

    L2 = x2**2 + y2**2
    if L2 == 0:
        return math.sqrt(x**2 + y**2)

    # Calculate projection parameter t, clamped to [0, 1] for segment
    t = max(0.0, min(1.0, (x * x2 + y * y2) / L2))

    # Projection coordinates
    proj_x = t * x2
    proj_y = t * y2

    # Distance to projection
    return math.sqrt((x - proj_x)**2 + (y - proj_y)**2)


def get_stops_in_corridor(
    df: pd.DataFrame,
    start_lat: float, start_lon: float,
    end_lat: float, end_lon: float,
    buffer_m: float
) -> pd.DataFrame:
    """Find all stops in the dataset within the corridor buffer."""
    distances = df.apply(
        lambda row: point_to_line_distance(
            row["Latitude"], row["Longitude"],
            start_lat, start_lon, end_lat, end_lon
        ),
        axis=1
    )
    return df[distances <= buffer_m]


def make_decision(score: float, data: dict) -> Tuple[str, str]:
    """
    Decide whether to RETAIN, IMPROVE, RELOCATE, or REMOVE based on score and demand.
    Returns (Decision, Explanation).
    """
    demand = float(data.get("Passenger_Count", 0))

    if score >= 75:
        return "RETAIN", "Excellent suitability score and good conditions. No action required."
    elif score >= 50:
        return "IMPROVE", "Location is generally acceptable but requires infrastructure improvements."
    elif score < 50 and demand >= 30:
        return "RELOCATE", "Poor location suitability but passenger demand justifies retaining a stop nearby. Recommend relocating."
    else:
        return "REMOVE", "Very poor suitability score and low passenger demand. Stop is redundant and should be removed."


def optimize_relocation_in_corridor(
    stop_lat: float, stop_lon: float,
    start_lat: float, start_lon: float,
    end_lat: float, end_lon: float,
    buffer_m: float,
    df: pd.DataFrame,
    retained_stops_df: pd.DataFrame
) -> List[RelocationCandidate]:
    """
    Find better candidate locations near a stop that must be relocated.
    Candidates must be inside the corridor and away from retained stops.
    """
    # Search around the current stop (up to 1km radius)
    candidates_raw = generate_grid_candidates(stop_lat, stop_lon, radius_km=1.0, grid_step_m=100)

    valid_candidates = []
    for cand_lat, cand_lon in candidates_raw:
        # 1. Must be inside corridor
        dist_to_line = point_to_line_distance(cand_lat, cand_lon, start_lat, start_lon, end_lat, end_lon)
        if dist_to_line > buffer_m:
            continue

        # 2. Must not be too close to existing RETAIN/IMPROVE stops
        if not retained_stops_df.empty:
            dists = retained_stops_df.apply(
                lambda row: haversine_distance(cand_lat, cand_lon, row["Latitude"], row["Longitude"]),
                axis=1
            )
            if dists.min() < 300: # 300m minimum spacing
                continue

        valid_candidates.append((cand_lat, cand_lon))

    results = []
    current_derived = derive_features_from_coordinates(stop_lat, stop_lon, df)
    current_score, _ = predict_suitability(current_derived)

    for cand_lat, cand_lon in valid_candidates:
        derived_data = derive_features_from_coordinates(cand_lat, cand_lon, df)
        score, _ = predict_suitability(derived_data)
        
        # Only keep if it's an improvement of at least +10 points
        if score >= current_score + 10:
            pos, neg = analyze_factors(derived_data)
            reason = pos[0] if pos else "Improved overall conditions."
            dist_moved = haversine_distance(stop_lat, stop_lon, cand_lat, cand_lon)

            results.append(RelocationCandidate(
                Latitude=cand_lat,
                Longitude=cand_lon,
                New_Score=score,
                Improvement=score - current_score,
                Distance_Moved_m=dist_moved,
                Reason=reason
            ))

    # Rank by highest score first
    results.sort(key=lambda x: x.New_Score, reverse=True)
    return results[:4] # Return best + 3 alternatives
