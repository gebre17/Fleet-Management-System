# TrackFleet — Real-Time Vehicle Tracking System

A comprehensive full-stack vehicle tracking system built with modern technologies. Track fleet vehicles in real-time on a live map, manage geofences, receive alerts, and generate reports.

## Features

### Core Functionality
- **Real-time GPS Tracking**: Live vehicle locations updated via WebSocket
- **Live Map Dashboard**: Interactive map with vehicle markers and routes
- **Geofence Management**: Create circular/polygon geofences and assign vehicles
- **Alert System**: Automatic alerts for geofence entries/exits, speeding, offline status
- **Activity Reports**: Distance, speed, activity duration, and geofence event reports
- **User Authentication**: JWT-based auth with role-based access control

### Technology Stack
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Zustand, Leaflet.js
- **Backend**: Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Database**: PostgreSQL 15
- **Real-time**: WebSockets (FastAPI native) + MQTT (Mosquitto)
- **Cache**: Redis 7
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx

## Project Structure

```
vehicle-tracking-system/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── tracker-simulator/ # GPS device simulator
├── infrastructure/    # Docker, Nginx, scripts
├── docs/              # Documentation
└── docker-compose.yml # Orchestration
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker Compose

1. **Clone and setup**:
```bash
cd vehicle-tracking-system
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

2. **Start the stack**:
```bash
docker-compose up -d
```

3. **Initialize database** (first run):
```bash
docker-compose exec backend alembic upgrade head
```

4. **Access the application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Nginx: http://localhost

### Local Development

#### Backend Setup

1. **Install dependencies**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. **Run migrations**:
```bash
alembic upgrade head
```

4. **Start the server**:
```bash
uvicorn app.main:app --reload
```

#### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Start development server**:
```bash
npm run dev
```

3. **Open browser**: http://localhost:3000

### GPS Simulator

To simulate vehicle movements and send location data:

```bash
cd tracker-simulator
pip install -r requirements.txt
python simulator.py --vehicles 5 --interval 5 --host localhost --port 1883
```

## API Documentation

Full API documentation is available at `/docs` when the backend is running.

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info

#### Vehicles
- `GET /api/v1/vehicles` - List vehicles (paginated)
- `POST /api/v1/vehicles` - Create vehicle
- `GET /api/v1/vehicles/{id}` - Get vehicle details
- `PUT /api/v1/vehicles/{id}` - Update vehicle
- `DELETE /api/v1/vehicles/{id}` - Delete vehicle

#### Tracking
- `POST /api/v1/tracking/{vehicle_id}/location` - Ingest GPS location
- `GET /api/v1/tracking/{vehicle_id}/location` - Get latest location
- `GET /api/v1/tracking/{vehicle_id}/history` - Get location history

#### Geofences
- `GET/POST /api/v1/geofences` - List/Create geofences
- `GET/PUT/DELETE /api/v1/geofences/{id}` - Manage geofences
- `POST /api/v1/geofences/{id}/vehicles` - Assign vehicle to geofence
- `DELETE /api/v1/geofences/{id}/vehicles/{vehicle_id}` - Unassign vehicle

#### Alerts
- `GET /api/v1/alerts` - List alerts with filters
- `PUT /api/v1/alerts/{id}/read` - Mark alert as read
- `PUT /api/v1/alerts/read-all` - Mark all alerts as read

#### Reports
- `GET /api/v1/reports/distance` - Distance report
- `GET /api/v1/reports/activity` - Activity report
- `GET /api/v1/reports/speed` - Speed report
- `GET /api/v1/reports/geofence-events` - Geofence events report

### WebSocket

Connect to real-time vehicle updates:

```
ws://localhost:8000/ws/{vehicle_id}
```

Receive location updates in real-time as vehicles move.

## Configuration

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/trackfleet
REDIS_URL=redis://localhost:6379
MQTT_HOST=localhost
MQTT_PORT=1883
SECRET_KEY=your-jwt-secret-key
SPEED_ALERT_THRESHOLD_KMH=120
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_MAP_TILE_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```

## Database Schema

The system uses PostgreSQL with async SQLAlchemy. Key tables include:

- `users` - User accounts
- `vehicles` - Fleet vehicles
- `locations` - GPS points (indexed for fast history queries)
- `geofences` - Geographic boundaries
- `geofence_vehicles` - M2M relationship
- `alerts` - System alerts
- `location_history` - Historical tracking data

All tables have timestamps and proper indexing for performance.

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Development Testing

The frontend is tested through manual interaction and browser dev tools. Consider adding Cypress for e2e testing in production.

## Deployment

### Docker Production Build

```bash
docker-compose -f docker-compose.yml up -d
```

### Environment for Production

Create production `.env` files with:
- Strong JWT secret key
- Production database credentials
- Production MQTT broker details
- CORS origins restricted to your domain

## Troubleshooting

### Backend won't connect to database
- Ensure PostgreSQL container is healthy: `docker-compose ps`
- Check logs: `docker-compose logs postgres`

### WebSocket connection failing
- Verify CORS is properly configured
- Check browser console for connection errors
- Ensure backend is running and accessible

### No location updates on map
- Verify simulator is running and MQTT is connected
- Check backend logs for location ingestion errors
- Confirm vehicle device_id matches simulator device_id

## Performance Considerations

- **Location History**: Limited to 10,000 records per request; use date filters
- **Real-time Updates**: WebSocket connections scale to thousands per server
- **Geofence Checks**: Runs synchronously on location ingest (async optimization available)
- **Caching**: Latest locations cached in Redis (5-min TTL)

## Security Notes

- All API endpoints require JWT authentication (except auth endpoints)
- Passwords are bcrypt-hashed
- CORS is restricted to frontend origin
- Use HTTPS in production
- Rotate JWT secret key regularly
- Enable MQTT authentication in production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
1. Check the [API Documentation](docs/API.md)
2. Review [Architecture Guide](docs/ARCHITECTURE.md)
3. Open an issue with detailed reproduction steps
