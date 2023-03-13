"""Database models"""
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.location import Location
from app.models.geofence import Geofence, GeofenceVehicle
from app.models.alert import Alert

__all__ = [
    "User",
    "Vehicle",
    "Location",
    "Geofence",
    "GeofenceVehicle",
    "Alert",
]
