"""
Unit tests for the GIS service (gis.py).
"""
import math

import pandas as pd
import pytest

from app.services.gis import derive_features_from_coordinates, haversine_distance
from tests.conftest import make_sample_df


# ── haversine_distance ────────────────────────────────────────────────────────

class TestHaversineDistance:
    def test_bangalore_to_mysore_approx_128km(self):
        """Known real-world distance between Bangalore and Mysore is ~128 km."""
        dist = haversine_distance(12.9716, 77.5946, 12.2958, 76.6394)
        assert 123_000 < dist < 133_000, f"Expected ~128 km, got {dist:.0f} m"

    def test_same_point_returns_zero(self):
        assert haversine_distance(12.0, 77.0, 12.0, 77.0) == 0.0

    def test_symmetry(self):
        d1 = haversine_distance(12.9, 77.5, 13.0, 77.6)
        d2 = haversine_distance(13.0, 77.6, 12.9, 77.5)
        assert math.isclose(d1, d2, rel_tol=1e-9)

    def test_returns_float(self):
        result = haversine_distance(0.0, 0.0, 1.0, 1.0)
        assert isinstance(result, float)

    def test_positive_distance(self):
        dist = haversine_distance(10.0, 75.0, 11.0, 76.0)
        assert dist > 0

    def test_equatorial_distance_approx(self):
        """1 degree of longitude at equator ≈ 111,320 m."""
        dist = haversine_distance(0.0, 0.0, 0.0, 1.0)
        assert 110_000 < dist < 112_000, f"Unexpected equatorial distance: {dist:.0f} m"


# ── derive_features_from_coordinates ─────────────────────────────────────────

class TestDeriveFeatures:
    def test_returns_all_required_keys(self, sample_df):
        result = derive_features_from_coordinates(12.97, 77.59, sample_df)
        required_keys = {
            "Passenger_Count", "Boarding", "Alighting", "Road_Width",
            "Walking_Distance_m", "Distance_to_Next_Stop_m", "Traffic_Level",
            "Bus_Frequency", "Waiting_Time_min", "Occupancy_pct",
        }
        assert required_keys.issubset(result.keys())

    def test_traffic_level_is_valid(self, sample_df):
        result = derive_features_from_coordinates(12.97, 77.59, sample_df)
        assert result["Traffic_Level"] in ("Low", "Moderate", "High")

    def test_passenger_count_is_positive(self, sample_df):
        result = derive_features_from_coordinates(12.97, 77.59, sample_df)
        assert result["Passenger_Count"] >= 0

    def test_road_width_is_positive(self, sample_df):
        result = derive_features_from_coordinates(12.97, 77.59, sample_df)
        assert result["Road_Width"] > 0

    def test_distance_to_nearest_is_finite(self, sample_df):
        result = derive_features_from_coordinates(12.97, 77.59, sample_df)
        assert math.isfinite(result["Distance_to_Next_Stop_m"])

    def test_walking_distance_default(self, sample_df):
        """Walking distance defaults to 200 m when not otherwise derivable."""
        result = derive_features_from_coordinates(12.97, 77.59, sample_df)
        assert result["Walking_Distance_m"] == 200.0

    def test_raises_on_empty_dataframe(self):
        empty_df = pd.DataFrame()
        with pytest.raises(ValueError, match="empty"):
            derive_features_from_coordinates(12.97, 77.59, empty_df)
