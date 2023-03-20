"""Tracking service."""
from datetime import datetime, timezone, timedelta
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.location import Location
from app.schemas.location import LocationCreate
from app.websocket.manager import manager
import redis.asyncio as redis


class TrackingService:
    """Service for vehicle tracking operations."""
    
    LOCATION_CACHE_TTL = 300  # 5 minutes
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
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
        # Set timestamp if not provided
        if not location_data.timestamp:
            location_data.timestamp = datetime.now(timezone.utc)
        
        # Create location record
        location = Location(
            vehicle_id=vehicle_id,
            **location_data.model_dump()
        )
        
        db.add(location)
        await db.commit()
        await db.refresh(location)
        
        # Update vehicle status
        stmt = select(Vehicle).where(Vehicle.id == vehicle_id)
        result = await db.execute(stmt)
        vehicle = result.scalar_one_or_none()
        
        if vehicle:
            vehicle.status = VehicleStatus.ACTIVE
            await db.commit()
        
        # Cache latest location in Redis
        if self.redis_client:
            cache_key = f"location:{vehicle_id}"
            await self.redis_client.setex(
                cache_key,
                self.LOCATION_CACHE_TTL,
                location.model_dump_json(),
            )
        
        # Broadcast to WebSocket clients
        await manager.broadcast_to_room(
            str(vehicle_id),
            {
                "type": "location_update",
                "vehicle_id": str(vehicle_id),
                "latitude": location.latitude,
                "longitude": location.longitude,
                "speed": location.speed,
                "heading": location.heading,
                "timestamp": location.timestamp.isoformat(),
            }
        )
        
        return location
    
    async def get_latest_location(
        self,
        vehicle_id: UUID,
        db: AsyncSession,
    ) -> Optional[Location]:
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
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
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
