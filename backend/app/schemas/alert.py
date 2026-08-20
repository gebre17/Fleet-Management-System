"""Pydantic schemas for alerts."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.alert import AlertSeverity, AlertType


class AlertBase(BaseModel):
    """Base alert schema."""

    model_config = ConfigDict(populate_by_name=True)

    type: AlertType
    severity: AlertSeverity
    message: str = Field(..., min_length=1)
    # The ORM attribute is `alert_metadata` (SQLAlchemy reserves `.metadata`
    # on declarative models — a plain `alias="metadata"` would make
    # from_attributes validation read that reserved attribute instead of
    # falling back to the real one). serialization_alias keeps the JSON
    # response key as the friendlier `metadata` without touching how the
    # field is read off the ORM object.
    alert_metadata: dict[str, Any] | None = Field(None, serialization_alias="metadata")


class AlertCreate(AlertBase):
    """Schema for creating an alert."""

    vehicle_id: UUID
    geofence_id: UUID | None = None


class AlertResponse(AlertBase):
    """Schema for alert response."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID
    vehicle_id: UUID
    geofence_id: UUID | None
    is_read: bool
    triggered_at: datetime
    created_at: datetime


class AlertListResponse(BaseModel):
    """Schema for alert list response."""

    total: int
    items: list[AlertResponse]


class AlertUpdateRequest(BaseModel):
    """Schema for updating an alert."""

    is_read: bool | None = None
