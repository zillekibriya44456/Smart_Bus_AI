"""
SQLAlchemy ORM domain model for the bus_stops table.
"""
from sqlalchemy import Column, Float, Index, Integer, String

from app.core.database import Base


class BusStop(Base):
    """Persisted bus stop record with precomputed suitability scores."""

    __tablename__ = "bus_stops"

    id = Column(Integer, primary_key=True, index=True)
    Stop_ID = Column(String, unique=True, index=True, nullable=False)

    # Geographic
    Latitude = Column(Float, nullable=True)
    Longitude = Column(Float, nullable=True)

    # Demand
    Passenger_Count = Column(Integer, nullable=True)
    Boarding = Column(Integer, nullable=True)
    Alighting = Column(Integer, nullable=True)

    # Infrastructure
    Road_Width = Column(Float, nullable=True)
    Walking_Distance_m = Column(Float, nullable=True)
    Distance_to_Next_Stop_m = Column(Float, nullable=True)
    Traffic_Level = Column(String, nullable=True)

    # Service quality
    Bus_Frequency = Column(Integer, nullable=True)
    Waiting_Time_min = Column(Integer, nullable=True)
    Occupancy_pct = Column(Float, nullable=True)

    # Precomputed scores (populated by init_db.py)
    Suitability_Score = Column(Float, nullable=True)
    Suitability_Category = Column(String, nullable=True)

    # Composite spatial index for bounding-box queries
    __table_args__ = (
        Index("ix_bus_stops_lat_lon", "Latitude", "Longitude"),
    )

    def __repr__(self) -> str:
        return (
            f"<BusStop id={self.id} Stop_ID={self.Stop_ID!r} "
            f"score={self.Suitability_Score}>"
        )
