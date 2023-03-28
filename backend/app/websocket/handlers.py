"""WebSocket event handlers."""
from app.websocket.manager import manager


async def on_location_update(vehicle_id: str, data: dict) -> None:
    """
    Handle location update event.
    
    Args:
        vehicle_id: Vehicle ID
        data: Location data
    """
    await manager.broadcast_to_room(vehicle_id, data)


async def on_alert(vehicle_id: str, alert_data: dict) -> None:
    """
    Handle alert event.
    
    Args:
        vehicle_id: Vehicle ID
        alert_data: Alert data
    """
    await manager.broadcast_all({
        "type": "alert",
        "vehicle_id": vehicle_id,
        "data": alert_data
    })
