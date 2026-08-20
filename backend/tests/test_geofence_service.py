"""Unit tests for GeofenceService."""
import pytest
from fastapi import HTTPException

from app.core.security import hash_password
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleType
from app.models.geofence import Geofence, GeofenceType
from app.schemas.geofence import GeofenceCreate
from app.services.geofence_service import GeofenceService, geofence_service


async def _make_user(db_session, email="owner@example.com") -> User:
    user = User(email=email, hashed_password=hash_password("password123"), full_name="Owner")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def _make_vehicle(db_session, user: User) -> Vehicle:
    vehicle = Vehicle(user_id=user.id, name="Van", plate_number=f"P-{user.id}", type=VehicleType.VAN)
    db_session.add(vehicle)
    await db_session.commit()
    await db_session.refresh(vehicle)
    return vehicle


def test_is_point_in_geofence_circle_inside_and_outside():
    geofence = Geofence(type=GeofenceType.CIRCLE, center_lat=9.0, center_lng=38.76, radius_meters=200)
    assert GeofenceService.is_point_in_geofence(9.0001, 38.7601, geofence) is True
    assert GeofenceService.is_point_in_geofence(9.5, 39.0, geofence) is False


def test_is_point_in_geofence_polygon():
    square = [(9.0, 38.0), (9.0, 38.01), (9.01, 38.01), (9.01, 38.0)]
    geofence = Geofence(type=GeofenceType.POLYGON, coordinates=square)
    assert GeofenceService.is_point_in_geofence(9.005, 38.005, geofence) is True
    assert GeofenceService.is_point_in_geofence(9.5, 38.5, geofence) is False


@pytest.mark.asyncio
async def test_create_and_get_geofence(db_session):
    user = await _make_user(db_session)
    created = await geofence_service.create_geofence(
        user_id=user.id,
        geofence_data=GeofenceCreate(name="Depot", type=GeofenceType.CIRCLE, center_lat=9.0, center_lng=38.7, radius_meters=100),
        db=db_session,
    )

    fetched = await GeofenceService.get_geofence(created.id, user.id, db_session)
    assert fetched.id == created.id
    assert fetched.name == "Depot"


@pytest.mark.asyncio
async def test_get_geofence_rejects_other_users(db_session):
    owner = await _make_user(db_session, "owner2@example.com")
    intruder = await _make_user(db_session, "intruder@example.com")

    created = await geofence_service.create_geofence(
        user_id=owner.id,
        geofence_data=GeofenceCreate(name="Private", type=GeofenceType.CIRCLE, center_lat=9.0, center_lng=38.7, radius_meters=100),
        db=db_session,
    )

    with pytest.raises(HTTPException) as exc_info:
        await GeofenceService.get_geofence(created.id, intruder.id, db_session)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_assign_and_list_vehicles(db_session):
    user = await _make_user(db_session, "fleet-owner@example.com")
    vehicle = await _make_vehicle(db_session, user)
    geofence = await geofence_service.create_geofence(
        user_id=user.id,
        geofence_data=GeofenceCreate(name="Yard", type=GeofenceType.CIRCLE, center_lat=9.0, center_lng=38.7, radius_meters=100),
        db=db_session,
    )

    await geofence_service.assign_vehicle_to_geofence(
        geofence_id=geofence.id, vehicle_id=vehicle.id, user_id=user.id, db=db_session,
    )

    assignments = await geofence_service.list_assigned_vehicles(geofence.id, user.id, db_session)
    assert len(assignments) == 1
    assert assignments[0].vehicle_id == vehicle.id

    await geofence_service.unassign_vehicle_from_geofence(geofence.id, vehicle.id, user.id, db_session)
    assignments_after = await geofence_service.list_assigned_vehicles(geofence.id, user.id, db_session)
    assert len(assignments_after) == 0
