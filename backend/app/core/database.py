"""Database configuration and session management."""
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import ProgrammingError
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for all models
Base = declarative_base()


async def get_db_session() -> AsyncSession:
    """Dependency to get database session."""
    async with async_session_maker() as session:
        yield session


async def init_db() -> None:
    """Initialize database tables, skipping any that already exist."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except ProgrammingError as e:
        # Tables already exist (e.g. container restart) — safe to continue.
        logger.warning("Database schema already initialised, skipping create_all: %s", e.orig)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
