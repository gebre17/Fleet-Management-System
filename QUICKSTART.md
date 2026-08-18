# TrackFleet Quick Start Guide

## 🚀 Start in 5 Minutes

### Prerequisites
- Docker & Docker Compose installed
- OR (for local dev):
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 15
  - Redis 7
  - Mosquitto MQTT

## Using Docker (Easiest)

```bash
# 1. Clone and navigate to project
cd Fleet-Management-System

# 2. Create your env files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 3. Build and start everything (migrations run automatically on backend startup)
docker-compose up -d --build

# 4. Open browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
# Nginx: http://localhost
```

Database migrations run automatically every time the backend container starts
(`backend/docker-entrypoint.sh` runs `alembic upgrade head` before `uvicorn`).
You only need to run it manually for local (non-Docker) development.

### Demo Credentials (if using seed data)
- Email: `demo@trackfleet.com`
- Password: `password123`

## Local Development

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (copy .env.example to .env and edit)
cp .env.example .env

# Start PostgreSQL, Redis, Mosquitto (via Docker or locally)
# Then run migrations:
alembic upgrade head

# Start server
uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Open: http://localhost:3000
```

### Simulator Setup
```bash
cd tracker-simulator

# Install dependencies
pip install -r requirements.txt

# Run simulator (creates 5 vehicles sending GPS data)
python simulator.py --vehicles 5 --interval 5
```

## Project Features

### ✅ Core Features Implemented

**Backend**
- [x] JWT Authentication (login/register/refresh)
- [x] Vehicle CRUD operations
- [x] Real-time GPS location ingestion
- [x] WebSocket for live tracking
- [x] MQTT client for IoT devices
- [x] Geofence management (circle + polygon)
- [x] Automatic geofence-based alerts
- [x] Alert system with severity levels
- [x] Distance, activity, speed, and geofence reports
- [x] Comprehensive error handling

**Frontend**
- [x] Authentication pages (login/register)
- [x] Dashboard with stats overview
- [x] Vehicle management page
- [x] Real-time alerts display
- [x] Geofence management interface
- [x] Activity reports
- [x] Settings page
- [x] Zustand state management
- [x] Axios API client with auth interceptors
- [x] WebSocket integration for live updates
- [x] TypeScript support throughout

**Infrastructure**
- [x] Docker containerization (backend, frontend)
- [x] Docker Compose orchestration
- [x] PostgreSQL with async SQLAlchemy
- [x] Redis caching layer
- [x] Mosquitto MQTT broker
- [x] Nginx reverse proxy
- [x] Database migrations (Alembic)

### 📚 Documentation
- [x] Comprehensive README
- [x] Architecture documentation
- [x] Quick start guide (this file)

## API Quick Reference

### Authentication
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass",
    "full_name": "John Doe"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass"
  }'
```

### Vehicles
```bash
# List vehicles
curl -X GET "http://localhost:8000/api/v1/vehicles?skip=0&limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create vehicle
curl -X POST http://localhost:8000/api/v1/vehicles \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vehicle 1",
    "plate_number": "ABC-123",
    "type": "car",
    "device_id": "device_001"
  }'
```

### Location Tracking
```bash
# Ingest location
curl -X POST http://localhost:8000/api/v1/tracking/{vehicle_id}/location \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "speed": 45.5,
    "heading": 180
  }'

# Get latest location
curl -X GET http://localhost:8000/api/v1/tracking/{vehicle_id}/location \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get location history
curl -X GET "http://localhost:8000/api/v1/tracking/{vehicle_id}/history?limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Geofences
```bash
# Create geofence (circle)
curl -X POST http://localhost:8000/api/v1/geofences \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Office Area",
    "type": "circle",
    "center_lat": 40.7128,
    "center_lng": -74.0060,
    "radius_meters": 500,
    "color": "#3B82F6"
  }'
```

### Reports
```bash
# Distance report
curl -X GET "http://localhost:8000/api/v1/reports/distance" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Activity report
curl -X GET "http://localhost:8000/api/v1/reports/activity" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Speed report
curl -X GET "http://localhost:8000/api/v1/reports/speed" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## WebSocket Connection

WebSocket endpoints require a valid JWT access token as a `token` query
parameter (browsers can't set custom headers on a WebSocket handshake).

```javascript
// Live updates for every vehicle you own (used by the Live Map page)
const ws = new WebSocket(`ws://localhost:8000/ws/fleet?token=${accessToken}`);

// Or live updates for a single vehicle
const ws = new WebSocket(`ws://localhost:8000/ws/${vehicleId}?token=${accessToken}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.type, data); // "location_update" or "alert"
};
```

## Troubleshooting

### Port already in use
```bash
# Change ports in docker-compose.yml or .env files
# Then restart services
docker-compose down
docker-compose up -d
```

### Database connection error
```bash
# Ensure PostgreSQL is running
docker-compose logs postgres

# Check if port 5432 is available
lsof -i :5432
```

### WebSocket connection failing
```bash
# Check if backend is running
docker-compose logs backend

# Verify CORS settings in backend/app/core/config.py
```

### Simulator not sending data
```bash
# Check MQTT connection
docker-compose logs mosquitto

# Verify device_id matches vehicle's device_id in database
```

## Next Steps

1. **Create Vehicles**: Register and create your first vehicle
2. **Simulate Data**: Run the simulator to send GPS data
3. **Create Geofences**: Set up circular or polygon geofences
4. **View Alerts**: Check real-time geofence alerts
5. **Generate Reports**: View activity and distance reports

## File Structure Reference

```
vehicle-tracking-system/
├── README.md                    # Main documentation
├── QUICKSTART.md               # This file
├── docker-compose.yml          # Container orchestration
│
├── backend/                     # Python/FastAPI backend
│   ├── app/
│   │   ├── api/v1/            # API route handlers
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   ├── core/              # Config & security
│   │   └── main.py            # FastAPI app
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile
│
├── frontend/                    # Next.js frontend
│   ├── src/
│   │   ├── app/               # Pages (Next.js App Router)
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks
│   │   ├── store/             # Zustand stores
│   │   ├── types/             # TypeScript types
│   │   └── lib/               # Utilities
│   ├── package.json           # npm dependencies
│   └── Dockerfile
│
├── tracker-simulator/           # GPS device simulator
│   ├── simulator.py
│   └── requirements.txt
│
└── infrastructure/              # Deployment files
    ├── nginx/
    ├── mosquitto.conf
    └── scripts/
```

## Performance Tips

1. **Database**: Use composite indexes on vehicle_id + timestamp
2. **Caching**: Redis caches latest locations (5 min TTL)
3. **Geofence**: Precompute boundaries when possible
4. **WebSocket**: One connection per vehicle-client pair
5. **Pagination**: Always use limit/offset for large result sets

## Security Checklist

- [ ] Change default JWT secret in production
- [ ] Use HTTPS with valid SSL certificate
- [ ] Enable MQTT authentication
- [ ] Restrict CORS to your domain
- [ ] Use strong database password
- [ ] Enable Redis password authentication
- [ ] Implement rate limiting
- [ ] Add API key for external integrations
- [ ] Enable audit logging
- [ ] Regular security updates

## Support & Resources

- **API Docs**: http://localhost:8000/docs (when running)
- **Architecture Guide**: `/docs/ARCHITECTURE.md`
- **GitHub Issues**: Check project repository for known issues
- **Logs**: `docker-compose logs [service_name]`

---

**Happy tracking! 🚗📍**
