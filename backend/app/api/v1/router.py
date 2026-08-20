"""API v1 router."""

from fastapi import APIRouter

from app.api.v1 import alerts, auth, geofences, reports, tracking, vehicles

api_router = APIRouter(prefix="/api/v1", tags=["api_v1"])

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
api_router.include_router(tracking.router, prefix="/tracking", tags=["tracking"])
api_router.include_router(geofences.router, prefix="/geofences", tags=["geofences"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
