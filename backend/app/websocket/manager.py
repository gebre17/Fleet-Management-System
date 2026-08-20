"""WebSocket connection manager."""

from fastapi import WebSocket


class ConnectionManager:
    """Manage WebSocket connections for real-time vehicle tracking."""

    def __init__(self):
        # vehicle_id -> set of connected WebSocket connections
        self.active_connections: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, vehicle_id: str) -> None:
        """
        Connect a new WebSocket client to a vehicle.

        Args:
            websocket: WebSocket connection
            vehicle_id: Vehicle ID to subscribe to
        """
        await websocket.accept()

        if vehicle_id not in self.active_connections:
            self.active_connections[vehicle_id] = set()

        self.active_connections[vehicle_id].add(websocket)

    def disconnect(self, websocket: WebSocket, vehicle_id: str) -> None:
        """
        Disconnect a WebSocket client.

        Args:
            websocket: WebSocket connection
            vehicle_id: Vehicle ID
        """
        if vehicle_id in self.active_connections:
            self.active_connections[vehicle_id].discard(websocket)

            if not self.active_connections[vehicle_id]:
                del self.active_connections[vehicle_id]

    async def broadcast_to_room(self, vehicle_id: str, data: dict) -> None:
        """
        Broadcast message to all clients subscribed to a vehicle.

        Args:
            vehicle_id: Vehicle ID
            data: Data to broadcast
        """
        if vehicle_id in self.active_connections:
            disconnected = set()

            for connection in self.active_connections[vehicle_id]:
                try:
                    await connection.send_json(data)
                except Exception:
                    disconnected.add(connection)

            for connection in disconnected:
                self.active_connections[vehicle_id].discard(connection)


# Global connection manager instance
manager = ConnectionManager()
