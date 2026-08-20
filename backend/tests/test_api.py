"""
Integration tests for all API endpoints.

These tests use the FastAPI TestClient with the ML model mocked so they
run fast without requiring the 50 MB pkl files.
"""
import pytest


# ── /health ───────────────────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_returns_200_or_503(self, client):
        """Health endpoint always responds (may be degraded without DB)."""
        resp = client.get("/health")
        assert resp.status_code in (200, 503)

    def test_health_response_has_status_field(self, client):
        resp = client.get("/health")
        data = resp.json()
        assert "status" in data

    def test_health_response_has_version(self, client):
        resp = client.get("/health")
        data = resp.json()
        assert "version" in data


# ── /analyze-location ─────────────────────────────────────────────────────────

class TestAnalyzeLocation:
    def test_valid_request_returns_200(self, client, good_payload):
        resp = client.post("/analyze-location", json=good_payload)
        assert resp.status_code == 200

    def test_response_has_required_fields(self, client, good_payload):
        resp = client.post("/analyze-location", json=good_payload)
        data = resp.json()
        for field in ("Suitability_Score", "Suitability_Category", "SubScores",
                      "Positive_Factors", "Negative_Factors", "Recommendations"):
            assert field in data, f"Missing field: {field}"

    def test_suitability_score_in_range(self, client, good_payload):
        resp = client.post("/analyze-location", json=good_payload)
        score = resp.json()["Suitability_Score"]
        assert 0 <= score <= 100

    def test_analysis_type_is_explicit(self, client, good_payload):
        resp = client.post("/analyze-location", json=good_payload)
        assert resp.json()["Analysis_Type"] == "Explicit"

    def test_missing_required_field_returns_422(self, client, good_payload):
        incomplete = {k: v for k, v in good_payload.items() if k != "Passenger_Count"}
        resp = client.post("/analyze-location", json=incomplete)
        assert resp.status_code == 422

    def test_negative_passenger_count_returns_422(self, client, good_payload):
        good_payload["Passenger_Count"] = -10
        resp = client.post("/analyze-location", json=good_payload)
        assert resp.status_code == 422

    def test_invalid_traffic_level_returns_422(self, client, good_payload):
        good_payload["Traffic_Level"] = "Very High"
        resp = client.post("/analyze-location", json=good_payload)
        assert resp.status_code == 422

    def test_zero_road_width_returns_422(self, client, good_payload):
        good_payload["Road_Width"] = 0
        resp = client.post("/analyze-location", json=good_payload)
        assert resp.status_code == 422

    def test_occupancy_above_100_returns_422(self, client, good_payload):
        good_payload["Occupancy_pct"] = 150.0
        resp = client.post("/analyze-location", json=good_payload)
        assert resp.status_code == 422

    def test_low_quality_stop_returns_low_score(self, client, bad_payload):
        resp = client.post("/analyze-location", json=bad_payload)
        # Hard constraints (road < 6m AND spacing < 200m) should drive score to 0
        assert resp.status_code == 200
        assert resp.json()["Suitability_Score"] == 0.0


# ── /analyze-coordinates ──────────────────────────────────────────────────────

class TestAnalyzeCoordinates:
    def test_valid_coordinates_return_200(self, client):
        resp = client.post("/analyze-coordinates", json={"Latitude": 12.97, "Longitude": 77.59})
        assert resp.status_code == 200

    def test_analysis_type_is_derived(self, client):
        resp = client.post("/analyze-coordinates", json={"Latitude": 12.97, "Longitude": 77.59})
        assert resp.json()["Analysis_Type"] == "Derived"

    def test_invalid_latitude_returns_422(self, client):
        resp = client.post("/analyze-coordinates", json={"Latitude": 200.0, "Longitude": 77.59})
        assert resp.status_code == 422

    def test_invalid_longitude_returns_422(self, client):
        resp = client.post("/analyze-coordinates", json={"Latitude": 12.97, "Longitude": 999.0})
        assert resp.status_code == 422


# ── /optimize-location ────────────────────────────────────────────────────────

class TestOptimizeLocation:
    def test_valid_request_returns_200(self, client):
        resp = client.post("/optimize-location", json={
            "Latitude": 12.97, "Longitude": 77.59, "Radius_km": 1.0
        })
        assert resp.status_code == 200

    def test_response_has_candidates_field(self, client):
        resp = client.post("/optimize-location", json={
            "Latitude": 12.97, "Longitude": 77.59, "Radius_km": 1.0
        })
        assert "Candidates" in resp.json()

    def test_radius_above_10_returns_422(self, client):
        resp = client.post("/optimize-location", json={
            "Latitude": 12.97, "Longitude": 77.59, "Radius_km": 15.0
        })
        assert resp.status_code == 422


# ── /compare-locations ────────────────────────────────────────────────────────

class TestCompareLocations:
    def test_valid_comparison_returns_200(self, client, good_payload, bad_payload):
        resp = client.post("/compare-locations", json={
            "Location_A": good_payload,
            "Location_B": bad_payload,
        })
        assert resp.status_code == 200

    def test_response_has_recommendation(self, client, good_payload, bad_payload):
        resp = client.post("/compare-locations", json={
            "Location_A": good_payload,
            "Location_B": bad_payload,
        })
        data = resp.json()
        assert "Recommended_Location" in data
        assert "Recommendation_Reason" in data

    def test_good_location_wins(self, client, good_payload, bad_payload):
        resp = client.post("/compare-locations", json={
            "Location_A": good_payload,
            "Location_B": bad_payload,
        })
        data = resp.json()
        assert data["Recommended_Location"] == "Location A"

    def test_invalid_traffic_level_in_location_returns_422(self, client, good_payload):
        bad = good_payload.copy()
        bad["Traffic_Level"] = "Extreme"
        resp = client.post("/compare-locations", json={
            "Location_A": good_payload,
            "Location_B": bad,
        })
        assert resp.status_code == 422


# ── /bus-stops ────────────────────────────────────────────────────────────────

class TestBusStops:
    def test_get_bus_stops_returns_200(self, client):
        resp = client.get("/bus-stops")
        assert resp.status_code == 200

    def test_returns_list(self, client):
        resp = client.get("/bus-stops")
        assert isinstance(resp.json(), list)

    def test_stops_have_suitability_score(self, client):
        stops = client.get("/bus-stops").json()
        if stops:
            assert "Suitability_Score" in stops[0]

    def test_unknown_stop_id_returns_404(self, client):
        resp = client.get("/bus-stops/NONEXISTENT_STOP_XYZ")
        assert resp.status_code == 404


# ── /recommend-infrastructure ─────────────────────────────────────────────────

class TestRecommendInfrastructure:
    def test_valid_request_returns_200(self, client):
        resp = client.post("/recommend-infrastructure", json={
            "Passenger_Count": 80, "Traffic_Level": "High", "Road_Width": 12.0
        })
        assert resp.status_code == 200

    def test_response_has_recommendations(self, client):
        resp = client.post("/recommend-infrastructure", json={
            "Passenger_Count": 80, "Traffic_Level": "High", "Road_Width": 12.0
        })
        data = resp.json()
        assert "Recommendations" in data
        assert isinstance(data["Recommendations"], list)

    def test_invalid_traffic_returns_422(self, client):
        resp = client.post("/recommend-infrastructure", json={
            "Passenger_Count": 50, "Traffic_Level": "Crazy", "Road_Width": 10.0
        })
        assert resp.status_code == 422
