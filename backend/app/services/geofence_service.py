"""Geofence service."""

from uuid import UUID

import redis.asyncio as redis
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.geofence import Geofence, GeofenceType, GeofenceVehicle
from app.schemas.geofence import GeofenceCreate, GeofenceUpdate
from app.utils.geo import point_in_circle, point_in_polygon


class GeofenceService:
    """Service for geofence operations."""

    def __init__(self, redis_url: str = settings.REDIS_URL):
        """
        Initialize geofence service.

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

    async def create_geofence(
        self,
        user_id: UUID,
        geofence_data: GeofenceCreate,
        db: AsyncSession,
    ) -> Geofence:
        """
        Create a new geofence.

        Args:
            user_id: Owner user ID
            geofence_data: Geofence creation data
            db: Database session

        Returns:
            Created geofence
        """
        geofence = Geofence(owner_id=user_id, **geofence_data.model_dump())

        db.add(geofence)
        await db.commit()
        await db.refresh(geofence)

        return geofence

    @staticmethod
    async def get_geofence(
        geofence_id: UUID,
        user_id: UUID,
        db: AsyncSession,
    ) -> Geofence:
        """
        Get geofence by ID.

        Args:
            geofence_id: Geofence ID
            user_id: User ID (for authorization)
            db: Database session

        Returns:
            Geofence

        Raises:
            HTTPException: If geofence not found or unauthorized
        """
        stmt = select(Geofence).where((Geofence.id == geofence_id) & (Geofence.owner_id == user_id))
        result = await db.execute(stmt)
        geofence = result.scalar_one_or_none()

        if not geofence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Geofence not found",
            )

        return geofence

    @staticmethod
    async def list_geofences(
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        db: AsyncSession = None,
    ) -> tuple[list[Geofence], int]:
        """
        List geofences for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Number of records to return
            db: Database session

        Returns:
            Tuple of (geofences, total_count)
        """
        stmt = select(Geofence).where(Geofence.owner_id == user_id)

        # Get total count
        count_stmt = select(func.count()).select_from(Geofence).where(Geofence.owner_id == user_id)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar()

        # Get paginated results
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        geofences = result.scalars().all()

        return geofences, total

    @staticmethod
    async def update_geofence(
        geofence_id: UUID,
        user_id: UUID,
        geofence_data: GeofenceUpdate,
        db: AsyncSession,
    ) -> Geofence:
        """
        Update a geofence.

        Args:
            geofence_id: Geofence ID
            user_id: User ID (for authorization)
            geofence_data: Update data
            db: Database session

        Returns:
            Updated geofence
        """
        geofence = await GeofenceService.get_geofence(geofence_id, user_id, db)

        update_data = geofence_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(geofence, key, value)

        await db.commit()
        await db.refresh(geofence)

        return geofence

    @staticmethod
    async def delete_geofence(
        geofence_id: UUID,
        user_id: UUID,
        db: AsyncSession,
    ) -> None:
        """
        Delete a geofence.

        Args:
            geofence_id: Geofence ID
            user_id: User ID (for authorization)
            db: Database session
        """
        geofence = await GeofenceService.get_geofence(geofence_id, user_id, db)
        await db.delete(geofence)
        await db.commit()

    @staticmethod
    async def assign_vehicle_to_geofence(
        geofence_id: UUID,
        vehicle_id: UUID,
        user_id: UUID,
        alert_on_enter: bool = True,
        alert_on_exit: bool = True,
        db: AsyncSession = None,
    ) -> GeofenceVehicle:
        """
        Assign a vehicle to a geofence.

        Args:
            geofence_id: Geofence ID
            vehicle_id: Vehicle ID
            user_id: User ID (for authorization)
            alert_on_enter: Alert on geofence enter
            alert_on_exit: Alert on geofence exit
            db: Database session

        Returns:
            Created assignment
        """
        # Verify ownership
        await GeofenceService.get_geofence(geofence_id, user_id, db)

        assignment = GeofenceVehicle(
            geofence_id=geofence_id,
            vehicle_id=vehicle_id,
            alert_on_enter=alert_on_enter,
            alert_on_exit=alert_on_exit,
        )

        db.add(assignment)
        await db.commit()
        await db.refresh(assignment)

        return assignment

    @staticmethod
    async def list_assigned_vehicles(
        geofence_id: UUID,
        user_id: UUID,
        db: AsyncSession,
    ) -> list[GeofenceVehicle]:
        """
        List vehicle assignments for a geofence.

        Args:
            geofence_id: Geofence ID
            user_id: User ID (for authorization)
            db: Database session

        Returns:
            List of geofence-vehicle assignments
        """
        await GeofenceService.get_geofence(geofence_id, user_id, db)

        stmt = select(GeofenceVehicle).where(GeofenceVehicle.geofence_id == geofence_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def unassign_vehicle_from_geofence(
        geofence_id: UUID,
        vehicle_id: UUID,
        user_id: UUID,
        db: AsyncSession = None,
    ) -> None:
        """
        Remove vehicle from geofence.

        Args:
            geofence_id: Geofence ID
            vehicle_id: Vehicle ID
            user_id: User ID (for authorization)
            db: Database session
        """
        # Verify ownership
        await GeofenceService.get_geofence(geofence_id, user_id, db)

        stmt = select(GeofenceVehicle).where(
            (GeofenceVehicle.geofence_id == geofence_id) & (GeofenceVehicle.vehicle_id == vehicle_id)
        )
        result = await db.execute(stmt)
        assignment = result.scalar_one_or_none()

        if assignment:
            await db.delete(assignment)
            await db.commit()

    @staticmethod
    def is_point_in_geofence(
        latitude: float,
        longitude: float,
        geofence: Geofence,
    ) -> bool:
        """
        Check if a point is inside a geofence.

        Args:
            latitude: Point latitude
            longitude: Point longitude
            geofence: Geofence to check against

        Returns:
            True if point is inside geofence, False otherwise
        """
        if geofence.type == GeofenceType.CIRCLE:
            return point_in_circle(
                latitude,
                longitude,
                geofence.center_lat,
                geofence.center_lng,
                geofence.radius_meters,
            )
        elif geofence.type == GeofenceType.POLYGON:
            return point_in_polygon(latitude, longitude, geofence.coordinates)

        return False


# Global geofence service instance
geofence_service = GeofenceService()
