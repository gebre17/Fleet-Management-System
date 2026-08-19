"""Application startup and shutdown events."""
import asyncio
import logging
from app.core.database import close_db
from app.services.tracking_service import tracking_service
from app.services.geofence_service import geofence_service
from app.services.offline_monitor import run_offline_monitor
from app.mqtt.client import mqtt_client
from app.mqtt.handlers import handle_device_location

logger = logging.getLogger(__name__)

_offline_monitor_task: asyncio.Task | None = None


async def startup_handler() -> None:
    """Handle application startup."""
    logger.info("Starting TrackFleet API...")

    # Initialize services
    await tracking_service.init()
    await geofence_service.init()
    logger.info("Services initialized")

    # Wire the MQTT ingestion pipeline before connecting, so no message is
    # ever dropped due to a missing callback.
    mqtt_client.set_location_callback(handle_device_location)
    try:
        mqtt_client.connect()
        logger.info("MQTT client connected")
    except Exception as e:
        logger.error(f"Failed to connect MQTT client: {e}")

    global _offline_monitor_task
    _offline_monitor_task = asyncio.create_task(run_offline_monitor())

    logger.info("TrackFleet API started successfully")


async def shutdown_handler() -> None:
    """Handle application shutdown."""
    logger.info("Shutting down TrackFleet API...")

    if _offline_monitor_task:
        _offline_monitor_task.cancel()
        try:
            await _offline_monitor_task
        except asyncio.CancelledError:
            pass

    mqtt_client.disconnect()
    logger.info("MQTT client disconnected")

    await tracking_service.close()
    await geofence_service.close()
    logger.info("Services closed")

    await close_db()
    logger.info("Database closed")

    logger.info("TrackFleet API shutdown complete")
