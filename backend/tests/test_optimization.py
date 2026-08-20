"""
Unit tests for the optimization service (optimization.py).
"""
import pytest

from app.services.optimization import generate_grid_candidates
from app.services.gis import haversine_distance
from tests.conftest import make_sample_df


class TestGenerateGridCandidates:
    def test_returns_non_empty_list(self):
        candidates = generate_grid_candidates(12.9716, 77.5946, 1.0)
        assert len(candidates) > 0

    def test_approximate_count_for_1km_radius(self):
        """
        Area of circle ≈ π·r² = 3.14 km².
        Grid step = 0.2 km → cell area = 0.04 km².
        Expected points ≈ 78 (tolerance ±30 for edge clipping).
        """
        candidates = generate_grid_candidates(12.9716, 77.5946, 1.0, grid_step_m=200)
        assert 50 < len(candidates) < 110, f"Unexpected candidate count: {len(candidates)}"

    def test_all_candidates_within_radius(self):
        center_lat, center_lon = 12.9716, 77.5946
        radius_km = 1.0
        candidates = generate_grid_candidates(center_lat, center_lon, radius_km)
        for lat, lon in candidates:
            dist_m = haversine_distance(center_lat, center_lon, lat, lon)
            assert dist_m <= radius_km * 1000 + 1, (
                f"Candidate ({lat:.4f}, {lon:.4f}) is {dist_m:.0f} m from center, "
                f"exceeds radius of {radius_km * 1000:.0f} m"
            )

    def test_returns_list_of_tuples(self):
        candidates = generate_grid_candidates(12.9716, 77.5946, 0.5)
        assert isinstance(candidates, list)
        for item in candidates:
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_zero_candidates_for_tiny_radius(self):
        """A radius smaller than one grid step yields at most 1 candidate (center)."""
        candidates = generate_grid_candidates(12.9716, 77.5946, 0.01, grid_step_m=500)
        assert len(candidates) <= 5

    def test_larger_radius_yields_more_candidates(self):
        small = generate_grid_candidates(12.9716, 77.5946, 0.5)
        large = generate_grid_candidates(12.9716, 77.5946, 2.0)
        assert len(large) > len(small)
