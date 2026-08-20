"""Tracking service."""

import json
from datetime import UTC, datetime
from uuid import UUID

import redis.asyncio as redis
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.location import Location
from app.models.vehicle import Vehicle, VehicleStatus
from app.schemas.location import LocationCreate
from app.services import alert_engine
from app.websocket.manager import manager


class TrackingService:
    """Service for vehicle tracking operations."""

    LOCATION_CACHE_TTL = 300  # 5 minutes

    def __init__(self, redis_url: str = settings.REDIS_URL):
        """
        Initialize tracking service.

        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis_client = None

    async def init(self) -> None:
        """Initialize Redis connection."""
        self.redis_client = await redis.from_url(self.redis_url)

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()

    async def ingest_location(
        self,
        vehicle_id: UUID,
        location_data: LocationCreate,
        db: AsyncSession,
    ) -> Location:
        """
        Ingest a new GPS location point for a vehicle.

        Args:
            vehicle_id: Vehicle ID
            location_data: Location data
            db: Database session

        Returns:
            Created location record
        """
        if not location_data.timestamp:
            location_data.timestamp = datetime.now(UTC)

        # Load the vehicle and its previous location *before* inserting the
        # new one, so the alert engine can detect enter/exit/threshold
        # transitions relative to where the vehicle was a moment ago.
        vehicle = await db.get(Vehicle, vehicle_id)
        previous_location = await self.get_latest_location(vehicle_id, db)

        location = Location(vehicle_id=vehicle_id, **location_data.model_dump())

        db.add(location)
        await db.commit()
        await db.refresh(location)

        if vehicle:
            vehicle.status = VehicleStatus.ACTIVE
            await db.commit()
            await alert_engine.evaluate_location(vehicle, previous_location, location, db)

        if self.redis_client:
            cache_key = f"location:{vehicle_id}"
            cache_payload = {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "speed": location.speed,
                "heading": location.heading,
                "battery_level": location.battery_level,
                "timestamp": location.timestamp.isoformat(),
            }
            await self.redis_client.setex(
                cache_key,
                self.LOCATION_CACHE_TTL,
                json.dumps(cache_payload),
            )

        broadcast_payload = {
            "type": "location_update",
            "vehicle_id": str(vehicle_id),
            "latitude": location.latitude,
            "longitude": location.longitude,
            "speed": location.speed,
            "heading": location.heading,
            "battery_level": location.battery_level,
            "status": vehicle.status.value if vehicle else None,
            "timestamp": location.timestamp.isoformat(),
        }
        await manager.broadcast_to_room(str(vehicle_id), broadcast_payload)
        if vehicle:
            await manager.broadcast_to_room(f"fleet:{vehicle.user_id}", broadcast_payload)

        return location

    async def get_latest_location(
        self,
        vehicle_id: UUID,
        db: AsyncSession,
    ) -> Location | None:
        """
        Get latest location for a vehicle.

        Args:
            vehicle_id: Vehicle ID
            db: Database session

        Returns:
            Latest location or None
        """
        stmt = (
            select(Location)
            .where(Location.vehicle_id == vehicle_id)
            .order_by(desc(Location.timestamp))
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_location_history(
        self,
        vehicle_id: UUID,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 1000,
        db: AsyncSession = None,
    ) -> list[Location]:
        """
        Get location history for a vehicle.

        Args:
            vehicle_id: Vehicle ID
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum records to return
            db: Database session

        Returns:
            List of locations
        """
        stmt = select(Location).where(Location.vehicle_id == vehicle_id)

        if start_time:
            stmt = stmt.where(Location.timestamp >= start_time)

        if end_time:
            stmt = stmt.where(Location.timestamp <= end_time)

        stmt = stmt.order_by(desc(Location.timestamp)).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()


# Global tracking service instance
tracking_service = TrackingService()
