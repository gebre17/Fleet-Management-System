"""Pydantic schemas for locations."""
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    """Base location schema."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: Optional[float] = None
    speed: Optional[float] = Field(None, ge=0)
    heading: Optional[float] = Field(None, ge=0, le=360)
    accuracy: Optional[float] = Field(None, ge=0)
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    timestamp: Optional[datetime] = None


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
