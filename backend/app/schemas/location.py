"""Pydantic schemas for locations."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    """Base location schema."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: float | None = None
    speed: float | None = Field(None, ge=0)
    heading: float | None = Field(None, ge=0, le=360)
    accuracy: float | None = Field(None, ge=0)
    battery_level: int | None = Field(None, ge=0, le=100)
    timestamp: datetime | None = None


class LocationCreate(LocationBase):
    """Schema for creating a location."""

    pass


class LocationResponse(LocationBase):
    """Schema for location response."""

    id: UUID
    vehicle_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class LocationHistoryResponse(BaseModel):
    """Schema for location history."""

    total: int
    items: list[LocationResponse]
