"""Location model."""
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, Index, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Location(Base):
    """Location model for GPS tracking."""
    __tablename__ = "locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float)
    speed = Column(Float)  # km/h
    heading = Column(Float)  # 0-360 degrees
    accuracy = Column(Float)  # GPS accuracy in meters
    battery_level = Column(Integer)  # device battery %
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_locations_vehicle_id", "vehicle_id"),
        Index("ix_locations_vehicle_timestamp", "vehicle_id", "timestamp"),
    )
