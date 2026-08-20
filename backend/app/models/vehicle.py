"""Vehicle model."""

import enum
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, Integer, String

from app.core.database import Base
from app.models.types import GUID


class VehicleType(str, enum.Enum):
    """Vehicle types."""

    CAR = "car"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"
    VAN = "van"


class VehicleStatus(str, enum.Enum):
    """Vehicle status."""

    ACTIVE = "active"
    IDLE = "idle"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class Vehicle(Base):
    """Vehicle model."""

    __tablename__ = "vehicles"

    id = Column(GUID, primary_key=True, default=uuid4)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    plate_number = Column(String(20), unique=True, nullable=False, index=True)
    type = Column(Enum(VehicleType), nullable=False)
    make = Column(String(50))
    model = Column(String(50))
    year = Column(Integer)
    device_id = Column(String(100), unique=True, index=True)
    status = Column(
        Enum(VehicleStatus),
        default=VehicleStatus.OFFLINE,
        nullable=False,
    )
    color = Column(String(30))
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    __table_args__ = (Index("ix_vehicles_user_id", "user_id"),)
