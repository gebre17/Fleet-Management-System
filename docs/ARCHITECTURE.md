# TrackFleet Architecture

## System Overview

TrackFleet is a real-time vehicle tracking system with three main tiers:

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                             │
│  Next.js Frontend (React, TypeScript, Tailwind CSS)        │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                   API Gateway (Nginx)                        │
├──────────────────────────────────────────────────────────────┤
│                    Application Layer                         │
│  FastAPI Backend (Python 3.11, async)                      │
│  ├─ REST API Routes (/api/v1/*)                           │
│  ├─ WebSocket Endpoint (/ws/{vehicle_id})                 │
│  └─ MQTT Client (trackfleet/devices/+/location)           │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ├─ PostgreSQL (persistent data)                           │
│  ├─ Redis (caching & session store)                        │
│  └─ Mosquitto MQTT (pub/sub for IoT)                      │
└──────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend (Next.js 14)

**Directory Structure**:
```
frontend/src/
├── app/               # Next.js App Router
│   ├── (auth)/       # Authentication routes
│   ├── (dashboard)/  # Protected dashboard routes
│   └── globals.css
├── components/        # React components
│   ├── map/          # Map-related components
│   ├── vehicles/     # Vehicle list/details
│   ├── dashboard/    # Dashboard widgets
│   └── layout/       # Layout shells
├── hooks/            # Custom React hooks
├── store/            # Zustand state management
├── types/            # TypeScript interfaces
└── lib/              # Utilities
    ├── api.ts        # Axios client with interceptors
    ├── websocket.ts  # WebSocket client
    └── utils.ts      # Helper functions
```

**Key Features**:
- **Client-Side Auth**: JWT stored in Zustand + localStorage
- **State Management**: Zustand for vehicles, alerts, auth
- **Real-time Updates**: WebSocket for live location tracking
- **API Client**: Axios with automatic token refresh
- **Maps**: Leaflet with React-Leaflet wrapper
- **Charts**: Recharts for reports

### Backend (FastAPI)

**Directory Structure**:
```
backend/app/
├── api/v1/           # API routes (routers)
│   ├── auth.py      # Authentication endpoints
│   ├── vehicles.py  # Vehicle CRUD
│   ├── tracking.py  # Location ingestion
│   ├── geofences.py # Geofence management
│   ├── alerts.py    # Alert queries
│   └── reports.py   # Report generation
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic request/response models
├── services/        # Business logic layer
│   ├── auth_service.py
│   ├── vehicle_service.py
│   ├── tracking_service.py
│   ├── geofence_service.py
│   ├── alert_service.py
│   └── report_service.py
├── websocket/       # WebSocket connection management
├── mqtt/            # MQTT client & handlers
├── core/            # Configuration & utilities
│   ├── config.py    # Settings from env vars
│   ├── database.py  # SQLAlchemy setup
│   ├── security.py  # JWT & password utilities
│   └── events.py    # Startup/shutdown handlers
├── utils/           # Helper functions
│   ├── geo.py      # Geofencing algorithms
│   └── helpers.py  # Miscellaneous utilities
└── main.py         # FastAPI app initialization
```

**Request Flow**:
1. Client makes HTTP request → Nginx → FastAPI
2. FastAPI route handler validates request with Pydantic
3. Handler calls Service layer for business logic
4. Service queries Database (async SQLAlchemy)
5. Response is serialized by Pydantic schema
6. Response sent back to client

**WebSocket Flow**:
1. Client connects to `/ws/{vehicle_id}`
2. ConnectionManager adds client to set
3. When location is ingested, it broadcasts to subscribed clients
4. Client disconnects → ConnectionManager removes from set

**MQTT Flow**:
1. IoT device publishes to `trackfleet/devices/{device_id}/location`
2. MQTT client subscribes and receives message
3. Triggers `tracking_service.ingest_location()`
4. Location saved to DB + cached in Redis + broadcast via WS

## Data Flow

### Location Ingestion Flow

```
IoT Device (MQTT)
    ↓
Mosquitto Broker
    ↓
MQTT Client (listening to trackfleet/devices/+/location)
    ↓
TrackingService.ingest_location()
    ├─ Save Location to PostgreSQL
    ├─ Update Vehicle.status = 'active'
    ├─ Cache in Redis (5 min TTL)
    ├─ Broadcast via WebSocket to subscribed clients
    └─ Run Geofence Check
        └─ If geofence crossed → Create Alert + Broadcast
```

### Alert Creation Flow

```
Geofence Service Check
    ├─ Determine if point in geofence
    ├─ Compare with previous state (from Redis)
    └─ If changed → AlertService.create_alert()
        ├─ Save Alert to PostgreSQL
        ├─ Broadcast Alert via WebSocket
        └─ Update Alert counter in Zustand (frontend)
```

## Database Schema

### Relationships

```
User (1) ──→ (many) Vehicle
User (1) ──→ (many) Geofence
Vehicle (many) ↔ (many) Geofence [via GeofenceVehicle]
Vehicle (1) ──→ (many) Location
Vehicle (1) ──→ (many) Alert
Geofence (1) ──→ (many) Alert
```

### Key Indexes

```sql
-- Vehicle queries
CREATE INDEX ix_vehicles_user_id ON vehicles(user_id);
CREATE INDEX ix_vehicles_plate_number ON vehicles(plate_number);

-- Location history (critical for performance)
CREATE INDEX ix_locations_vehicle_id ON locations(vehicle_id);
CREATE INDEX ix_locations_vehicle_timestamp ON locations(vehicle_id, timestamp DESC);

-- Alert queries
CREATE INDEX ix_alerts_vehicle_id ON alerts(vehicle_id);
CREATE INDEX ix_alerts_triggered_at ON alerts(triggered_at);
```

## Geofencing Algorithm

### Circle Detection (Haversine)

```python
distance = haversine_distance(vehicle_lat, vehicle_lng, 
                               geofence_center_lat, geofence_center_lng)
is_inside = distance <= geofence_radius_meters
```

### Polygon Detection (Ray-Casting)

```python
def point_in_polygon(lat, lng, polygon_coords):
    # Cast a ray from point to infinity and count intersections
    # Even count = outside, odd count = inside
    ...
```

Both algorithms run synchronously on each location ingest for immediate alert generation.

## Caching Strategy

### Redis Cache Keys

```
location:{vehicle_id}          # Latest GPS point (5 min TTL)
geofence_state:{vehicle_id}:{geofence_id}  # "inside"/"outside" (persistent)
session:{token}                # Token blacklist (optional for logout)
```

### Cache Invalidation

- **Location Cache**: Automatic TTL expiry (5 min)
- **Geofence State**: Manual update on geofence crossing
- **Session Cache**: Manual on logout

## Scalability Considerations

### Horizontal Scaling

**Frontend**: 
- Stateless Next.js containers
- Use CDN for static assets
- Session via JWT (not server session)

**Backend**:
- Multiple FastAPI instances behind load balancer
- Shared PostgreSQL (connection pooling)
- Shared Redis (pub/sub for broadcast)
- MQTT topic subscriptions on each instance (all receive messages)

**Database**:
- PostgreSQL read replicas for analytics
- Archive old locations to separate cold storage

### Performance Optimizations

1. **Location Query Optimization**:
   - Composite index on (vehicle_id, timestamp DESC)
   - Limit history queries to date range
   - Pagination support

2. **Geofence Check Optimization**:
   - Cache geofence geometries in memory
   - Queue expensive calculations (Celery optional)
   - Early-exit for inactive geofences

3. **WebSocket Optimization**:
   - ConnectionManager uses set (O(1) add/remove)
   - Per-vehicle broadcast (not global)
   - Client-side unsubscribe on page leave

## Security Architecture

### Authentication
- JWT tokens (access + refresh)
- Refresh tokens stored server-side (blacklist)
- Password hashed with bcrypt
- Token refresh flow on 401 response

### Authorization
- Role-based (admin, operator, viewer)
- Resource-level (users only see their vehicles)
- All protected endpoints check `get_current_user` dependency

### Data Protection
- HTTPS in production (via nginx reverse proxy)
- CORS restricted to frontend origin
- MQTT authentication in production
- Secrets from environment variables

## Deployment Architecture

### Docker Services

```yaml
postgres     # Persistent data store
redis        # Cache & pub/sub
mosquitto    # MQTT broker
backend      # FastAPI app
frontend     # Next.js app
nginx        # Reverse proxy & load balancer
```

### Environment Variables

Sensitive config injected at runtime:
- Database credentials
- JWT secret key
- API URLs
- MQTT credentials

### Health Checks

All services include health checks:
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- FastAPI: `GET /health`
- Nginx: checks upstream services

## Monitoring & Logging

### Logging Strategy
- Structured logging to stdout (container-friendly)
- Log level: INFO in production
- Includes request IDs for tracing

### Metrics to Monitor
- API response time (p50, p95, p99)
- WebSocket connection count
- Location ingest rate
- Database query time
- MQTT message throughput

## Future Enhancements

1. **Heavy Job Processing**: Celery for report generation
2. **Real-time Analytics**: ClickHouse for time-series data
3. **Machine Learning**: Anomaly detection on speed/routes
4. **Mobile App**: React Native or Flutter client
5. **Advanced Mapping**: Vector tiles, custom styling
6. **Audit Logging**: Track all API operations
7. **Multi-tenancy**: Support multiple organizations
