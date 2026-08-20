import unittest
from app.services.gis import haversine_distance

class TestGIS(unittest.TestCase):
    def test_haversine_distance(self):
        # Coordinates for Bangalore and Mysore (~128km apart)
        lat1, lon1 = 12.9716, 77.5946
        lat2, lon2 = 12.2958, 76.6394
        
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        
        # Approximate distance should be ~128,000 meters (+/- 5km)
        self.assertTrue(123000 < distance < 133000, f"Distance {distance} out of bounds")
        
    def test_zero_distance(self):
        distance = haversine_distance(12.0, 77.0, 12.0, 77.0)
        self.assertEqual(distance, 0.0)

if __name__ == '__main__':
    unittest.main()
