"""Report service."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert, AlertType
from app.models.location import Location
from app.models.vehicle import Vehicle
from app.utils.geo import haversine_distance


class ReportService:
    """Service for generating reports. All reports are scoped to vehicles
    owned by the requesting user."""

    @staticmethod
    async def get_distance_report(
        user_id: UUID,
        vehicle_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        db: AsyncSession = None,
    ) -> list[dict]:
        """Generate distance report."""
        stmt = select(Location).join(Vehicle, Vehicle.id == Location.vehicle_id)

        filters = [Vehicle.user_id == user_id]
        if vehicle_id:
            filters.append(Location.vehicle_id == vehicle_id)
        if start_date:
            filters.append(Location.timestamp >= start_date)
        if end_date:
            filters.append(Location.timestamp <= end_date)

        stmt = stmt.where(and_(*filters)).order_by(Location.vehicle_id, Location.timestamp)

        result = await db.execute(stmt)
        locations = result.scalars().all()

        report = {}
        current_vehicle = None
        prev_location = None

        for location in locations:
            if location.vehicle_id != current_vehicle:
                current_vehicle = location.vehicle_id
                prev_location = None

            if current_vehicle not in report:
                report[current_vehicle] = {"total_km": 0, "segments": 0}

            if prev_location:
                distance_m = haversine_distance(
                    prev_location.latitude,
                    prev_location.longitude,
                    location.latitude,
                    location.longitude,
                )
                report[current_vehicle]["total_km"] += distance_m / 1000
                report[current_vehicle]["segments"] += 1

            prev_location = location

        return [
            {
                "vehicle_id": str(vid),
                "total_km": round(data["total_km"], 2),
                "segments": data["segments"],
            }
            for vid, data in report.items()
        ]

    @staticmethod
    async def get_activity_report(
        user_id: UUID,
        vehicle_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        db: AsyncSession = None,
    ) -> list[dict]:
        """Generate activity report (online/offline duration)."""
        stmt = select(Vehicle).where(Vehicle.user_id == user_id)
        if vehicle_id:
            stmt = stmt.where(Vehicle.id == vehicle_id)

        result = await db.execute(stmt)
        vehicles = result.scalars().all()

        report = []

        for vehicle in vehicles:
            loc_stmt = select(Location).where(Location.vehicle_id == vehicle.id)

            if start_date:
                loc_stmt = loc_stmt.where(Location.timestamp >= start_date)
            if end_date:
                loc_stmt = loc_stmt.where(Location.timestamp <= end_date)

            loc_stmt = loc_stmt.order_by(Location.timestamp)

            loc_result = await db.execute(loc_stmt)
            locations = loc_result.scalars().all()

            if not locations:
                continue

            first_location = locations[0]
            last_location = locations[-1]

            online_duration = (last_location.timestamp - first_location.timestamp).total_seconds() / 3600

            report.append(
                {
                    "vehicle_id": str(vehicle.id),
                    "vehicle_name": vehicle.name,
                    "online_hours": round(online_duration, 2),
                    "location_count": len(locations),
                }
            )

        return report

    @staticmethod
    async def get_speed_report(
        user_id: UUID,
        vehicle_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        db: AsyncSession = None,
    ) -> list[dict]:
        """Generate speed report (average and max speed)."""
        stmt = select(Location).join(Vehicle, Vehicle.id == Location.vehicle_id).where(Location.speed > 0)

        filters = [Vehicle.user_id == user_id]
        if vehicle_id:
            filters.append(Location.vehicle_id == vehicle_id)
        if start_date:
            filters.append(Location.timestamp >= start_date)
        if end_date:
            filters.append(Location.timestamp <= end_date)

        stmt = stmt.where(and_(*filters))

        result = await db.execute(stmt)
        locations = result.scalars().all()

        report = {}
        for location in locations:
            if location.vehicle_id not in report:
                report[location.vehicle_id] = {"speeds": []}

            report[location.vehicle_id]["speeds"].append(location.speed)

        return [
            {
                "vehicle_id": str(vid),
                "avg_speed_kmh": round(sum(data["speeds"]) / len(data["speeds"]), 2),
                "max_speed_kmh": round(max(data["speeds"]), 2),
                "measurements": len(data["speeds"]),
            }
            for vid, data in report.items()
        ]

    @staticmethod
    async def get_geofence_events_report(
        user_id: UUID,
        vehicle_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        db: AsyncSession = None,
    ) -> list[dict]:
        """Generate geofence events report."""
        stmt = (
            select(Alert)
            .join(Vehicle, Vehicle.id == Alert.vehicle_id)
            .where(
                Alert.type.in_([AlertType.GEOFENCE_ENTER, AlertType.GEOFENCE_EXIT]),
            )
        )

        filters = [Vehicle.user_id == user_id]
        if vehicle_id:
            filters.append(Alert.vehicle_id == vehicle_id)
        if start_date:
            filters.append(Alert.triggered_at >= start_date)
        if end_date:
            filters.append(Alert.triggered_at <= end_date)

        stmt = stmt.where(and_(*filters)).order_by(Alert.triggered_at)

        result = await db.execute(stmt)
        alerts = result.scalars().all()

        return [
            {
                "vehicle_id": str(alert.vehicle_id),
                "geofence_id": str(alert.geofence_id) if alert.geofence_id else None,
                "event_type": alert.type.value,
                "message": alert.message,
                "timestamp": alert.triggered_at.isoformat(),
            }
            for alert in alerts
        ]


# Global report service instance
report_service = ReportService()
