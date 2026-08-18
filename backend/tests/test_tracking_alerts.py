"""Integration tests for the location-ingest -> alert-engine pipeline.

This exercises the full previously-broken path: POST a location ->
tracking_service.ingest_location -> alert_engine geofence/speed/battery
checks -> alert_service.create_alert -> GET /alerts. It also verifies
alerts and reports are scoped per-user (regression test for the
ownership/IDOR fix).
"""
import pytest

GEOFENCE_CENTER = {"lat": 9.0000, "lng": 38.7600}
POINT_INSIDE = {"lat": 9.0001, "lng": 38.7601}  # ~15m from center
POINT_OUTSIDE = {"lat": 9.0500, "lng": 38.8000}  # several km away


async def _create_vehicle(client, headers):
    response = await client.post(
        "/api/v1/vehicles/",
        headers=headers,
        json={
            "name": "Delivery Van 1",
            "plate_number": "AA-1234",
            "type": "van",
            "device_id": "device-test-001",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def _create_geofence(client, headers):
    response = await client.post(
        "/api/v1/geofences/",
        headers=headers,
        json={
            "name": "Depot",
            "type": "circle",
            "center_lat": GEOFENCE_CENTER["lat"],
            "center_lng": GEOFENCE_CENTER["lng"],
            "radius_meters": 200,
            "color": "#3B82F6",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def _post_location(client, headers, vehicle_id, **overrides):
    payload = {"latitude": POINT_OUTSIDE["lat"], "longitude": POINT_OUTSIDE["lng"], "speed": 40}
    payload.update(overrides)
    response = await client.post(
        f"/api/v1/tracking/{vehicle_id}/location", headers=headers, json=payload
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _alert_count(client, headers, alert_type):
    response = await client.get(
        "/api/v1/alerts/", headers=headers, params={"alert_type": alert_type, "limit": 100}
    )
    assert response.status_code == 200
    return response.json()["total"]


@pytest.mark.asyncio
async def test_geofence_enter_and_exit_alerts(client, auth_headers):
    vehicle_id = await _create_vehicle(client, auth_headers)
    geofence_id = await _create_geofence(client, auth_headers)

    await client.post(
        f"/api/v1/geofences/{geofence_id}/vehicles",
        headers=auth_headers,
        json={"vehicle_id": vehicle_id, "alert_on_enter": True, "alert_on_exit": True},
    )

    # First fix is outside the geofence -> no transition, no alert.
    await _post_location(
        client, auth_headers, vehicle_id, latitude=POINT_OUTSIDE["lat"], longitude=POINT_OUTSIDE["lng"]
    )
    assert await _alert_count(client, auth_headers, "geofence_enter") == 0

    # Moves inside -> geofence_enter.
    await _post_location(
        client, auth_headers, vehicle_id, latitude=POINT_INSIDE["lat"], longitude=POINT_INSIDE["lng"]
    )
    assert await _alert_count(client, auth_headers, "geofence_enter") == 1

    # Moves back outside -> geofence_exit.
    await _post_location(
        client, auth_headers, vehicle_id, latitude=POINT_OUTSIDE["lat"], longitude=POINT_OUTSIDE["lng"]
    )
    assert await _alert_count(client, auth_headers, "geofence_exit") == 1


@pytest.mark.asyncio
async def test_speeding_alert_is_edge_triggered(client, auth_headers):
    vehicle_id = await _create_vehicle(client, auth_headers)

    await _post_location(client, auth_headers, vehicle_id, speed=40)
    assert await _alert_count(client, auth_headers, "speeding") == 0

    await _post_location(client, auth_headers, vehicle_id, speed=150)
    assert await _alert_count(client, auth_headers, "speeding") == 1

    # Still speeding on the next ping -> no duplicate alert.
    await _post_location(client, auth_headers, vehicle_id, speed=155)
    assert await _alert_count(client, auth_headers, "speeding") == 1


@pytest.mark.asyncio
async def test_low_battery_alert_is_edge_triggered(client, auth_headers):
    vehicle_id = await _create_vehicle(client, auth_headers)

    await _post_location(client, auth_headers, vehicle_id, battery_level=80)
    assert await _alert_count(client, auth_headers, "low_battery") == 0

    await _post_location(client, auth_headers, vehicle_id, battery_level=10)
    assert await _alert_count(client, auth_headers, "low_battery") == 1

    # Still low -> no duplicate.
    await _post_location(client, auth_headers, vehicle_id, battery_level=8)
    assert await _alert_count(client, auth_headers, "low_battery") == 1


@pytest.mark.asyncio
async def test_alerts_and_reports_are_scoped_per_user(client, auth_headers):
    vehicle_id = await _create_vehicle(client, auth_headers)
    await _post_location(client, auth_headers, vehicle_id, speed=150)  # triggers a speeding alert

    other_register = await client.post(
        "/api/v1/auth/register",
        json={"email": "other-user@example.com", "password": "password123", "full_name": "Other User"},
    )
    other_headers = {"Authorization": f"Bearer {other_register.json()['access_token']}"}

    own_alerts = await client.get("/api/v1/alerts/", headers=auth_headers)
    other_alerts = await client.get("/api/v1/alerts/", headers=other_headers)
    assert own_alerts.json()["total"] >= 1
    assert other_alerts.json()["total"] == 0

    own_report = await client.get("/api/v1/reports/distance", headers=auth_headers)
    other_report = await client.get("/api/v1/reports/distance", headers=other_headers)
    assert other_report.json() == []
    assert own_report.status_code == 200
