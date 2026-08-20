"""MQTT client for IoT device communication."""

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable

import paho.mqtt.client as mqtt

from app.core.config import settings

logger = logging.getLogger(__name__)

LOCATION_TOPIC_FILTER = "trackfleet/devices/+/location"


class MQTTClient:
    """MQTT client for receiving GPS data from IoT devices.

    paho-mqtt runs its network loop on its own background thread
    (``loop_start()``), so callbacks like ``_on_message`` never execute on
    the asyncio event loop uvicorn is running on. To safely hand a message
    off to async code (e.g. a DB session), we capture the running loop when
    ``connect()`` is called from inside the app's startup coroutine and use
    ``run_coroutine_threadsafe`` to schedule work on it from the MQTT thread.
    """

    def __init__(self):
        self.client: mqtt.Client | None = None
        self.is_connected: bool = False
        self.on_location_received: Callable[[dict], Awaitable[None]] | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def connect(self) -> None:
        """Connect to MQTT broker."""
        self._loop = asyncio.get_event_loop()

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        if settings.MQTT_USERNAME:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

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
            client.subscribe(LOCATION_TOPIC_FILTER)
        else:
            logger.error(f"MQTT connection failed with code {rc}")

    def _on_message(self, client: mqtt.Client, userdata, msg) -> None:
        """Callback when MQTT message is received (runs on paho's thread)."""
        try:
            payload = json.loads(msg.payload.decode())
        except json.JSONDecodeError:
            logger.error(f"Failed to decode MQTT message: {msg.payload!r}")
            return

        if not self.on_location_received or not self._loop:
            return

        future = asyncio.run_coroutine_threadsafe(self.on_location_received(payload), self._loop)
        future.add_done_callback(self._log_callback_error)

    @staticmethod
    def _log_callback_error(future: "asyncio.Future") -> None:
        try:
            future.result()
        except Exception:
            logger.exception("Error handling MQTT location payload")

    def _on_disconnect(self, client: mqtt.Client, userdata, rc) -> None:
        """Callback when MQTT client disconnects."""
        self.is_connected = False
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnection with code {rc}")
        else:
            logger.info("MQTT client disconnected")

    def set_location_callback(self, callback: Callable[[dict], Awaitable[None]]) -> None:
        """
        Set callback for when location data is received.

        Args:
            callback: Async function to call with the decoded location payload
        """
        self.on_location_received = callback


# Global MQTT client instance
mqtt_client = MQTTClient()
