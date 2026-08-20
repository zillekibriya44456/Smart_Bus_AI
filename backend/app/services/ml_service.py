"""
ML inference service.

Loads scikit-learn regression model from disk on first use and provides
the suitability prediction function used by all API endpoints.

The classifier model (.pkl) was previously loaded but never called;
it has been removed to eliminate dead code.
"""
import logging
import os
from typing import Tuple

import joblib
import pandas as pd

from app.core.config import settings

logger = logging.getLogger(__name__)

# Module-level model cache (lazy-loaded on first request, persisted in memory)
_reg_model = None

# Hard-constraint thresholds (keep in sync with engine.py)
_MIN_ROAD_WIDTH_M: float = 6.0
_MIN_STOP_SPACING_M: float = 200.0


def _model_path() -> str:
    return os.path.join(settings.MODEL_DIR, "best_reg_model.pkl")


def validate_models() -> None:
    """
    Verify that the required model file exists and can be loaded.
    Raises FileNotFoundError or RuntimeError on failure.
    Called at application startup so misconfiguration fails fast.
    """
    path = _model_path()
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Regression model not found at '{path}'. "
            "Ensure the ML training pipeline has been run and the model file is present."
        )
    # Trigger actual load to catch corrupted pkl files early
    _load_model()
    logger.info("ML model validation passed: %s", path)


def _load_model() -> None:
    """Load the regression model into the module cache if not already loaded."""
    global _reg_model
    if _reg_model is None:
        path = _model_path()
        logger.info("Loading regression model from %s", path)
        _reg_model = joblib.load(path)
        logger.info("Regression model loaded successfully.")


def predict_suitability(data: dict) -> Tuple[float, str]:
    """
    Predict the suitability score (0–100) and category for a bus stop location.

    Hard constraints override the model score when physical minimums are not met:
      - Road width < 6 m  → score forced to 0
      - Distance to next stop < 200 m  → score forced to 0

    Args:
        data: Dictionary of feature values matching the model's training features.

    Returns:
        Tuple of (rounded_score: float, category: str).
    """
    _load_model()

    df = pd.DataFrame([data])
    score: float = float(_reg_model.predict(df)[0])

    # Apply hard constraints
    road_width = float(data.get("Road_Width", 0))
    stop_spacing = float(data.get("Distance_to_Next_Stop_m", 0))
    if road_width < _MIN_ROAD_WIDTH_M or stop_spacing < _MIN_STOP_SPACING_M:
        logger.debug(
            "Hard constraint triggered: road_width=%.1f, stop_spacing=%.1f — score set to 0.",
            road_width,
            stop_spacing,
        )
        score = 0.0

    # Derive category from score thresholds (consistent with engine.py)
    if score >= 80:
        category = "Highly Suitable"
    elif score >= 65:
        category = "Suitable"
    elif score >= 50:
        category = "Moderately Suitable"
    elif score >= 35:
        category = "Needs Improvement"
    else:
        category = "Not Suitable"

    return round(score, 2), category
