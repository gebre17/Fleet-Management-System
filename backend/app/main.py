"""Main FastAPI application."""
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.events import startup_handler, shutdown_handler
from app.websocket.manager import manager

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8000", "http://localhost"],
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


@app.websocket("/ws/{vehicle_id}")
async def websocket_endpoint(websocket: WebSocket, vehicle_id: str) -> None:
    """
    WebSocket endpoint for real-time vehicle tracking.
    
    Args:
        websocket: WebSocket connection
        vehicle_id: Vehicle ID to subscribe to
    """
    await manager.connect(websocket, vehicle_id)
    try:
        while True:
            # Keep connection open
            data = await websocket.receive_json()
            # Echo back to all subscribers
            await manager.broadcast_to_room(vehicle_id, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, vehicle_id)
        logger.info(f"Client disconnected from vehicle: {vehicle_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, vehicle_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
