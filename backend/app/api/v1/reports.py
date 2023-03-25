"""Report routes."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.core.security import get_current_user
from app.models.user import User
from app.services.report_service import report_service

router = APIRouter()


@router.get("/distance")
async def get_distance_report(
    vehicle_id: Optional[UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list:
    """
    Get distance report.
    
    Args:
        vehicle_id: Optional vehicle ID filter
        start_date: Start date filter
        end_date: End date filter
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Distance report data
    """
    return await report_service.get_distance_report(
        vehicle_id=vehicle_id,
        start_date=start_date,
        end_date=end_date,
        db=db,
    )


@router.get("/activity")
async def get_activity_report(
    vehicle_id: Optional[UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list:
    """
    Get activity report.
    
    Args:
        vehicle_id: Optional vehicle ID filter
        start_date: Start date filter
        end_date: End date filter
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Activity report data
    """
    return await report_service.get_activity_report(
        vehicle_id=vehicle_id,
        start_date=start_date,
        end_date=end_date,
        db=db,
    )


@router.get("/speed")
async def get_speed_report(
    vehicle_id: Optional[UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list:
    """
    Get speed report.
    
    Args:
        vehicle_id: Optional vehicle ID filter
        start_date: Start date filter
        end_date: End date filter
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Speed report data
    """
    return await report_service.get_speed_report(
        vehicle_id=vehicle_id,
        start_date=start_date,
        end_date=end_date,
        db=db,
    )


@router.get("/geofence-events")
async def get_geofence_events_report(
    vehicle_id: Optional[UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list:
    """
    Get geofence events report.
    
    Args:
        vehicle_id: Optional vehicle ID filter
        start_date: Start date filter
        end_date: End date filter
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Geofence events report data
    """
    return await report_service.get_geofence_events_report(
        vehicle_id=vehicle_id,
        start_date=start_date,
        end_date=end_date,
        db=db,
    )
