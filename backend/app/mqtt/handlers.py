"""MQTT event handlers."""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def handle_device_location(data: Dict[str, Any]) -> None:
    """
    Handle location data from IoT device.
    
    Args:
        data: Location payload with device_id, lat, lng, speed, heading, battery
    """
    # This will be called by the tracking service
    logger.info(f"Received location from device: {data.get('device_id')}")
