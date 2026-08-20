"""
API endpoints for the Smart Bus Stop AI system.

All endpoints validate inputs via Pydantic schemas before reaching service
logic. CSV reading is performed once at module load (cached) to avoid
repeated disk I/O on every request.
"""
import json
import logging
import os
from functools import lru_cache
from typing import Any, Dict, List

import pandas as pd
from fastapi import APIRouter, HTTPException

from ..core.config import settings
from ..models.schemas import (
    CoordinateRequest,
    CompareLocationsRequest,
    CompareLocationsResponse,
    InfrastructureRequest,
    LocationRequest,
    LocationResponse,
    OptimizationCandidate,
    OptimizationRequest,
    OptimizationResponse,
)
from ..services.engine import (
    analyze_factors,
    calculate_improvement_priority,
    calculate_sub_scores,
    generate_recommendations,
)
from ..services.gis import derive_features_from_coordinates
from ..services.ml_service import predict_suitability
from ..services.optimization import optimize_bus_stops

logger = logging.getLogger(__name__)
router = APIRouter()

# ── CSV data loader (cached) ──────────────────────────────────────────────────
_CLEAN_CSV = os.path.join(settings.DATA_DIR, "bus_stop_optimization_dataset_15000_cleaned.csv")


@lru_cache(maxsize=1)
def _get_dataframe() -> pd.DataFrame:
    """
    Load the cleaned bus stop dataset from disk, cached for the process lifetime.

    Raises:
        HTTPException 503 if the CSV file is not found.
    """
    if not os.path.exists(_CLEAN_CSV):
        logger.error("CSV dataset not found at '%s'.", _CLEAN_CSV)
        raise HTTPException(
            status_code=503,
            detail=f"Bus stop dataset unavailable. Expected at: {_CLEAN_CSV}",
        )
    logger.info("Loading bus stop dataset from %s", _CLEAN_CSV)
    return pd.read_csv(_CLEAN_CSV)


# ── Shared helper ─────────────────────────────────────────────────────────────

