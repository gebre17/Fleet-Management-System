"""Configuration management."""
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://trackfleet:password@localhost:5432/trackfleet"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # MQTT
    MQTT_HOST: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None

    # JWT
    SECRET_KEY: str = "change-this-super-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Alert thresholds
    SPEED_ALERT_THRESHOLD_KMH: float = 120.0
    OFFLINE_ALERT_THRESHOLD_MINUTES: int = 10
    LOW_BATTERY_THRESHOLD_PERCENT: int = 20

    # CORS — comma-separated list of allowed origins (override in production)
    CORS_ORIGINS_RAW: str = (
        "http://localhost:3000,http://localhost:3001,http://localhost:8000,http://localhost"
    )

    # App
    APP_TITLE: str = "TrackFleet API"
    APP_VERSION: str = "1.0.0"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
