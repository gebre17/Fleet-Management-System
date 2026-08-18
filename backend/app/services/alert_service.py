"""Alert service."""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from app.models.alert import Alert, AlertType, AlertSeverity
from app.models.vehicle import Vehicle
from app.websocket.manager import manager


class AlertService:
    """Service for alert operations."""

    @staticmethod
    async def create_alert(
        vehicle_id: UUID,
        alert_type: AlertType,
        severity: AlertSeverity,
        message: str,
        db: AsyncSession,
        geofence_id: Optional[UUID] = None,
        metadata: Optional[dict] = None,
        owner_id: Optional[UUID] = None,
    ) -> Alert:
        """
        Create a new alert.

        Args:
            vehicle_id: Vehicle ID
            alert_type: Alert type
            severity: Alert severity
            message: Alert message
            db: Database session
            geofence_id: Associated geofence (optional)
            metadata: Additional metadata
            owner_id: Vehicle owner's user ID, used to scope the realtime
                broadcast to that user's connections. If omitted, it is
                looked up from the vehicle.

        Returns:
            Created alert
        """
        alert = Alert(
            vehicle_id=vehicle_id,
            geofence_id=geofence_id,
            type=alert_type,
            severity=severity,
            message=message,
            alert_metadata=metadata or {},
            triggered_at=datetime.now(timezone.utc),
        )

        db.add(alert)
        await db.commit()
        await db.refresh(alert)

        if owner_id is None:
            stmt = select(Vehicle.user_id).where(Vehicle.id == vehicle_id)
            result = await db.execute(stmt)
            owner_id = result.scalar_one_or_none()

        payload = {
            "type": "alert",
            "alert_id": str(alert.id),
            "vehicle_id": str(vehicle_id),
            "alert_type": alert.type.value,
            "severity": alert.severity.value,
            "message": message,
            "timestamp": alert.triggered_at.isoformat(),
        }
        # Notify anyone watching this specific vehicle, plus the owner's
        # fleet-wide feed (never a blanket broadcast to every connection).
        await manager.broadcast_to_room(str(vehicle_id), payload)
        if owner_id:
            await manager.broadcast_to_room(f"fleet:{owner_id}", payload)

        return alert

    @staticmethod
    async def list_alerts(
        user_id: UUID,
        vehicle_id: Optional[UUID] = None,
        alert_type: Optional[AlertType] = None,
        is_read: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
        db: AsyncSession = None,
    ) -> tuple[List[Alert], int]:
        """
        List alerts, scoped to vehicles owned by ``user_id``, with filters.

        Args:
            user_id: Owning user's ID (authorization scope)
            vehicle_id: Filter by vehicle ID
            alert_type: Filter by alert type
            is_read: Filter by read status
            skip: Number of records to skip
            limit: Number of records to return
            db: Database session

        Returns:
            Tuple of (alerts, total_count)
        """
        stmt = select(Alert).join(Vehicle, Vehicle.id == Alert.vehicle_id)

        filters = [Vehicle.user_id == user_id]
        if vehicle_id:
            filters.append(Alert.vehicle_id == vehicle_id)
        if alert_type:
            filters.append(Alert.type == alert_type)
        if is_read is not None:
            filters.append(Alert.is_read == is_read)

        stmt = stmt.where(and_(*filters))

        count_stmt = (
            select(func.count())
            .select_from(Alert)
            .join(Vehicle, Vehicle.id == Alert.vehicle_id)
            .where(and_(*filters))
        )
        count_result = await db.execute(count_stmt)
        total = count_result.scalar()

        stmt = stmt.order_by(desc(Alert.triggered_at)).offset(skip).limit(limit)
        result = await db.execute(stmt)
        alerts = result.scalars().all()

        return alerts, total

    @staticmethod
    async def mark_alert_as_read(
        alert_id: UUID,
        user_id: UUID,
        db: AsyncSession,
    ) -> Optional[Alert]:
        """
        Mark an alert as read, if it belongs to a vehicle owned by ``user_id``.

        Args:
            alert_id: Alert ID
            user_id: Owning user's ID (authorization scope)
            db: Database session

        Returns:
            Updated alert, or None if not found / not owned by the user
        """
        stmt = (
            select(Alert)
            .join(Vehicle, Vehicle.id == Alert.vehicle_id)
            .where(Alert.id == alert_id, Vehicle.user_id == user_id)
        )
        result = await db.execute(stmt)
        alert = result.scalar_one_or_none()

        if alert:
            alert.is_read = True
            await db.commit()
            await db.refresh(alert)

        return alert

    @staticmethod
    async def mark_all_alerts_as_read(
        user_id: UUID,
        vehicle_id: Optional[UUID] = None,
        db: AsyncSession = None,
    ) -> int:
        """
        Mark all of a user's alerts as read.

        Args:
            user_id: Owning user's ID (authorization scope)
            vehicle_id: Optional vehicle ID to filter
            db: Database session

        Returns:
            Number of alerts updated
        """
        stmt = (
            select(Alert)
            .join(Vehicle, Vehicle.id == Alert.vehicle_id)
            .where(Alert.is_read == False, Vehicle.user_id == user_id)  # noqa: E712
        )

        if vehicle_id:
            stmt = stmt.where(Alert.vehicle_id == vehicle_id)

        result = await db.execute(stmt)
        alerts = result.scalars().all()

        count = 0
        for alert in alerts:
            alert.is_read = True
            count += 1

        await db.commit()

        return count


# Global alert service instance
alert_service = AlertService()
