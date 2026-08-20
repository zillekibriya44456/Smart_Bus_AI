"""
Pytest fixtures shared across all test modules.
"""
import os
from unittest.mock import MagicMock, patch, PropertyMock

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

# Mock psycopg2 / database before any app module is imported
import sys
sys.modules.setdefault("psycopg2", MagicMock())

# ── Paths ──────────────────────────────────────────────────────────────────────
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML_MODELS_DIR = os.path.abspath(os.path.join(BACKEND_DIR, "../../ml/models"))


# ── Sample data ───────────────────────────────────────────────────────────────
SAMPLE_LOCATION_PAYLOAD = {
    "Passenger_Count": 75,
    "Boarding": 40,
    "Alighting": 35,
    "Road_Width": 12.0,
    "Walking_Distance_m": 150.0,
    "Distance_to_Next_Stop_m": 600.0,
    "Traffic_Level": "Moderate",
    "Bus_Frequency": 10,
    "Waiting_Time_min": 5,
    "Occupancy_pct": 70.0,
}

SAMPLE_LOW_QUALITY_PAYLOAD = {
    "Passenger_Count": 5,
    "Boarding": 3,
    "Alighting": 2,
    "Road_Width": 4.0,   # Below hard constraint
    "Walking_Distance_m": 900.0,
    "Distance_to_Next_Stop_m": 100.0,  # Below hard constraint
    "Traffic_Level": "High",
    "Bus_Frequency": 2,
    "Waiting_Time_min": 25,
    "Occupancy_pct": 20.0,
}


def make_sample_df(n: int = 10) -> pd.DataFrame:
    """Create a small synthetic bus stop DataFrame for testing."""
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "Stop_ID": [f"STOP_{i:03d}" for i in range(n)],
        "Latitude": 12.97 + rng.uniform(-0.05, 0.05, n),
        "Longitude": 77.59 + rng.uniform(-0.05, 0.05, n),
        "Passenger_Count": rng.integers(10, 100, n),
        "Boarding": rng.integers(5, 50, n),
        "Alighting": rng.integers(5, 50, n),
        "Road_Width": rng.uniform(6, 15, n),
        "Walking_Distance_m": rng.uniform(50, 800, n),
        "Distance_to_Next_Stop_m": rng.uniform(200, 1500, n),
        "Traffic_Level": rng.choice(["Low", "Moderate", "High"], n),
        "Bus_Frequency": rng.integers(2, 20, n),
        "Waiting_Time_min": rng.integers(2, 30, n),
        "Occupancy_pct": rng.uniform(20, 95, n),
        "Population_Density": rng.uniform(1000, 50000, n),
    })


# ── FastAPI TestClient (with mocked ML model) ─────────────────────────────────
@pytest.fixture(scope="session")
def client():
    """
    Return a FastAPI TestClient with the ML model mocked so tests don't
    require the actual 50 MB pkl file.
    """
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([72.5])

    with patch("app.services.ml_service._reg_model", mock_model), \
         patch("app.services.ml_service.validate_models", return_value=None), \
         patch("app.api.endpoints._get_dataframe", return_value=make_sample_df(200)):

        from app.main import app
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c


@pytest.fixture
def sample_df():
    return make_sample_df()


@pytest.fixture
def good_payload():
    return SAMPLE_LOCATION_PAYLOAD.copy()


@pytest.fixture
def bad_payload():
    return SAMPLE_LOW_QUALITY_PAYLOAD.copy()
