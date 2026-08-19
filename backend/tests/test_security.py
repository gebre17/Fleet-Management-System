"""Unit tests for password hashing and JWT handling."""
from datetime import timedelta

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_user_from_token,
)
from app.models.user import User


def test_hash_password_roundtrip():
    hashed = hash_password("correct-horse-battery-staple")
    assert hashed != "correct-horse-battery-staple"
    assert verify_password("correct-horse-battery-staple", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_create_access_token_decodes_with_subject():
    token = create_access_token(data={"sub": "user-123"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "user-123"
    assert "exp" in payload


def test_create_refresh_token_is_flagged_as_refresh():
    token = create_refresh_token(data={"sub": "user-123"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["type"] == "refresh"


def test_expired_access_token_is_rejected():
    token = create_access_token(data={"sub": "user-123"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(Exception):
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


@pytest.mark.asyncio
async def test_get_user_from_token_returns_user(db_session):
    user = User(
        email="jwt-test@example.com",
        hashed_password=hash_password("password123"),
        full_name="JWT Test",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    resolved = await get_user_from_token(token, db_session)

    assert resolved is not None
    assert resolved.id == user.id


@pytest.mark.asyncio
async def test_get_user_from_token_rejects_refresh_token(db_session):
    user = User(
        email="jwt-test-2@example.com",
        hashed_password=hash_password("password123"),
        full_name="JWT Test 2",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = create_refresh_token(data={"sub": str(user.id)})
    resolved = await get_user_from_token(token, db_session)

    assert resolved is None


@pytest.mark.asyncio
async def test_get_user_from_token_rejects_garbage(db_session):
    resolved = await get_user_from_token("not-a-real-token", db_session)
    assert resolved is None
