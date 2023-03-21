"""Tracking routes."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.core.security import get_current_user
from app.models.user import User
from app.services.vehicle_service import VehicleService
from app.services.tracking_service import tracking_service
from app.schemas.location import LocationCreate, LocationResponse, LocationHistoryResponse

router = APIRouter()


@router.post("/{vehicle_id}/location", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def ingest_location(
    vehicle_id: UUID,
    location_data: LocationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> LocationResponse:
    """
    Ingest GPS location data for a vehicle.
    
    Args:
        vehicle_id: Vehicle ID
        location_data: Location data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Created location record
    """
    # Verify ownership
    await VehicleService.get_vehicle(
        vehicle_id=vehicle_id,
        user_id=current_user.id,
        db=db,
    )
    
    location = await tracking_service.ingest_location(
        vehicle_id=vehicle_id,
        location_data=location_data,
        db=db,
    )
    
    return LocationResponse.model_validate(location)


@router.get("/{vehicle_id}/location", response_model=Optional[LocationResponse])
async def get_latest_location(
    vehicle_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> Optional[LocationResponse]:
    """
    Get latest GPS location for a vehicle.
    
    Args:
        vehicle_id: Vehicle ID
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Latest location or None
    """
    # Verify ownership
    await VehicleService.get_vehicle(
        vehicle_id=vehicle_id,
        user_id=current_user.id,
        db=db,
    )
    
    location = await tracking_service.get_latest_location(
        vehicle_id=vehicle_id,
        db=db,
    )
    
    if location:
        return LocationResponse.model_validate(location)
    
    return None


@router.get("/{vehicle_id}/history", response_model=LocationHistoryResponse)
async def get_location_history(
    vehicle_id: UUID,
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> LocationHistoryResponse:
    """
    Get location history for a vehicle.
    
    Args:
        vehicle_id: Vehicle ID
        start: Start time filter
        end: End time filter
        limit: Maximum records to return
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Location history
    """
    # Verify ownership
    await VehicleService.get_vehicle(
        vehicle_id=vehicle_id,
        user_id=current_user.id,
        db=db,
    )
    
    locations = await tracking_service.get_location_history(
        vehicle_id=vehicle_id,
        start_time=start,
        end_time=end,
        limit=limit,
        db=db,
    )
    
    return LocationHistoryResponse(
        total=len(locations),
        items=[LocationResponse.model_validate(loc) for loc in locations],
    )
