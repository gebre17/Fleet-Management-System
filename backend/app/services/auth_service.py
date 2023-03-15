"""Authentication service."""
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserRole
from app.schemas.vehicle import VehicleCreate
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from fastapi import HTTPException, status


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    async def register_user(
        email: str,
        password: str,
        full_name: str,
        db: AsyncSession,
    ) -> User:
        """
        Register a new user.
        
        Args:
            email: User email
            password: User password (plain text)
            full_name: User full name
            db: Database session
        
        Returns:
            Created user
        
        Raises:
            HTTPException: If email already exists
        """
        # Check if user exists
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        # Create new user
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=UserRole.OPERATOR,
            is_active=True,
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def authenticate_user(
        email: str,
        password: str,
        db: AsyncSession,
    ) -> User:
        """
        Authenticate user by email and password.
        
        Args:
            email: User email
            password: User password (plain text)
            db: Database session
        
        Returns:
            Authenticated user
        
        Raises:
            HTTPException: If credentials are invalid
        """
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
        
        return user
    
    @staticmethod
    def create_tokens(user_id: str) -> dict:
        """
        Create access and refresh tokens for user.
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with access_token and refresh_token
        """
        access_token = create_access_token(data={"sub": user_id})
        refresh_token = create_refresh_token(data={"sub": user_id})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
