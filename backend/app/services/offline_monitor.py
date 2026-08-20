"""Background task that flags vehicles as offline when they stop reporting
GPS locations, and raises an OFFLINE alert exactly once per transition.
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session_maker
from app.models.alert import AlertSeverity, AlertType
from app.models.location import Location
from app.models.vehicle import Vehicle, VehicleStatus
from app.services.alert_service import alert_service

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 60


async def _check_offline_vehicles() -> None:
    cutoff = datetime.now(UTC) - timedelta(minutes=settings.OFFLINE_ALERT_THRESHOLD_MINUTES)

    async with async_session_maker() as db:
        stmt = select(Vehicle).where(Vehicle.status != VehicleStatus.OFFLINE)
        result = await db.execute(stmt)
        vehicles = result.scalars().all()

        for vehicle in vehicles:
            latest_stmt = (
                select(Location)
                .where(Location.vehicle_id == vehicle.id)
                .order_by(Location.timestamp.desc())
                .limit(1)
            )
            latest_result = await db.execute(latest_stmt)
            latest_location = latest_result.scalar_one_or_none()

            if not latest_location or latest_location.timestamp >= cutoff:
                continue

            vehicle.status = VehicleStatus.OFFLINE
            await db.commit()

            await alert_service.create_alert(
                vehicle_id=vehicle.id,
                alert_type=AlertType.OFFLINE,
                severity=AlertSeverity.WARNING,
                message=(
                    f"{vehicle.name} has not reported a location in "
                    f"{settings.OFFLINE_ALERT_THRESHOLD_MINUTES} minutes"
                ),
                db=db,
                metadata={"last_seen": latest_location.timestamp.isoformat()},
                owner_id=vehicle.user_id,
            )
            logger.info(f"Vehicle {vehicle.id} marked offline")


async def run_offline_monitor() -> None:
    """Run the offline-check loop until cancelled."""
    while True:
        try:
            await _check_offline_vehicles()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Offline monitor check failed")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
