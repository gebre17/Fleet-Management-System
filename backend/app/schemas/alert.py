"""Pydantic schemas for alerts."""
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.alert import AlertType, AlertSeverity


class AlertBase(BaseModel):
    """Base alert schema."""
    type: AlertType
    severity: AlertSeverity
    message: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class AlertCreate(AlertBase):
    """Schema for creating an alert."""
    vehicle_id: UUID
    geofence_id: Optional[UUID] = None


class AlertResponse(AlertBase):
    """Schema for alert response."""
    id: UUID
    vehicle_id: UUID
    geofence_id: Optional[UUID]
    is_read: bool
    triggered_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """Schema for alert list response."""
    total: int
    items: list[AlertResponse]


class AlertUpdateRequest(BaseModel):
    """Schema for updating an alert."""
    is_read: Optional[bool] = None
