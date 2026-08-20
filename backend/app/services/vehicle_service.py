"""Vehicle service."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleService:
    """Service for vehicle operations."""

    @staticmethod
    async def create_vehicle(
        user_id: UUID,
        vehicle_data: VehicleCreate,
        db: AsyncSession,
    ) -> Vehicle:
        """
        Create a new vehicle.

        Args:
            user_id: Owner user ID
            vehicle_data: Vehicle creation data
            db: Database session

        Returns:
            Created vehicle
        """
        vehicle = Vehicle(user_id=user_id, **vehicle_data.model_dump())

        db.add(vehicle)
        await db.commit()
        await db.refresh(vehicle)

        return vehicle

    @staticmethod
    async def get_vehicle(
        vehicle_id: UUID,
        user_id: UUID,
        db: AsyncSession,
    ) -> Vehicle:
        """
        Get vehicle by ID.

        Args:
            vehicle_id: Vehicle ID
            user_id: User ID (for authorization)
            db: Database session

        Returns:
            Vehicle

        Raises:
            HTTPException: If vehicle not found or unauthorized
        """
        stmt = select(Vehicle).where((Vehicle.id == vehicle_id) & (Vehicle.user_id == user_id))
        result = await db.execute(stmt)
        vehicle = result.scalar_one_or_none()

        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found",
            )

        return vehicle

    @staticmethod
    async def list_vehicles(
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        db: AsyncSession = None,
    ) -> tuple[list[Vehicle], int]:
        """
        List vehicles for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Number of records to return
            db: Database session

        Returns:
            Tuple of (vehicles, total_count)
        """
        stmt = select(Vehicle).where(Vehicle.user_id == user_id)

        # Get total count
        count_stmt = select(func.count()).select_from(Vehicle).where(Vehicle.user_id == user_id)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar()

        # Get paginated results
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        vehicles = result.scalars().all()

        return vehicles, total

    @staticmethod
    async def update_vehicle(
        vehicle_id: UUID,
        user_id: UUID,
        vehicle_data: VehicleUpdate,
        db: AsyncSession,
    ) -> Vehicle:
        """
        Update a vehicle.

        Args:
            vehicle_id: Vehicle ID
            user_id: User ID (for authorization)
            vehicle_data: Update data
            db: Database session

        Returns:
            Updated vehicle
        """
        vehicle = await VehicleService.get_vehicle(vehicle_id, user_id, db)

        update_data = vehicle_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(vehicle, key, value)

        await db.commit()
        await db.refresh(vehicle)

        return vehicle

    @staticmethod
    async def delete_vehicle(
        vehicle_id: UUID,
        user_id: UUID,
        db: AsyncSession,
    ) -> None:
        """
        Delete a vehicle, along with its location history, alerts, and
        geofence assignments (cascaded at the DB level).

        Args:
            vehicle_id: Vehicle ID
            user_id: User ID (for authorization)
            db: Database session
        """
        vehicle = await VehicleService.get_vehicle(vehicle_id, user_id, db)
        await db.delete(vehicle)
        await db.commit()

    @staticmethod
    async def get_vehicle_by_device_id(
        device_id: str,
        db: AsyncSession,
    ) -> Vehicle | None:
        """
        Get vehicle by device ID.

        Args:
            device_id: IoT device ID
            db: Database session

        Returns:
            Vehicle or None
        """
        stmt = select(Vehicle).where(Vehicle.device_id == device_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
