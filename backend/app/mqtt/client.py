"""MQTT client for IoT device communication."""
from typing import Callable, Optional
import json
import logging
import paho.mqtt.client as mqtt
from app.core.config import settings

logger = logging.getLogger(__name__)


class MQTTClient:
    """MQTT client for receiving GPS data from IoT devices."""
    
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.is_connected: bool = False
        self.on_location_received: Optional[Callable] = None
    
    def connect(self) -> None:
        """Connect to MQTT broker."""
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        try:
            self.client.connect(settings.MQTT_HOST, settings.MQTT_PORT, keepalive=60)
            self.client.loop_start()
            logger.info(f"MQTT client connecting to {settings.MQTT_HOST}:{settings.MQTT_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise
    
    def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT client disconnected")
    
    def _on_connect(self, client: mqtt.Client, userdata, flags, rc) -> None:
        """Callback when MQTT client connects."""
        if rc == 0:
            self.is_connected = True
            logger.info("MQTT client connected successfully")
            # Subscribe to location topic
            client.subscribe("trackfleet/devices/+/location")
        else:
            logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_message(self, client: mqtt.Client, userdata, msg) -> None:
        """Callback when MQTT message is received."""
        try:
            payload = json.loads(msg.payload.decode())
            
            if self.on_location_received:
                # Run callback without blocking
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                if loop.is_running():
                    asyncio.create_task(self.on_location_received(payload))
                else:
                    loop.run_until_complete(self.on_location_received(payload))
        
        except json.JSONDecodeError:
            logger.error(f"Failed to decode MQTT message: {msg.payload}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def _on_disconnect(self, client: mqtt.Client, userdata, rc) -> None:
        """Callback when MQTT client disconnects."""
        self.is_connected = False
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnection with code {rc}")
        else:
            logger.info("MQTT client disconnected")
    
    def set_location_callback(self, callback: Callable) -> None:
        """
        Set callback for when location data is received.
        
        Args:
            callback: Async function to call with location data
        """
        self.on_location_received = callback


# Global MQTT client instance
mqtt_client = MQTTClient()
