"""Unit tests for geographic utilities (geofence math)."""
from app.utils.geo import haversine_distance, point_in_circle, point_in_polygon

# A small square around Addis Ababa's Meskel Square area, used across tests.
SQUARE = [
    (9.010, 38.760),
    (9.010, 38.765),
    (9.005, 38.765),
    (9.005, 38.760),
]


def test_haversine_distance_same_point_is_zero():
    assert haversine_distance(9.005, 38.763, 9.005, 38.763) == 0


def test_haversine_distance_known_short_hop():
    # Roughly 500m apart along a meridian (~0.0045 deg lat).
    distance = haversine_distance(9.0000, 38.7600, 9.0045, 38.7600)
    assert 450 < distance < 550


def test_point_in_circle_inside():
    assert point_in_circle(9.0001, 38.7601, 9.0000, 38.7600, radius_m=500) is True


def test_point_in_circle_outside():
    assert point_in_circle(9.5000, 39.0000, 9.0000, 38.7600, radius_m=500) is False


def test_point_in_circle_boundary_is_inclusive():
    assert point_in_circle(9.0000, 38.7600, 9.0000, 38.7600, radius_m=0) is True


def test_point_in_polygon_inside():
    assert point_in_polygon(9.007, 38.762, SQUARE) is True


def test_point_in_polygon_outside():
    assert point_in_polygon(9.100, 38.900, SQUARE) is False


def test_point_in_polygon_degenerate_returns_false():
    assert point_in_polygon(9.007, 38.762, [(9.0, 38.0), (9.1, 38.1)]) is False
