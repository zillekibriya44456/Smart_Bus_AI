import unittest
from app.services.optimization import generate_grid_candidates

class TestOptimization(unittest.TestCase):
    def test_generate_grid_candidates(self):
        # 1km radius grid around Bangalore
        center_lat, center_lon = 12.9716, 77.5946
        radius_km = 1.0
        grid_step_m = 200
        
        candidates = generate_grid_candidates(center_lat, center_lon, radius_km, grid_step_m)
        
        # Area of circle = pi * r^2 ~ 3.14 sq km
        # Grid step = 0.2 km, area per point ~ 0.04 sq km
        # Expected points ~ 3.14 / 0.04 ~ 78 points
        
        self.assertTrue(len(candidates) > 50)
        self.assertTrue(len(candidates) < 100)
        
        # Check that all points are within the radius (approx using bounding box)
        for cand_lat, cand_lon in candidates:
            self.assertTrue(abs(cand_lat - center_lat) < 0.02)
            self.assertTrue(abs(cand_lon - center_lon) < 0.02)

if __name__ == '__main__':
    unittest.main()
