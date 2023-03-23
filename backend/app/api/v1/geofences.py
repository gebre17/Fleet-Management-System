"""Geofence routes."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.core.security import get_current_user
from app.models.user import User
from app.services.geofence_service import geofence_service
from app.schemas.geofence import (
    GeofenceCreate,
    GeofenceUpdate,
    GeofenceResponse,
    GeofenceListResponse,
    GeofenceVehicleAssignmentRequest,
)

router = APIRouter()


@router.post("/", response_model=GeofenceResponse, status_code=status.HTTP_201_CREATED)
async def create_geofence(
    geofence_data: GeofenceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> GeofenceResponse:
    """
    Create a new geofence.
    
    Args:
        geofence_data: Geofence creation data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Created geofence
    """
    geofence = await geofence_service.create_geofence(
        user_id=current_user.id,
        geofence_data=geofence_data,
        db=db,
    )
    return GeofenceResponse.model_validate(geofence)


@router.get("/", response_model=GeofenceListResponse)
async def list_geofences(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> GeofenceListResponse:
    """
    List all geofences for current user.
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Paginated geofence list
    """
    geofences, total = await geofence_service.list_geofences(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        db=db,
    )
    
    return GeofenceListResponse(
        total=total,
        items=[GeofenceResponse.model_validate(g) for g in geofences],
    )


@router.get("/{geofence_id}", response_model=GeofenceResponse)
async def get_geofence(
    geofence_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> GeofenceResponse:
    """
    Get geofence details.
    
    Args:
        geofence_id: Geofence ID
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Geofence details
    """
    geofence = await geofence_service.get_geofence(
        geofence_id=geofence_id,
        user_id=current_user.id,
        db=db,
    )
    return GeofenceResponse.model_validate(geofence)


@router.put("/{geofence_id}", response_model=GeofenceResponse)
async def update_geofence(
    geofence_id: UUID,
    geofence_data: GeofenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> GeofenceResponse:
    """
    Update geofence.
    
    Args:
        geofence_id: Geofence ID
        geofence_data: Update data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated geofence
    """
    geofence = await geofence_service.update_geofence(
        geofence_id=geofence_id,
        user_id=current_user.id,
        geofence_data=geofence_data,
        db=db,
    )
    return GeofenceResponse.model_validate(geofence)


@router.delete("/{geofence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_geofence(
    geofence_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Delete geofence.
    
    Args:
        geofence_id: Geofence ID
        current_user: Current authenticated user
        db: Database session
    """
    await geofence_service.delete_geofence(
        geofence_id=geofence_id,
        user_id=current_user.id,
        db=db,
    )


@router.post("/{geofence_id}/vehicles", status_code=status.HTTP_201_CREATED)
async def assign_vehicle_to_geofence(
    geofence_id: UUID,
    assignment: GeofenceVehicleAssignmentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Assign vehicle to geofence.
    
    Args:
        geofence_id: Geofence ID
        assignment: Assignment configuration
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Assignment confirmation
    """
    await geofence_service.assign_vehicle_to_geofence(
        geofence_id=geofence_id,
        vehicle_id=assignment.vehicle_id,
        user_id=current_user.id,
        alert_on_enter=assignment.alert_on_enter,
        alert_on_exit=assignment.alert_on_exit,
        db=db,
    )
    
    return {"message": "Vehicle assigned to geofence"}


@router.delete("/{geofence_id}/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_vehicle_from_geofence(
    geofence_id: UUID,
    vehicle_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Remove vehicle from geofence.
    
    Args:
        geofence_id: Geofence ID
        vehicle_id: Vehicle ID
        current_user: Current authenticated user
        db: Database session
    """
    await geofence_service.unassign_vehicle_from_geofence(
        geofence_id=geofence_id,
        vehicle_id=vehicle_id,
        user_id=current_user.id,
        db=db,
    )
