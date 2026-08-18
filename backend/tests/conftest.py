"""Test fixtures.

Tests run against an in-memory SQLite database (via the cross-dialect
GUID/JSON column types in app.models.types) and drive the API through
httpx directly against the ASGI app — no Docker, Postgres, Redis, or
MQTT broker required. FastAPI's startup/shutdown events are intentionally
not triggered, so nothing here touches Redis or MQTT.
"""
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db_session
from app.main import app


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    async def _override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = _override_get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(client):
    """Register a user and return an Authorization header for them."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "driver@example.com",
            "password": "supersecret123",
            "full_name": "Test Driver",
        },
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
