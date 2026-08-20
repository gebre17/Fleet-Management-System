"""Pydantic schemas for geofences."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.geofence import GeofenceType


class GeofenceBase(BaseModel):
    """Base geofence schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    type: GeofenceType
    center_lat: float | None = Field(None, ge=-90, le=90)
    center_lng: float | None = Field(None, ge=-180, le=180)
    radius_meters: float | None = Field(None, gt=0)
    coordinates: list[tuple[float, float]] | None = None
    color: str = Field("#3B82F6", max_length=7)


class GeofenceCreate(GeofenceBase):
    """Schema for creating a geofence."""

    pass


class GeofenceUpdate(BaseModel):
    """Schema for updating a geofence."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    center_lat: float | None = Field(None, ge=-90, le=90)
    center_lng: float | None = Field(None, ge=-180, le=180)
    radius_meters: float | None = Field(None, gt=0)
    color: str | None = Field(None, max_length=7)
    is_active: bool | None = None


class GeofenceResponse(GeofenceBase):
    """Schema for geofence response."""

    id: UUID
    owner_id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class GeofenceListResponse(BaseModel):
    """Schema for geofence list response."""

    total: int
    items: list[GeofenceResponse]


class GeofenceVehicleAssignmentRequest(BaseModel):
    """Schema for assigning vehicles to geofences."""

    vehicle_id: UUID
    alert_on_enter: bool = True
    alert_on_exit: bool = True


class GeofenceVehicleResponse(BaseModel):
    """Schema for a vehicle assigned to a geofence."""

    vehicle_id: UUID
    alert_on_enter: bool
    alert_on_exit: bool

    class Config:
        from_attributes = True
