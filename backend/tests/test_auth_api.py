"""Integration tests for the authentication API."""
import pytest


@pytest.mark.asyncio
async def test_register_returns_tokens(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "password123", "full_name": "New User"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email_rejected(client):
    payload = {"email": "dupe@example.com", "password": "password123", "full_name": "Dupe"}
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 200

    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 400


@pytest.mark.asyncio
async def test_login_with_correct_credentials(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "password123", "full_name": "Login User"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


@pytest.mark.asyncio
async def test_login_with_wrong_password_rejected(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login2@example.com", "password": "password123", "full_name": "Login User 2"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login2@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_current_user(client, auth_headers):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "driver@example.com"


@pytest.mark.asyncio
async def test_refresh_issues_new_tokens(client):
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": "refresh@example.com", "password": "password123", "full_name": "Refresh User"},
    )
    refresh_token = register.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


@pytest.mark.asyncio
async def test_refresh_rejects_access_token(client):
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": "refresh2@example.com", "password": "password123", "full_name": "Refresh User 2"},
    )
    access_token = register.json()["access_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token},
    )
    assert response.status_code == 401
