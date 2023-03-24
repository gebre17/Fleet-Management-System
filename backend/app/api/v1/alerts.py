"""Alert routes."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.core.security import get_current_user
from app.models.user import User
from app.models.alert import AlertType
from app.services.alert_service import alert_service
from app.schemas.alert import AlertResponse, AlertListResponse, AlertUpdateRequest

router = APIRouter()


@router.get("/", response_model=AlertListResponse)
async def list_alerts(
    vehicle_id: Optional[UUID] = Query(None),
    alert_type: Optional[str] = Query(None),
    is_read: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> AlertListResponse:
    """
    List alerts with filters.
    
    Args:
        vehicle_id: Filter by vehicle ID
        alert_type: Filter by alert type
        is_read: Filter by read status
        skip: Number of records to skip
        limit: Number of records to return
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Paginated alert list
    """
    alert_type_enum = None
    if alert_type:
        try:
            alert_type_enum = AlertType(alert_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid alert type: {alert_type}",
            )
    
    alerts, total = await alert_service.list_alerts(
        vehicle_id=vehicle_id,
        alert_type=alert_type_enum,
        is_read=is_read,
        skip=skip,
        limit=limit,
        db=db,
    )
    
    return AlertListResponse(
        total=total,
        items=[AlertResponse.model_validate(a) for a in alerts],
    )


@router.put("/{alert_id}/read", response_model=AlertResponse)
async def mark_alert_as_read(
    alert_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> AlertResponse:
    """
    Mark alert as read.
    
    Args:
        alert_id: Alert ID
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated alert
    """
    alert = await alert_service.mark_alert_as_read(
        alert_id=alert_id,
        db=db,
    )
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    
    return AlertResponse.model_validate(alert)


@router.put("/read-all", response_model=dict)
async def mark_all_alerts_as_read(
    vehicle_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Mark all alerts as read.
    
    Args:
        vehicle_id: Optional vehicle ID to filter
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Count of updated alerts
    """
    count = await alert_service.mark_all_alerts_as_read(
        vehicle_id=vehicle_id,
        db=db,
    )
    
    return {"alerts_updated": count}
