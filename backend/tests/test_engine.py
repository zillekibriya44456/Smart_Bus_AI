"""
Unit tests for the deterministic scoring engine (engine.py).
"""
import pytest
from app.services.engine import (
    analyze_factors,
    calculate_improvement_priority,
    calculate_sub_scores,
    generate_recommendations,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def high_quality_data():
    return {
        "Passenger_Count": 90,
        "Boarding": 50,
        "Alighting": 40,
        "Road_Width": 14.0,
        "Walking_Distance_m": 80.0,
        "Distance_to_Next_Stop_m": 650.0,
        "Traffic_Level": "Low",
        "Bus_Frequency": 15,
        "Waiting_Time_min": 3,
        "Occupancy_pct": 75.0,
    }


@pytest.fixture
def low_quality_data():
    return {
        "Passenger_Count": 5,
        "Boarding": 3,
        "Alighting": 2,
        "Road_Width": 4.0,
        "Walking_Distance_m": 950.0,
        "Distance_to_Next_Stop_m": 1500.0,
        "Traffic_Level": "High",
        "Bus_Frequency": 1,
        "Waiting_Time_min": 30,
        "Occupancy_pct": 10.0,
    }


# ── calculate_sub_scores ──────────────────────────────────────────────────────

class TestCalculateSubScores:
    def test_returns_all_dimensions(self, high_quality_data):
        scores = calculate_sub_scores(high_quality_data)
        assert set(scores.keys()) == {"Demand", "Road", "Accessibility", "Safety", "Spacing"}

    def test_high_quality_scores_above_60(self, high_quality_data):
        scores = calculate_sub_scores(high_quality_data)
        for dim, score in scores.items():
            assert score >= 60, f"Expected {dim} >= 60, got {score}"

    def test_demand_capped_at_100(self):
        data = {"Passenger_Count": 999, "Road_Width": 10, "Walking_Distance_m": 200,
                "Distance_to_Next_Stop_m": 600, "Traffic_Level": "Low"}
        scores = calculate_sub_scores(data)
        assert scores["Demand"] == 100

    def test_road_capped_at_100(self):
        data = {"Passenger_Count": 50, "Road_Width": 50, "Walking_Distance_m": 200,
                "Distance_to_Next_Stop_m": 600, "Traffic_Level": "Moderate"}
        scores = calculate_sub_scores(data)
        assert scores["Road"] == 100

    def test_safety_low_traffic(self):
        data = {"Passenger_Count": 50, "Road_Width": 10, "Walking_Distance_m": 200,
                "Distance_to_Next_Stop_m": 600, "Traffic_Level": "Low"}
        scores = calculate_sub_scores(data)
        assert scores["Safety"] == 100

    def test_safety_high_traffic(self):
        data = {"Passenger_Count": 50, "Road_Width": 10, "Walking_Distance_m": 200,
                "Distance_to_Next_Stop_m": 600, "Traffic_Level": "High"}
        scores = calculate_sub_scores(data)
        assert scores["Safety"] == 20

    def test_safety_unknown_traffic_defaults_to_60(self):
        data = {"Passenger_Count": 50, "Road_Width": 10, "Walking_Distance_m": 200,
                "Distance_to_Next_Stop_m": 600, "Traffic_Level": "Unknown"}
        scores = calculate_sub_scores(data)
        assert scores["Safety"] == 60

    def test_spacing_below_300_gets_40(self):
        data = {"Passenger_Count": 50, "Road_Width": 10, "Walking_Distance_m": 200,
                "Distance_to_Next_Stop_m": 150, "Traffic_Level": "Low"}
        scores = calculate_sub_scores(data)
        assert scores["Spacing"] == 40

    def test_spacing_optimal_range_gets_100(self):
        data = {"Passenger_Count": 50, "Road_Width": 10, "Walking_Distance_m": 200,
                "Distance_to_Next_Stop_m": 600, "Traffic_Level": "Low"}
        scores = calculate_sub_scores(data)
        assert scores["Spacing"] == 100

    def test_missing_optional_keys_use_defaults(self):
        data = {"Passenger_Count": 50, "Road_Width": 10}
        scores = calculate_sub_scores(data)
        assert "Demand" in scores

    def test_all_scores_in_range_0_to_100(self, high_quality_data):
        scores = calculate_sub_scores(high_quality_data)
        for dim, score in scores.items():
            assert 0 <= score <= 100, f"{dim} score {score} out of range"

    def test_all_scores_in_range_low_quality(self, low_quality_data):
        scores = calculate_sub_scores(low_quality_data)
        for dim, score in scores.items():
            assert 0 <= score <= 100, f"{dim} score {score} out of range"


# ── calculate_improvement_priority ───────────────────────────────────────────

class TestCalculateImprovementPriority:
    def test_critical_priority(self):
        sub_scores = {"Demand": 90, "Road": 10, "Accessibility": 5, "Safety": 5, "Spacing": 80}
        score, category = calculate_improvement_priority(sub_scores)
        assert category == "Critical"
        assert score >= 75

    def test_low_priority_high_quality(self):
        sub_scores = {"Demand": 20, "Road": 100, "Accessibility": 100, "Safety": 100, "Spacing": 100}
        score, category = calculate_improvement_priority(sub_scores)
        assert category == "Low"

    def test_returns_tuple_of_int_and_str(self, high_quality_data):
        sub_scores = calculate_sub_scores(high_quality_data)
        score, category = calculate_improvement_priority(sub_scores)
        assert isinstance(score, int)
        assert isinstance(category, str)

    def test_priority_categories_exhaustive(self):
        """All thresholds map to a valid category string."""
        for demand in [10, 50, 90]:
            for worst in [0, 30, 60, 90]:
                sub_scores = {
                    "Demand": demand, "Road": worst, "Accessibility": worst + 5,
                    "Safety": worst + 10, "Spacing": 80,
                }
                _, cat = calculate_improvement_priority(sub_scores)
                assert cat in ("Critical", "High", "Medium", "Low")


# ── analyze_factors ───────────────────────────────────────────────────────────

class TestAnalyzeFactors:
    def test_high_demand_in_positive(self, high_quality_data):
        pos, neg = analyze_factors(high_quality_data)
        assert any("passenger" in f.lower() for f in pos)

    def test_low_demand_in_negative(self, low_quality_data):
        pos, neg = analyze_factors(low_quality_data)
        assert any("low" in f.lower() or "demand" in f.lower() for f in neg)

    def test_narrow_road_in_negative(self, low_quality_data):
        pos, neg = analyze_factors(low_quality_data)
        assert any("narrow" in f.lower() or "road" in f.lower() for f in neg)

    def test_wide_road_in_positive(self, high_quality_data):
        pos, neg = analyze_factors(high_quality_data)
        assert any("road" in f.lower() or "wide" in f.lower() for f in pos)

    def test_high_traffic_in_negative(self, low_quality_data):
        pos, neg = analyze_factors(low_quality_data)
        assert any("traffic" in f.lower() for f in neg)

    def test_returns_lists(self, high_quality_data):
        pos, neg = analyze_factors(high_quality_data)
        assert isinstance(pos, list)
        assert isinstance(neg, list)


# ── generate_recommendations ──────────────────────────────────────────────────

class TestGenerateRecommendations:
    def test_high_demand_gets_large_shelter(self, high_quality_data):
        recs = generate_recommendations(high_quality_data)
        assert any("large" in r.lower() or "smart" in r.lower() for r in recs)

    def test_low_demand_gets_small_shelter(self, low_quality_data):
        recs = generate_recommendations(low_quality_data)
        assert any("small" in r.lower() for r in recs)

    def test_wide_road_gets_pullout_bay(self, high_quality_data):
        recs = generate_recommendations(high_quality_data)
        assert any("pull-out" in r.lower() or "bus" in r.lower() for r in recs)

    def test_returns_list_of_strings(self, high_quality_data):
        recs = generate_recommendations(high_quality_data)
        assert isinstance(recs, list)
        assert all(isinstance(r, str) for r in recs)

    def test_medium_demand_gets_medium_shelter(self):
        data = {"Passenger_Count": 60, "Traffic_Level": "Moderate", "Road_Width": 8.0}
        recs = generate_recommendations(data)
        assert any("medium" in r.lower() or "25" in r for r in recs)
