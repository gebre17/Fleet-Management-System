"""Pydantic schemas for vehicles."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.vehicle import VehicleStatus, VehicleType


class VehicleBase(BaseModel):
    """Base vehicle schema."""

    name: str = Field(..., min_length=1, max_length=100)
    plate_number: str = Field(..., min_length=1, max_length=20)
    type: VehicleType
    make: str | None = Field(None, max_length=50)
    model: str | None = Field(None, max_length=50)
    year: int | None = None
    device_id: str | None = Field(None, max_length=100)
    color: str | None = Field(None, max_length=30)


class VehicleCreate(VehicleBase):
    """Schema for creating a vehicle."""

    pass


class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle."""

    name: str | None = Field(None, min_length=1, max_length=100)
    plate_number: str | None = Field(None, min_length=1, max_length=20)
    type: VehicleType | None = None
    make: str | None = Field(None, max_length=50)
    model: str | None = Field(None, max_length=50)
    year: int | None = None
    device_id: str | None = Field(None, max_length=100)
    color: str | None = Field(None, max_length=30)
    status: VehicleStatus | None = None


class VehicleResponse(VehicleBase):
    """Schema for vehicle response."""

    id: UUID
    user_id: UUID
    status: VehicleStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VehicleListResponse(BaseModel):
    """Schema for vehicle list response."""

    total: int
    items: list[VehicleResponse]
