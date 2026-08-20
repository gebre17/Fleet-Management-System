"""MQTT event handlers."""

import logging
from typing import Any

from pydantic import ValidationError

from app.core.database import async_session_maker
from app.schemas.location import LocationCreate
from app.services.tracking_service import tracking_service
from app.services.vehicle_service import VehicleService

logger = logging.getLogger(__name__)


async def handle_device_location(data: dict[str, Any]) -> None:
    """
    Handle a location payload published by a GPS device over MQTT.

    Expected payload (see tracker-simulator/simulator.py):
        {"device_id": str, "lat": float, "lng": float,
         "speed": float, "heading": float, "battery": int}

    Args:
        data: Decoded MQTT JSON payload
    """
    device_id = data.get("device_id")
    if not device_id:
        logger.warning("Dropping MQTT location payload without device_id")
        return

    try:
        location_data = LocationCreate(
            latitude=data["lat"],
            longitude=data["lng"],
            speed=data.get("speed"),
            heading=data.get("heading"),
            accuracy=data.get("accuracy"),
            altitude=data.get("altitude"),
            battery_level=data.get("battery"),
        )
    except (KeyError, ValidationError) as e:
        logger.error(f"Invalid location payload from device {device_id}: {e}")
        return

    async with async_session_maker() as session:
        vehicle = await VehicleService.get_vehicle_by_device_id(device_id, session)
        if not vehicle:
            logger.warning(f"Received location for unknown device_id: {device_id}")
            return

        await tracking_service.ingest_location(
            vehicle_id=vehicle.id,
            location_data=location_data,
            db=session,
        )
        logger.info(f"Ingested MQTT location for vehicle {vehicle.id} (device {device_id})")
