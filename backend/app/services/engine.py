"""
Deterministic scoring engine for bus stop suitability analysis.

Provides:
  - calculate_sub_scores       — weighted dimension scores (0–100 each)
  - calculate_improvement_priority — urgency × demand priority ranking
  - analyze_factors            — human-readable positive/negative factor lists
  - generate_recommendations   — infrastructure recommendation strings
"""
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# Traffic level → safety score lookup
_TRAFFIC_SAFETY_MAP: Dict[str, int] = {"Low": 100, "Moderate": 60, "High": 20}

# Suitability category thresholds (shared with ml_service.py)
_PRIORITY_THRESHOLDS: List[Tuple[int, str]] = [
    (75, "Critical"),
    (50, "High"),
    (25, "Medium"),
    (0, "Low"),
]


def calculate_sub_scores(data: dict) -> Dict[str, int]:
    """
    Calculate normalised sub-scores (0–100) for each suitability dimension.

    Dimensions: Demand, Road, Accessibility, Safety, Spacing.

    Args:
        data: Feature dictionary.  Missing keys are handled with safe defaults.

    Returns:
        Dict mapping dimension name → integer score.
    """
    # Demand — capped at 100 passengers
    passenger_count = float(data.get("Passenger_Count", 0))
    demand_score = min((passenger_count / 100) * 100, 100)

    # Road — optimal width is ≥15 m
    road_width = float(data.get("Road_Width", 0))
    road_score = min((road_width / 15) * 100, 100)

    # Accessibility — <100 m is perfect (100), >800 m is 0
    walk_dist = float(data.get("Walking_Distance_m", 400))
    acc_score = max(0, min(100, 100 - ((walk_dist - 100) / 7)))

    # Safety — derived from traffic level
    traffic_level = str(data.get("Traffic_Level", "Moderate"))
    safe_score = _TRAFFIC_SAFETY_MAP.get(traffic_level, 60)
    if traffic_level not in _TRAFFIC_SAFETY_MAP:
        logger.warning("Unexpected Traffic_Level value '%s'; defaulting safety score to 60.", traffic_level)

    # Spacing — optimal range is 300–800 m from next stop
    dist = float(data.get("Distance_to_Next_Stop_m", 600))
    if dist < 300:
        spacing_score = 40
    elif dist <= 800:
        spacing_score = 100
    else:
        spacing_score = max(20, 100 - ((dist - 800) / 10))

    return {
        "Demand": round(demand_score),
        "Road": round(road_score),
        "Accessibility": round(acc_score),
        "Safety": round(safe_score),
        "Spacing": round(spacing_score),
    }


def calculate_improvement_priority(sub_scores: Dict[str, int]) -> Tuple[int, str]:
    """
    Derive an improvement priority score and category.

    Priority = (100 − worst_infrastructure_score) × demand_multiplier

    Args:
        sub_scores: Output of calculate_sub_scores().

    Returns:
        Tuple of (priority_score: int, category: str).
    """
    worst_score = min(sub_scores["Safety"], sub_scores["Accessibility"], sub_scores["Road"])
    urgency = 100 - worst_score
    demand_multiplier = sub_scores["Demand"] / 100.0
    priority_score = round(urgency * demand_multiplier)

    category = "Low"
    for threshold, label in _PRIORITY_THRESHOLDS:
        if priority_score >= threshold:
            category = label
            break

    logger.debug("Priority score=%d category=%s", priority_score, category)
    return priority_score, category


def analyze_factors(data: dict) -> Tuple[List[str], List[str]]:
    """
    Produce lists of positive and negative factors for a bus stop location.

    Args:
        data: Feature dictionary.

    Returns:
        Tuple of (positive_factors, negative_factors).
    """
    positive: List[str] = []
    negative: List[str] = []

    passenger_count = float(data.get("Passenger_Count", 0))
    if passenger_count > 60:
        positive.append("High passenger demand justifies stop placement.")
    elif passenger_count < 20:
        negative.append("Low passenger demand limits utility.")

    road_width = float(data.get("Road_Width", 0))
    if road_width >= 12:
        positive.append("Wide road provides ample space for bus bay.")
    elif road_width < 8:
        negative.append("Narrow road may cause traffic bottlenecks.")

    walk_dist = float(data.get("Walking_Distance_m", 400))
    if walk_dist <= 300:
        positive.append("Excellent pedestrian accessibility (<300 m).")
    else:
        negative.append("Poor pedestrian accessibility.")

    traffic_level = str(data.get("Traffic_Level", "Moderate"))
    if traffic_level == "High":
        negative.append("High traffic congestion reported in this area.")

    dist = float(data.get("Distance_to_Next_Stop_m", 600))
    if 500 <= dist <= 1000:
        positive.append("Optimal distance to neighboring stops.")
    elif dist < 500:
        negative.append("Too close to next stop, risking cluster inefficiencies.")
    else:
        negative.append("Isolated stop — may increase walking distances for users.")

    return positive, negative


def generate_recommendations(data: dict) -> List[str]:
    """
    Generate infrastructure recommendations based on demand, traffic, and road width.

    Args:
        data: Feature dictionary.

    Returns:
        List of recommendation strings.
    """
    recs: List[str] = []
    demand = float(data.get("Passenger_Count", 0))
    traffic = str(data.get("Traffic_Level", "Moderate"))
    road_width = float(data.get("Road_Width", 0))

    if demand >= 80:
        recs.extend([
            "Large smart bus shelter with digital display.",
            "At least 40 seats.",
            "Multiple bus bays required.",
            "Install CCTV for security.",
        ])
    elif demand >= 40:
        recs.extend([
            "Medium shelter with basic amenities.",
            "At least 25 seats.",
            "1–2 bus bays.",
        ])
        if traffic in ("Moderate", "High"):
            recs.append("Zebra crossing and pedestrian signals.")
    else:
        recs.extend([
            "Small shelter (1 bus bay).",
            "10–15 seats.",
        ])

    if road_width >= 10:
        recs.append("Construct dedicated bus pull-out bay.")

    return recs
