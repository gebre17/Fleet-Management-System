"""Seed database with sample data."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models import Base, User, Vehicle
from app.models.vehicle import VehicleType, VehicleStatus
from app.core.security import hash_password
from uuid import uuid4


async def seed_database():
    """Seed database with sample data."""
    # Create engine
    engine = create_async_engine(
        "postgresql+asyncpg://trackfleet:trackfleet_dev_password@postgres:5432/trackfleet"
    )

    # Create session
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create sample user
        user = User(
            id=uuid4(),
            email="demo@trackfleet.com",
            hashed_password=hash_password("password123"),
            full_name="Demo User",
            is_active=True,
        )
        session.add(user)
        await session.flush()

        # Create sample vehicles
        vehicles_data = [
            {
                "name": "Vehicle 001",
                "plate_number": "ABC-001",
                "type": VehicleType.CAR,
                "make": "Toyota",
                "model": "Camry",
                "year": 2023,
                "device_id": "device_001",
                "color": "white",
            },
            {
                "name": "Vehicle 002",
                "plate_number": "ABC-002",
                "type": VehicleType.TRUCK,
                "make": "Ford",
                "model": "F-150",
                "year": 2023,
                "device_id": "device_002",
                "color": "black",
            },
            {
                "name": "Vehicle 003",
                "plate_number": "ABC-003",
                "type": VehicleType.VAN,
                "make": "Mercedes",
                "model": "Sprinter",
                "year": 2022,
                "device_id": "device_003",
                "color": "silver",
            },
        ]

        for vehicle_data in vehicles_data:
            vehicle = Vehicle(
                id=uuid4(),
                user_id=user.id,
                status=VehicleStatus.OFFLINE,
                **vehicle_data,
            )
            session.add(vehicle)

        await session.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
