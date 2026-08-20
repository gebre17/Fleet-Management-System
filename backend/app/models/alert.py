"""Alert model."""

import enum
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Index, String

from app.core.database import Base
from app.models.types import GUID


class AlertType(str, enum.Enum):
    """Alert types."""

    GEOFENCE_ENTER = "geofence_enter"
    GEOFENCE_EXIT = "geofence_exit"
    SPEEDING = "speeding"
    OFFLINE = "offline"
    LOW_BATTERY = "low_battery"


class AlertSeverity(str, enum.Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Alert(Base):
    """Alert model."""

    __tablename__ = "alerts"

    id = Column(GUID, primary_key=True, default=uuid4)
    vehicle_id = Column(GUID, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    geofence_id = Column(GUID, ForeignKey("geofences.id", ondelete="SET NULL"), nullable=True)
    type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    alert_metadata = Column("metadata", JSON)  # Additional data like speed, limit, etc.
    triggered_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    __table_args__ = (Index("ix_alerts_vehicle_id", "vehicle_id"),)
