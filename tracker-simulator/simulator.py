/**
 * GPS Tracker Simulator
 */
import json
import asyncio
import argparse
import logging
from datetime import datetime, timedelta
import math
import random
from typing import List, Tuple

import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GPSSimulator:
    """Simulates GPS devices sending location data via MQTT."""

    def __init__(
        self,
        mqtt_host: str = "localhost",
        mqtt_port: int = 1883,
        num_vehicles: int = 5,
        interval_seconds: float = 5,
    ):
        """
        Initialize the GPS simulator.

        Args:
            mqtt_host: MQTT broker host
            mqtt_port: MQTT broker port
            num_vehicles: Number of vehicles to simulate
            interval_seconds: Interval between location updates
        """
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.num_vehicles = num_vehicles
        self.interval_seconds = interval_seconds
        self.client = None
        self.is_running = False

        # Sample routes (lat, lng)
        self.routes = {
            "city_loop": [
                (40.7128, -74.0060),  # NYC
                (40.7139, -74.0064),
                (40.7150, -74.0065),
                (40.7160, -74.0055),
                (40.7128, -74.0060),
            ],
            "highway": [
                (40.7580, -73.9855),
                (40.7614, -73.9776),
                (40.7489, -73.9680),
                (40.7128, -74.0060),
                (40.7580, -73.9855),
            ],
            "suburban": [
                (40.6882, -73.7949),
                (40.6892, -73.7850),
                (40.6750, -73.7890),
                (40.6882, -73.7949),
            ],
        }

    def connect(self) -> None:
        """Connect to MQTT broker."""
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        try:
            self.client.connect(self.mqtt_host, self.mqtt_port, keepalive=60)
            self.client.loop_start()
            logger.info(f"Connected to MQTT broker at {self.mqtt_host}:{self.mqtt_port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    def _on_connect(self, client, userdata, flags, rc) -> None:
        """Callback when connected to MQTT broker."""
        if rc == 0:
            logger.info("MQTT client connected")
            self.is_running = True
        else:
            logger.error(f"MQTT connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc) -> None:
        """Callback when disconnected from MQTT broker."""
        self.is_running = False
        logger.info(f"MQTT client disconnected with code {rc}")

    def calculate_heading(
        self, lat1: float, lng1: float, lat2: float, lng2: float
    ) -> float:
        """Calculate bearing from one point to another."""
        dLon = lng2 - lng1
        y = math.sin(dLon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
        bearing = math.atan2(y, x)
        return (bearing * 180) / math.pi + 360

    def calculate_distance(
        self, lat1: float, lng1: float, lat2: float, lng2: float
    ) -> float:
        """Calculate distance between two points in kilometers."""
        R = 6371  # Earth's radius in km
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lng2 - lng1)
        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def simulate_vehicle(
        self, vehicle_id: str, device_id: str, route: List[Tuple[float, float]]
    ) -> None:
        """Simulate a single vehicle's movement."""
        if not route or len(route) < 2:
            logger.warning(f"Invalid route for vehicle {vehicle_id}")
            return

        waypoint_idx = 0
        while self.is_running:
            current = route[waypoint_idx % len(route)]
            next_waypoint = route[(waypoint_idx + 1) % len(route)]

            # Calculate heading and distance
            heading = self.calculate_heading(
                current[0], current[1], next_waypoint[0], next_waypoint[1]
            )
            distance = self.calculate_distance(
                current[0], current[1], next_waypoint[0], next_waypoint[1]
            )

            # Simulate speed between 20-80 km/h
            speed = random.uniform(20, 80)

            # Create location payload
            payload = {
                "device_id": device_id,
                "lat": current[0] + random.gauss(0, 0.0001),
                "lng": current[1] + random.gauss(0, 0.0001),
                "speed": speed,
                "heading": heading,
                "battery": random.randint(70, 100),
            }

            # Publish to MQTT
            topic = f"trackfleet/devices/{device_id}/location"
            self.client.publish(topic, json.dumps(payload))
            logger.info(f"Published location for {device_id}: {payload}")

            # Move to next waypoint
            waypoint_idx += 1
            asyncio.run(asyncio.sleep(self.interval_seconds))

    def run(self) -> None:
        """Run the simulator."""
        self.connect()

        route_keys = list(self.routes.keys())

        # Create and start vehicle threads
        import threading

        threads = []
        for i in range(self.num_vehicles):
            vehicle_id = f"vehicle_{i+1:03d}"
            device_id = f"device_{i+1:03d}"
            route_key = route_keys[i % len(route_keys)]
            route = self.routes[route_key]

            thread = threading.Thread(
                target=self.simulate_vehicle,
                args=(vehicle_id, device_id, route),
                daemon=True,
            )
            threads.append(thread)
            thread.start()

        logger.info(f"Simulator started with {self.num_vehicles} vehicles")

        try:
            # Keep running
            while True:
                asyncio.run(asyncio.sleep(1))
        except KeyboardInterrupt:
            logger.info("Shutting down simulator...")
            self.is_running = False
            self.client.loop_stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GPS Tracker Simulator")
    parser.add_argument("--host", default="localhost", help="MQTT broker host")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--vehicles", type=int, default=5, help="Number of vehicles to simulate")
    parser.add_argument("--interval", type=float, default=5, help="Update interval in seconds")

    args = parser.parse_args()

    simulator = GPSSimulator(
        mqtt_host=args.host,
        mqtt_port=args.port,
        num_vehicles=args.vehicles,
        interval_seconds=args.interval,
    )
    simulator.run()
