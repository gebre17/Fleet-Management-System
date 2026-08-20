"""Vehicle routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleListResponse,
    VehicleResponse,
    VehicleUpdate,
)
from app.services.vehicle_service import VehicleService

router = APIRouter()


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> VehicleResponse:
    """
    Create a new vehicle.

    Args:
        vehicle_data: Vehicle creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created vehicle
    """
    vehicle = await VehicleService.create_vehicle(
        user_id=current_user.id,
        vehicle_data=vehicle_data,
        db=db,
    )
    return VehicleResponse.model_validate(vehicle)


@router.get("/", response_model=VehicleListResponse)
async def list_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> VehicleListResponse:
    """
    List all vehicles for current user.

    Args:
        skip: Number of records to skip
        limit: Number of records to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        Paginated vehicle list
    """
    vehicles, total = await VehicleService.list_vehicles(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        db=db,
    )

    return VehicleListResponse(
        total=total,
        items=[VehicleResponse.model_validate(v) for v in vehicles],
    )


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> VehicleResponse:
    """
    Get vehicle details.

    Args:
        vehicle_id: Vehicle ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Vehicle details
    """
    vehicle = await VehicleService.get_vehicle(
        vehicle_id=vehicle_id,
        user_id=current_user.id,
        db=db,
    )
    return VehicleResponse.model_validate(vehicle)


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: UUID,
    vehicle_data: VehicleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> VehicleResponse:
    """
    Update vehicle.

    Args:
        vehicle_id: Vehicle ID
        vehicle_data: Update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated vehicle
    """
    vehicle = await VehicleService.update_vehicle(
        vehicle_id=vehicle_id,
        user_id=current_user.id,
        vehicle_data=vehicle_data,
        db=db,
    )
    return VehicleResponse.model_validate(vehicle)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Delete vehicle.

    Args:
        vehicle_id: Vehicle ID
        current_user: Current authenticated user
        db: Database session
    """
    await VehicleService.delete_vehicle(
        vehicle_id=vehicle_id,
        user_id=current_user.id,
        db=db,
    )
