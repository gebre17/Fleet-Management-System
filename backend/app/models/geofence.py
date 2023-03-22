"""Geofence model."""
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
import enum


class GeofenceType(str, enum.Enum):
    """Geofence types."""
    CIRCLE = "circle"
    POLYGON = "polygon"


class Geofence(Base):
    """Geofence model."""
    __tablename__ = "geofences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String)
    type = Column(Enum(GeofenceType), nullable=False)
    # For circle
    center_lat = Column(Float)
    center_lng = Column(Float)
    radius_meters = Column(Float)
    # For polygon
    coordinates = Column(JSONB)  # [[lat,lng], [lat,lng], ...]
    color = Column(String(7), default="#3B82F6")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (Index("ix_geofences_owner_id", "owner_id"),)


class GeofenceVehicle(Base):
    """Many-to-many relationship between geofences and vehicles."""
    __tablename__ = "geofence_vehicles"

    geofence_id = Column(UUID(as_uuid=True), ForeignKey("geofences.id"), primary_key=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), primary_key=True)
    alert_on_enter = Column(Boolean, default=True)
    alert_on_exit = Column(Boolean, default=True)

    __table_args__ = (
        Index("ix_geofence_vehicles_geofence_id", "geofence_id"),
        Index("ix_geofence_vehicles_vehicle_id", "vehicle_id"),
    )
