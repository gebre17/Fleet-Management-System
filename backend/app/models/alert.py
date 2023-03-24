"""Alert model."""
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
import enum


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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    geofence_id = Column(UUID(as_uuid=True), ForeignKey("geofences.id"), nullable=True)
    type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    alert_metadata = Column("metadata", JSONB)  # Additional data like speed, limit, etc.
    triggered_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_alerts_vehicle_id", "vehicle_id"),
    )
