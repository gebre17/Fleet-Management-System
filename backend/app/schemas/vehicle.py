"""Pydantic schemas for vehicles."""
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.vehicle import VehicleType, VehicleStatus


class VehicleBase(BaseModel):
    """Base vehicle schema."""
    name: str = Field(..., min_length=1, max_length=100)
    plate_number: str = Field(..., min_length=1, max_length=20)
    type: VehicleType
    make: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=50)
    year: Optional[int] = None
    device_id: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=30)


class VehicleCreate(VehicleBase):
    """Schema for creating a vehicle."""
    pass


class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    plate_number: Optional[str] = Field(None, min_length=1, max_length=20)
    type: Optional[VehicleType] = None
    make: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=50)
    year: Optional[int] = None
    device_id: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=30)
    status: Optional[VehicleStatus] = None


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
