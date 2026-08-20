"""
Pydantic request/response schemas for the Smart Bus Stop API.

All request bodies are validated before reaching the service layer.
Invalid inputs produce HTTP 422 with a structured error response.
"""
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ── Request schemas ────────────────────────────────────────────────────────────

class LocationRequest(BaseModel):
    """Explicit location feature values supplied by the user."""

    Passenger_Count: int = Field(..., ge=0, description="Total expected passengers per hour.")
    Boarding: int = Field(..., ge=0, description="Number of passengers boarding per hour.")
    Alighting: int = Field(..., ge=0, description="Number of passengers alighting per hour.")
    Road_Width: float = Field(..., gt=0, description="Road width in metres.")
    Walking_Distance_m: float = Field(..., ge=0, description="Pedestrian walking distance to stop (metres).")
    Distance_to_Next_Stop_m: float = Field(..., ge=0, description="Distance to the nearest adjacent stop (metres).")
    Traffic_Level: Literal["Low", "Moderate", "High"] = Field(
        ..., description="Traffic intensity at the location."
    )
    Bus_Frequency: int = Field(..., ge=0, description="Number of buses per hour.")
    Waiting_Time_min: int = Field(..., ge=0, description="Average passenger waiting time (minutes).")
    Occupancy_pct: float = Field(..., ge=0, le=100, description="Average bus occupancy percentage.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
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
            ]
        }
    }


class CoordinateRequest(BaseModel):
    """Geographic coordinate pair for spatial analysis."""

    Latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees.")
    Longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees.")


class OptimizationRequest(BaseModel):
    """Search area for the bus stop optimization algorithm."""

    Latitude: float = Field(..., ge=-90, le=90)
    Longitude: float = Field(..., ge=-180, le=180)
    Radius_km: float = Field(..., gt=0, le=10, description="Search radius in kilometres (max 10 km).")


class CompareLocationsRequest(BaseModel):
    """Two explicit locations to compare side-by-side."""

    Location_A: LocationRequest
    Location_B: LocationRequest


class InfrastructureRequest(BaseModel):
    """Minimal feature set for infrastructure recommendations."""

    Passenger_Count: int = Field(..., ge=0)
    Traffic_Level: Literal["Low", "Moderate", "High"]
    Road_Width: float = Field(..., gt=0)


# ── Response schemas ───────────────────────────────────────────────────────────

class LocationResponse(BaseModel):
    """Full suitability analysis result for a single location."""

    Suitability_Score: float
    Suitability_Category: str
    SubScores: Dict[str, Any]
    Priority_Score: Optional[int] = None
    Priority_Category: Optional[str] = None
    Positive_Factors: List[str]
    Negative_Factors: List[str]
    Recommendations: List[str]
    Analysis_Type: str = "Explicit"
    Derived_From_Coordinates: Optional[Dict[str, Any]] = None


class OptimizationCandidate(BaseModel):
    """A single ranked candidate location from the optimization algorithm."""

    Rank: int
    Latitude: float
    Longitude: float
    Suitability_Score: float
    Suitability_Category: str
    Positive_Factors: List[str]
    Negative_Factors: List[str]
    Derived_Features: Dict[str, Any]


class OptimizationResponse(BaseModel):
    """Response from the /optimize-location endpoint."""

    Center_Latitude: float
    Center_Longitude: float
    Radius_km: float
    Disclaimer: str = (
        "AI-generated candidate locations based on available project data and configured "
        "constraints. These are derived estimations, not officially approved engineering locations."
    )
    Candidates: List[OptimizationCandidate]


class CompareLocationsResponse(BaseModel):
    """Side-by-side comparison of two locations with a recommendation."""

    Location_A_Response: LocationResponse
    Location_B_Response: LocationResponse
    Recommended_Location: str
    Recommendation_Reason: str


class CorridorRequest(BaseModel):
    """Request for Corridor Analysis bounding start and end points."""

    Start_Latitude: float = Field(..., ge=-90, le=90)
    Start_Longitude: float = Field(..., ge=-180, le=180)
    End_Latitude: float = Field(..., ge=-90, le=90)
    End_Longitude: float = Field(..., ge=-180, le=180)
    Buffer_m: float = Field(500.0, gt=0, le=5000, description="Buffer width in metres on either side of the line.")


class RelocationCandidate(BaseModel):
    """A recommended candidate for a relocated bus stop."""

    Latitude: float
    Longitude: float
    New_Score: float
    Improvement: float
    Distance_Moved_m: float
    Reason: str


class CorridorDecision(BaseModel):
    """Decision and data for a single bus stop in the corridor."""

    Stop_ID: str
    Current_Latitude: float
    Current_Longitude: float
    Current_Score: float
    Decision: Literal["RETAIN", "IMPROVE", "RELOCATE", "REMOVE"]
    Positive_Factors: List[str]
    Negative_Factors: List[str]
    Explanation: str
    Recommended_Location: Optional[RelocationCandidate] = None
    Alternatives: List[RelocationCandidate] = Field(default_factory=list)


class CorridorAnalysisResponse(BaseModel):
    """Aggregated response for a corridor analysis."""

    Total_Stops_Analyzed: int
    Count_Retain: int
    Count_Improve: int
    Count_Relocate: int
    Count_Remove: int
    Average_Score_Before: float
    Average_Score_After: float
    Decisions: List[CorridorDecision]

