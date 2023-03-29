"""Geographic utility functions."""
import math
from typing import List, Tuple


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance in metres between two GPS coordinates.
    
    Args:
        lat1: First latitude
        lon1: First longitude
        lat2: Second latitude
        lon2: Second longitude
    
    Returns:
        Distance in meters
    """
    R = 6371000  # Earth's radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def point_in_circle(
    lat: float, lng: float, center_lat: float, center_lng: float, radius_m: float
) -> bool:
    """
    Check if a point is within a circle.
    
    Args:
        lat: Point latitude
        lng: Point longitude
        center_lat: Circle center latitude
        center_lng: Circle center longitude
        radius_m: Circle radius in meters
    
    Returns:
        True if point is inside circle, False otherwise
    """
    distance = haversine_distance(lat, lng, center_lat, center_lng)
    return distance <= radius_m


def point_in_polygon(lat: float, lng: float, polygon: List[Tuple[float, float]]) -> bool:
    """
    Check if a point is within a polygon using ray-casting algorithm.
    
    Args:
        lat: Point latitude
        lng: Point longitude
        polygon: List of (lat, lng) tuples defining polygon vertices
    
    Returns:
        True if point is inside polygon, False otherwise
    """
    n = len(polygon)
    if n < 3:
        return False
    
    inside = False
    j = n - 1
    
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        
        if ((yi > lng) != (yj > lng)) and (lat < (xj - xi) * (lng - yi) / (yj - yi) + xi):
            inside = not inside
        
        j = i
    
    return inside