def _build_location_response(data: dict, analysis_type: str = "Explicit", derived_from: dict = None) -> LocationResponse:
    """
    Run the full analysis pipeline on a feature dict and return a LocationResponse.

    Args:
        data:          Feature dictionary.
        analysis_type: "Explicit" or "Derived".
        derived_from:  Optional raw coordinate dict to embed in the response.
    """
    score, category = predict_suitability(data)
    pos, neg = analyze_factors(data)
    recs = generate_recommendations(data)
    sub_scores = calculate_sub_scores(data)
    priority_score, priority_category = calculate_improvement_priority(sub_scores)

    return LocationResponse(
        Suitability_Score=score,
        Suitability_Category=category,
        SubScores=sub_scores,
        Priority_Score=priority_score,
        Priority_Category=priority_category,
        Positive_Factors=pos,
        Negative_Factors=neg,
        Recommendations=recs,
        Analysis_Type=analysis_type,
        Derived_From_Coordinates=derived_from,
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/analyze-location", response_model=LocationResponse, tags=["Analysis"])
def analyze_location(req: LocationRequest) -> LocationResponse:
    """
    Analyse a bus stop location using explicitly provided feature values.

    All feature values are supplied by the user and treated as ground truth.
    """
    logger.info("POST /analyze-location — Passenger_Count=%d", req.Passenger_Count)
    try:
        return _build_location_response(req.model_dump())
    except Exception as exc:
        logger.exception("Error in analyze_location: %s", exc)
        raise HTTPException(status_code=500, detail="Internal analysis error.")


@router.post("/analyze-coordinates", response_model=LocationResponse, tags=["Analysis"])
def analyze_coordinates(req: CoordinateRequest) -> LocationResponse:
    """
    Derive bus stop features from a geographic coordinate and analyse suitability.

    Feature values are *estimated* from the K nearest existing stops in the
    dataset. Results are marked ``Analysis_Type="Derived"`` to indicate this.
    """
    logger.info("POST /analyze-coordinates — lat=%.4f, lon=%.4f", req.Latitude, req.Longitude)
    try:
        df = _get_dataframe()
        derived_data = derive_features_from_coordinates(req.Latitude, req.Longitude, df)
        return _build_location_response(derived_data, analysis_type="Derived", derived_from=derived_data)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error in analyze_coordinates: %s", exc)
        raise HTTPException(status_code=500, detail="Internal coordinate analysis error.")


@router.post("/optimize-location", response_model=OptimizationResponse, tags=["Optimization"])
def optimize_location(req: OptimizationRequest) -> OptimizationResponse:
    """
    Find the top candidate locations for a new bus stop within a search radius.

    Returns up to 5 ranked candidates based on AI-predicted suitability scores.
    """
    logger.info(
        "POST /optimize-location — center=(%.4f, %.4f), radius=%.1f km",
        req.Latitude, req.Longitude, req.Radius_km,
    )
    try:
        df = _get_dataframe()
        candidates = optimize_bus_stops(req.Latitude, req.Longitude, req.Radius_km, df)

        candidate_responses = [
            OptimizationCandidate(
                Rank=i + 1,
                Latitude=c["Latitude"],
                Longitude=c["Longitude"],
                Suitability_Score=c["Suitability_Score"],
                Suitability_Category=c["Suitability_Category"],
                Positive_Factors=c["Positive_Factors"],
                Negative_Factors=c["Negative_Factors"],
                Derived_Features=c["Derived_Features"],
            )
            for i, c in enumerate(candidates)
        ]

        return OptimizationResponse(
            Center_Latitude=req.Latitude,
            Center_Longitude=req.Longitude,
            Radius_km=req.Radius_km,
            Candidates=candidate_responses,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error in optimize_location: %s", exc)
        raise HTTPException(status_code=500, detail="Internal optimization error.")


@router.post("/compare-locations", response_model=CompareLocationsResponse, tags=["Analysis"])
def compare_locations(req: CompareLocationsRequest) -> CompareLocationsResponse:
    """
    Compare two bus stop locations and recommend the better one.

    Both locations are analysed using identical logic; the higher suitability
    score wins the recommendation.
    """
    logger.info("POST /compare-locations")
    try:
        res_a = _build_location_response(req.Location_A.model_dump())
        res_b = _build_location_response(req.Location_B.model_dump())

        if res_a.Suitability_Score > res_b.Suitability_Score:
            recommended = "Location A"
            diff = res_a.Suitability_Score - res_b.Suitability_Score
            best_factor = res_a.Positive_Factors[0] if res_a.Positive_Factors else "Good general conditions"
            reason = (
                f"Location A is recommended because its overall suitability score is "
                f"{diff:.1f} points higher. It features better core metrics: {best_factor}."
            )
        elif res_b.Suitability_Score > res_a.Suitability_Score:
            recommended = "Location B"
            diff = res_b.Suitability_Score - res_a.Suitability_Score
            best_factor = res_b.Positive_Factors[0] if res_b.Positive_Factors else "Good general conditions"
            reason = (
                f"Location B is recommended because its overall suitability score is "
                f"{diff:.1f} points higher. It features better core metrics: {best_factor}."
            )
        else:
            recommended = "Tie"
            reason = (
                "Both locations have the exact same overall suitability score. "
                "Choose based on secondary considerations like land cost or network connectivity."
            )

        return CompareLocationsResponse(
            Location_A_Response=res_a,
            Location_B_Response=res_b,
            Recommended_Location=recommended,
            Recommendation_Reason=reason,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error in compare_locations: %s", exc)
        raise HTTPException(status_code=500, detail="Internal comparison error.")


@router.post("/recommend-infrastructure", tags=["Analysis"])
def recommend_infrastructure(req: InfrastructureRequest) -> Dict[str, List[str]]:
    """Generate infrastructure recommendations from a minimal feature set."""
    logger.info(
        "POST /recommend-infrastructure — Passenger_Count=%d", req.Passenger_Count
    )
    recs = generate_recommendations(req.model_dump())
    return {"Recommendations": recs}


@router.get("/bus-stops", tags=["Data"])
def get_bus_stops() -> List[Dict[str, Any]]:
    """
    Return a sample of 200 bus stops from the dataset, each enriched with
    AI suitability scores and sorted by improvement priority (highest first).
    """
    logger.info("GET /bus-stops")
    try:
        df = _get_dataframe()
        df_sample = df.sample(n=min(200, len(df)), random_state=42)
        stops = []

        for _, row in df_sample.iterrows():
            data = row.to_dict()
            score, category = predict_suitability(data)
            pos, neg = analyze_factors(data)
            recs = generate_recommendations(data)
            sub_scores = calculate_sub_scores(data)
            priority_score, priority_category = calculate_improvement_priority(sub_scores)

            stops.append({
                "Stop_ID": row.get("Stop_ID", "Unknown"),
                "Passenger_Count": row["Passenger_Count"],
                "Road_Width": row["Road_Width"],
                "Traffic_Level": row["Traffic_Level"],
                "Latitude": row.get("Latitude"),
                "Longitude": row.get("Longitude"),
                "Suitability_Score": score,
                "Suitability_Category": category,
                "Priority_Score": priority_score,
                "Priority_Category": priority_category,
                "Positive_Factors": pos,
                "Negative_Factors": neg,
                "Recommendations": recs,
            })

        stops.sort(key=lambda x: x["Priority_Score"], reverse=True)
        return stops
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error in get_bus_stops: %s", exc)
        raise HTTPException(status_code=500, detail="Internal error fetching bus stops.")


@router.get("/bus-stops/{stop_id}", tags=["Data"])
def get_bus_stop(stop_id: str) -> Dict[str, Any]:
    """Return the full data and analysis for a single bus stop by ID."""
    logger.info("GET /bus-stops/%s", stop_id)
    try:
        df = _get_dataframe()
        stop = df[df["Stop_ID"] == stop_id]

        if stop.empty:
            raise HTTPException(status_code=404, detail=f"Stop '{stop_id}' not found.")

        data = stop.iloc[0].to_dict()
        score, category = predict_suitability(data)
        pos, neg = analyze_factors(data)
        recs = generate_recommendations(data)

        return {
            "Data": data,
            "Analysis": {
                "Suitability_Score": score,
                "Suitability_Category": category,
                "Positive_Factors": pos,
                "Negative_Factors": neg,
                "Recommendations": recs,
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error in get_bus_stop: %s", exc)
        raise HTTPException(status_code=500, detail="Internal error fetching bus stop.")


@router.get("/simulation/results", tags=["Simulation"])
def get_simulation_results() -> Dict[str, Any]:
    """
    Return the latest SUMO simulation comparison report.

    Returns HTTP 404 if the simulation has not been run yet.
    """
    logger.info("GET /simulation/results")
    report_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../../../../simulation/results/comparison_report.json",
    )
    if not os.path.exists(report_path):
        raise HTTPException(
            status_code=404,
            detail="Simulation report not found. Run the simulation script first.",
        )
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.exception("Error reading simulation report: %s", exc)
        raise HTTPException(status_code=500, detail="Error reading simulation report.")
