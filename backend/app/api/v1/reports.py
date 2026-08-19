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
    """Get distance report, scoped to the current user's vehicles."""
    return await report_service.get_distance_report(
        user_id=current_user.id,
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
    """Get activity report, scoped to the current user's vehicles."""
    return await report_service.get_activity_report(
        user_id=current_user.id,
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
    """Get speed report, scoped to the current user's vehicles."""
    return await report_service.get_speed_report(
        user_id=current_user.id,
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
    """Get geofence events report, scoped to the current user's vehicles."""
    return await report_service.get_geofence_events_report(
        user_id=current_user.id,
        vehicle_id=vehicle_id,
        start_date=start_date,
        end_date=end_date,
        db=db,
    )
