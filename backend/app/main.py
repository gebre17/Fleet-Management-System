"""Main FastAPI application."""

import logging
from uuid import UUID

from fastapi import Depends, FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import get_db_session
from app.core.error_tracking import configure_error_tracking
from app.core.events import shutdown_handler, startup_handler
from app.core.logging import configure_logging
from app.core.security import get_user_from_token
from app.services.vehicle_service import VehicleService
from app.websocket.manager import manager

configure_logging()
configure_error_tracking()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TrackFleet API",
    version="1.0.0",
    description="Real-time vehicle tracking system",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Add event handlers
app.add_event_handler("startup", startup_handler)
app.add_event_handler("shutdown", shutdown_handler)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.websocket("/ws/fleet")
async def websocket_fleet(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """
    WebSocket endpoint streaming live location updates and alerts for
    every vehicle owned by the authenticated user (used by the live map).
    """
    user = await get_user_from_token(token, db)
    if user is None or not user.is_active:
        await websocket.close(code=4401)
        return

    room = f"fleet:{user.id}"
    await manager.connect(websocket, room)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
    except Exception as e:
        logger.error(f"Fleet WebSocket error: {e}")
        manager.disconnect(websocket, room)


@app.websocket("/ws/{vehicle_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    vehicle_id: UUID,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """
    WebSocket endpoint for real-time tracking of a single vehicle.

    Args:
        websocket: WebSocket connection
        vehicle_id: Vehicle ID to subscribe to
        token: JWT access token (query param — browsers can't set WS headers)
    """
    user = await get_user_from_token(token, db)
    if user is None or not user.is_active:
        await websocket.close(code=4401)
        return

    try:
        await VehicleService.get_vehicle(vehicle_id=vehicle_id, user_id=user.id, db=db)
    except Exception:
        await websocket.close(code=4404)
        return

    room = str(vehicle_id)
    await manager.connect(websocket, room)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
        logger.info(f"Client disconnected from vehicle: {vehicle_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, room)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
