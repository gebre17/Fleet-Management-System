"""Geofence model."""

import enum
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, Float, ForeignKey, Index, String

from app.core.database import Base
from app.models.types import GUID


class GeofenceType(str, enum.Enum):
    """Geofence types."""

    CIRCLE = "circle"
    POLYGON = "polygon"


class Geofence(Base):
    """Geofence model."""

    __tablename__ = "geofences"

    id = Column(GUID, primary_key=True, default=uuid4)
    owner_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String)
    type = Column(Enum(GeofenceType), nullable=False)
    # For circle
    center_lat = Column(Float)
    center_lng = Column(Float)
    radius_meters = Column(Float)
    # For polygon
    coordinates = Column(JSON)  # [[lat,lng], [lat,lng], ...]
    color = Column(String(7), default="#3B82F6")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    __table_args__ = (Index("ix_geofences_owner_id", "owner_id"),)


class GeofenceVehicle(Base):
    """Many-to-many relationship between geofences and vehicles."""

    __tablename__ = "geofence_vehicles"

    geofence_id = Column(GUID, ForeignKey("geofences.id", ondelete="CASCADE"), primary_key=True)
    vehicle_id = Column(GUID, ForeignKey("vehicles.id", ondelete="CASCADE"), primary_key=True)
    alert_on_enter = Column(Boolean, default=True)
    alert_on_exit = Column(Boolean, default=True)

    __table_args__ = (
        Index("ix_geofence_vehicles_geofence_id", "geofence_id"),
        Index("ix_geofence_vehicles_vehicle_id", "vehicle_id"),
    )
