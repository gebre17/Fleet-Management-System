"""Alert engine: evaluates a newly-ingested location against a vehicle's
geofences and thresholds, and raises alerts on state *transitions*.

Every check here is edge-triggered (compares the previous location's state
to the new one) rather than level-triggered, so a vehicle sitting still
inside a geofence, over the speed limit, or with a low battery only
generates one alert per transition instead of one per GPS ping.
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.alert import AlertSeverity, AlertType
from app.models.geofence import Geofence, GeofenceVehicle
from app.models.location import Location
from app.models.vehicle import Vehicle
from app.services.alert_service import alert_service
from app.services.geofence_service import GeofenceService

logger = logging.getLogger(__name__)


async def evaluate_location(
    vehicle: Vehicle,
    previous: Location | None,
    current: Location,
    db: AsyncSession,
) -> None:
    """Run geofence, speeding, and low-battery checks for a new location."""
    await _evaluate_geofences(vehicle, previous, current, db)
    await _evaluate_speeding(vehicle, previous, current, db)
    await _evaluate_battery(vehicle, previous, current, db)


async def _evaluate_geofences(
    vehicle: Vehicle,
    previous: Location | None,
    current: Location,
    db: AsyncSession,
) -> None:
    stmt = (
        select(GeofenceVehicle, Geofence)
        .join(Geofence, Geofence.id == GeofenceVehicle.geofence_id)
        .where(GeofenceVehicle.vehicle_id == vehicle.id, Geofence.is_active.is_(True))
    )
    result = await db.execute(stmt)

    for assignment, geofence in result.all():
        was_inside = bool(previous) and GeofenceService.is_point_in_geofence(
            previous.latitude, previous.longitude, geofence
        )
        is_inside = GeofenceService.is_point_in_geofence(current.latitude, current.longitude, geofence)

        if is_inside and not was_inside and assignment.alert_on_enter:
            await alert_service.create_alert(
                vehicle_id=vehicle.id,
                alert_type=AlertType.GEOFENCE_ENTER,
                severity=AlertSeverity.INFO,
                message=f"{vehicle.name} entered geofence '{geofence.name}'",
                db=db,
                geofence_id=geofence.id,
                metadata={"latitude": current.latitude, "longitude": current.longitude},
                owner_id=vehicle.user_id,
            )
        elif was_inside and not is_inside and assignment.alert_on_exit:
            await alert_service.create_alert(
                vehicle_id=vehicle.id,
                alert_type=AlertType.GEOFENCE_EXIT,
                severity=AlertSeverity.INFO,
                message=f"{vehicle.name} exited geofence '{geofence.name}'",
                db=db,
                geofence_id=geofence.id,
                metadata={"latitude": current.latitude, "longitude": current.longitude},
                owner_id=vehicle.user_id,
            )


async def _evaluate_speeding(
    vehicle: Vehicle,
    previous: Location | None,
    current: Location,
    db: AsyncSession,
) -> bool:
    threshold = settings.SPEED_ALERT_THRESHOLD_KMH
    current_speed = current.speed or 0
    previous_speed = (previous.speed if previous else 0) or 0

    if current_speed > threshold and previous_speed <= threshold:
        await alert_service.create_alert(
            vehicle_id=vehicle.id,
            alert_type=AlertType.SPEEDING,
            severity=AlertSeverity.WARNING,
            message=f"{vehicle.name} is speeding at {current_speed:.0f} km/h (limit {threshold:.0f} km/h)",
            db=db,
            metadata={"speed": current_speed, "threshold": threshold},
            owner_id=vehicle.user_id,
        )
        return True
    return False


async def _evaluate_battery(
    vehicle: Vehicle,
    previous: Location | None,
    current: Location,
    db: AsyncSession,
) -> None:
    threshold = settings.LOW_BATTERY_THRESHOLD_PERCENT
    if current.battery_level is None:
        return

    previous_level = previous.battery_level if previous else None
    was_low = previous_level is not None and previous_level <= threshold

    if current.battery_level <= threshold and not was_low:
        severity = AlertSeverity.CRITICAL if current.battery_level <= threshold / 2 else AlertSeverity.WARNING
        await alert_service.create_alert(
            vehicle_id=vehicle.id,
            alert_type=AlertType.LOW_BATTERY,
            severity=severity,
            message=f"{vehicle.name} device battery is low ({current.battery_level}%)",
            db=db,
            metadata={"battery_level": current.battery_level, "threshold": threshold},
            owner_id=vehicle.user_id,
        )
