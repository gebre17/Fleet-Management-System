"""Application startup and shutdown events."""
import logging
from app.core.database import init_db, close_db
from app.services.tracking_service import tracking_service
from app.services.geofence_service import geofence_service
from app.services.alert_service import alert_service
from app.services.report_service import report_service
from app.mqtt.client import mqtt_client

logger = logging.getLogger(__name__)


async def startup_handler() -> None:
    """Handle application startup."""
    logger.info("Starting TrackFleet API...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize services
    await tracking_service.init()
    await geofence_service.init()
    logger.info("Services initialized")
    
    # Connect MQTT client
    try:
        mqtt_client.connect()
        logger.info("MQTT client connected")
    except Exception as e:
        logger.error(f"Failed to connect MQTT client: {e}")
    
    logger.info("TrackFleet API started successfully")


async def shutdown_handler() -> None:
    """Handle application shutdown."""
    logger.info("Shutting down TrackFleet API...")
    
    # Close MQTT client
    mqtt_client.disconnect()
    logger.info("MQTT client disconnected")
    
    # Close services
    await tracking_service.close()
    await geofence_service.close()
    logger.info("Services closed")
    
    # Close database
    await close_db()
    logger.info("Database closed")
    
    logger.info("TrackFleet API shutdown complete")
