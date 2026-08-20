"""Authentication routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.models.user import User
from app.services.auth_service import AuthService

router = APIRouter()


class RegisterRequest(BaseModel):
    """Register request schema."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=100)


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response schema."""

    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Register a new user.

    Args:
        request: Registration request
        db: Database session

    Returns:
        Access and refresh tokens
    """
    user = await AuthService.register_user(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        db=db,
    )

    tokens = AuthService.create_tokens(str(user.id))
    return tokens


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Login user.

    Args:
        request: Login request
        db: Database session

    Returns:
        Access and refresh tokens
    """
    user = await AuthService.authenticate_user(
        email=request.email,
        password=request.password,
        db=db,
    )

    tokens = AuthService.create_tokens(str(user.id))
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Exchange a refresh token for a new access/refresh token pair.

    Args:
        request: Refresh request containing the refresh token
        db: Database session

    Returns:
        New access and refresh tokens
    """
    from jose import JWTError, jwt

    from app.core.config import settings

    try:
        payload = jwt.decode(
            request.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return AuthService.create_tokens(user_id)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user info.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return current_user


@router.post("/logout")
async def logout() -> dict:
    """
    Logout user (token blacklisting in production).

    Returns:
        Success message
    """
    return {"message": "Logged out successfully"}
