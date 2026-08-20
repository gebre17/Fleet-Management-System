"""Unit tests for ReportService."""
from datetime import datetime, timedelta, timezone

import pytest

from app.core.security import hash_password
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleType
from app.models.location import Location
from app.services.report_service import report_service


async def _make_user(db_session) -> User:
    user = User(email="reporter@example.com", hashed_password=hash_password("password123"), full_name="Reporter")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def _make_vehicle(db_session, user: User) -> Vehicle:
    vehicle = Vehicle(user_id=user.id, name="Truck", plate_number="RPT-1", type=VehicleType.TRUCK)
    db_session.add(vehicle)
    await db_session.commit()
    await db_session.refresh(vehicle)
    return vehicle


async def _add_location(db_session, vehicle, lat, lng, speed, minutes_ago):
    loc = Location(
        vehicle_id=vehicle.id,
        latitude=lat,
        longitude=lng,
        speed=speed,
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=minutes_ago),
    )
    db_session.add(loc)
    await db_session.commit()
    return loc


@pytest.mark.asyncio
async def test_distance_report_sums_segments(db_session):
    user = await _make_user(db_session)
    vehicle = await _make_vehicle(db_session, user)

    # Two points ~500m apart along a meridian.
    await _add_location(db_session, vehicle, 9.0000, 38.7600, speed=40, minutes_ago=10)
    await _add_location(db_session, vehicle, 9.0045, 38.7600, speed=40, minutes_ago=5)

    report = await report_service.get_distance_report(user_id=user.id, db=db_session)
    assert len(report) == 1
    assert report[0]["vehicle_id"] == str(vehicle.id)
    assert report[0]["segments"] == 1
    assert 0.4 < report[0]["total_km"] < 0.6


@pytest.mark.asyncio
async def test_speed_report_computes_avg_and_max(db_session):
    user = await _make_user(db_session)
    vehicle = await _make_vehicle(db_session, user)

    await _add_location(db_session, vehicle, 9.0, 38.7, speed=40, minutes_ago=10)
    await _add_location(db_session, vehicle, 9.0, 38.7, speed=80, minutes_ago=5)

    report = await report_service.get_speed_report(user_id=user.id, db=db_session)
    assert len(report) == 1
    assert report[0]["avg_speed_kmh"] == 60.0
    assert report[0]["max_speed_kmh"] == 80.0
    assert report[0]["measurements"] == 2


@pytest.mark.asyncio
async def test_reports_are_empty_for_vehicles_with_no_locations(db_session):
    user = await _make_user(db_session)
    await _make_vehicle(db_session, user)

    distance = await report_service.get_distance_report(user_id=user.id, db=db_session)
    speed = await report_service.get_speed_report(user_id=user.id, db=db_session)
    activity = await report_service.get_activity_report(user_id=user.id, db=db_session)

    assert distance == []
    assert speed == []
    assert activity == []
