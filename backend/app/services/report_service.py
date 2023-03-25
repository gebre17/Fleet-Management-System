"""Report service."""
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models.location import Location
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.alert import Alert, AlertType
from app.utils.geo import haversine_distance


class ReportService:
    """Service for generating reports."""
    
    @staticmethod
    async def get_distance_report(
        vehicle_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: AsyncSession = None,
    ) -> List[dict]:
        """
        Generate distance report.
        
        Args:
            vehicle_id: Optional vehicle ID filter
            start_date: Start date filter
            end_date: End date filter
            db: Database session
        
        Returns:
            List of distance data per vehicle
        """
        # Get all locations in range
        stmt = select(Location)
        
        filters = []
        if vehicle_id:
            filters.append(Location.vehicle_id == vehicle_id)
        if start_date:
            filters.append(Location.timestamp >= start_date)
        if end_date:
            filters.append(Location.timestamp <= end_date)
        
        if filters:
            stmt = stmt.where(and_(*filters))
        
        stmt = stmt.order_by(Location.vehicle_id, Location.timestamp)
        
        result = await db.execute(stmt)
        locations = result.scalars().all()
        
        # Calculate distances
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
        vehicle_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: AsyncSession = None,
    ) -> List[dict]:
        """
        Generate activity report (online/offline duration).
        
        Args:
            vehicle_id: Optional vehicle ID filter
            start_date: Start date filter
            end_date: End date filter
            db: Database session
        
        Returns:
            List of activity data per vehicle
        """
        # Get all vehicles
        stmt = select(Vehicle)
        if vehicle_id:
            stmt = stmt.where(Vehicle.id == vehicle_id)
        
        result = await db.execute(stmt)
        vehicles = result.scalars().all()
        
        report = []
        
        for vehicle in vehicles:
            # Get locations for vehicle in time range
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
            
            # Calculate online time (time between first and last location)
            first_location = locations[0]
            last_location = locations[-1]
            
            if first_location and last_location:
                online_duration = (last_location.timestamp - first_location.timestamp).total_seconds() / 3600
                
                report.append({
                    "vehicle_id": str(vehicle.id),
                    "vehicle_name": vehicle.name,
                    "online_hours": round(online_duration, 2),
                    "location_count": len(locations),
                })
        
        return report
    
    @staticmethod
    async def get_speed_report(
        vehicle_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: AsyncSession = None,
    ) -> List[dict]:
        """
        Generate speed report (average and max speed).
        
        Args:
            vehicle_id: Optional vehicle ID filter
            start_date: Start date filter
            end_date: End date filter
            db: Database session
        
        Returns:
            List of speed data per vehicle
        """
        stmt = select(Location).where(Location.speed > 0)
        
        filters = []
        if vehicle_id:
            filters.append(Location.vehicle_id == vehicle_id)
        if start_date:
            filters.append(Location.timestamp >= start_date)
        if end_date:
            filters.append(Location.timestamp <= end_date)
        
        if filters:
            stmt = stmt.where(and_(*filters))
        
        result = await db.execute(stmt)
        locations = result.scalars().all()
        
        # Group by vehicle
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
        vehicle_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: AsyncSession = None,
    ) -> List[dict]:
        """
        Generate geofence events report.
        
        Args:
            vehicle_id: Optional vehicle ID filter
            start_date: Start date filter
            end_date: End date filter
            db: Database session
        
        Returns:
            List of geofence events
        """
        stmt = select(Alert).where(
            Alert.type.in_([AlertType.GEOFENCE_ENTER, AlertType.GEOFENCE_EXIT])
        )
        
        filters = []
        if vehicle_id:
            filters.append(Alert.vehicle_id == vehicle_id)
        if start_date:
            filters.append(Alert.triggered_at >= start_date)
        if end_date:
            filters.append(Alert.triggered_at <= end_date)
        
        if filters:
            stmt = stmt.where(and_(*filters))
        
        stmt = stmt.order_by(Alert.triggered_at)
        
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
