# TrackFleet Deployment Guide

## 🚀 Production Deployment

This guide covers deploying TrackFleet to a production environment.

## Pre-Deployment Checklist

### Security
- [ ] Change default JWT secret in `backend/.env`
- [ ] Generate strong database password
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up MQTT broker authentication
- [ ] Enable Redis password
- [ ] Implement rate limiting in Nginx
- [ ] Configure CORS to specific domain
- [ ] Use environment variables for all secrets

### Infrastructure
- [ ] Provision servers (VPS, cloud instance)
- [ ] Set up domain name and DNS
- [ ] Install Docker & Docker Compose
- [ ] Configure firewall rules
- [ ] Set up backup strategy
- [ ] Configure monitoring/alerting
- [ ] Set up log aggregation

### Performance
- [ ] Configure database connection pooling
- [ ] Set up Redis persistence
- [ ] Optimize Nginx caching
- [ ] Enable compression for API responses
- [ ] Set up CDN for static assets

## Deployment Methods

### Option 1: Docker Compose on VPS

#### Step 1: Prepare Server

```bash
# SSH into server
ssh user@your-server.com

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

#### Step 2: Deploy Application

```bash
# Clone repository
git clone https://github.com/yourusername/vehicle-tracking-system.git
cd vehicle-tracking-system

# Create production env files
cat > backend/.env << EOF
DATABASE_URL=postgresql+asyncpg://trackfleet:$(openssl rand -base64 32)@postgres:5432/trackfleet
REDIS_URL=redis://:$(openssl rand -base64 32)@redis:6379
MQTT_HOST=mosquitto
MQTT_PORT=1883
SECRET_KEY=$(openssl rand -base64 64)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SPEED_ALERT_THRESHOLD_KMH=120
EOF

cat > frontend/.env.production << EOF
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com
NEXT_PUBLIC_MAP_TILE_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
EOF

# Create production docker-compose override
cat > docker-compose.production.yml << 'EOF'
version: '3.9'

services:
  postgres:
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
  
  redis:
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redisdata:/data
  
  backend:
    environment:
      - DEBUG=false
    restart: always
  
  frontend:
    restart: always
  
  nginx:
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infrastructure/nginx/nginx.production.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    restart: always

volumes:
  pgdata:
  redisdata:
EOF

# Start with SSL
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d
```

### Option 2: AWS Deployment

#### Using ECS (Elastic Container Service)

```bash
# Build and push images to ECR
aws ecr create-repository --repository-name trackfleet-backend
aws ecr create-repository --repository-name trackfleet-frontend

# Tag and push
docker tag trackfleet-backend:latest ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/trackfleet-backend:latest
docker push ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/trackfleet-backend:latest

# Set up RDS PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier trackfleet-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username trackfleet \
  --master-user-password <strong-password>

# Set up ElastiCache for Redis
aws elasticache create-cache-cluster \
  --cache-cluster-id trackfleet-cache \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1

# Create ECS cluster and deploy
aws ecs create-cluster --cluster-name trackfleet
# ... (create task definitions and services)
```

### Option 3: Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace trackfleet

# Create ConfigMap for configuration
kubectl create configmap trackfleet-config \
  --from-literal=NEXT_PUBLIC_API_URL=https://api.yourdomain.com \
  -n trackfleet

# Create Secret for sensitive data
kubectl create secret generic trackfleet-secrets \
  --from-literal=DATABASE_URL=postgresql://... \
  --from-literal=REDIS_URL=redis://... \
  --from-literal=SECRET_KEY=... \
  -n trackfleet

# Deploy with Helm or kubectl apply -f
kubectl apply -f k8s/postgresql.yaml -n trackfleet
kubectl apply -f k8s/redis.yaml -n trackfleet
kubectl apply -f k8s/backend.yaml -n trackfleet
kubectl apply -f k8s/frontend.yaml -n trackfleet
kubectl apply -f k8s/nginx.yaml -n trackfleet
```

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com

# Configure Nginx for SSL
sudo vi /etc/nginx/nginx.conf
```

Update `nginx.production.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Modern configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Database Backup & Recovery

### Automated PostgreSQL Backups

```bash
# Create backup script
cat > /home/user/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/trackfleet"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/trackfleet_$TIMESTAMP.sql.gz"

mkdir -p $BACKUP_DIR

docker-compose exec -T postgres pg_dump -U trackfleet trackfleet | gzip > $BACKUP_FILE

# Keep only last 7 days
find $BACKUP_DIR -name "trackfleet_*.sql.gz" -mtime +7 -delete

echo "Backup created: $BACKUP_FILE"
EOF

chmod +x /home/user/backup-db.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/user/backup-db.sh") | crontab -
```

### Restore from Backup

```bash
# Decompress backup
gunzip trackfleet_20240115_020000.sql.gz

# Restore to database
docker-compose exec -T postgres psql -U trackfleet trackfleet < trackfleet_20240115_020000.sql
```

## Monitoring & Logging

### Set up Monitoring

```bash
# Install Prometheus & Grafana (optional)
docker run -d -p 9090:9090 prom/prometheus

# Collect metrics from backend
# Add to backend app:
# from prometheus_client import Counter, Histogram
# requests_total = Counter('requests_total', 'Total requests')
# request_duration = Histogram('request_duration_seconds', 'Request duration')
```

### Log Aggregation

```bash
# Configure Docker to use JSON logging driver
cat > /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# Restart Docker
sudo systemctl restart docker

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Performance Tuning

### Database

```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_locations_vehicle_timestamp ON locations(vehicle_id, timestamp DESC);
CREATE INDEX idx_alerts_vehicle_id ON alerts(vehicle_id);
CREATE INDEX idx_geofences_owner_id ON geofences(owner_id);

-- Vacuum and analyze
VACUUM ANALYZE;

-- Check slow queries
ALTER SYSTEM SET log_min_duration_statement = 1000; -- Log queries slower than 1 second
SELECT pg_reload_conf();
```

### Redis

```bash
# Monitor Redis memory usage
redis-cli info memory

# Implement cache eviction
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Nginx

```nginx
# Add caching for static assets
location ~* ^.+\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# Gzip compression
gzip on;
gzip_types text/plain text/css text/javascript application/json application/javascript;
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml - add multiple backend instances
services:
  backend-1:
    build: ./backend
    environment:
      - INSTANCE_ID=1
  
  backend-2:
    build: ./backend
    environment:
      - INSTANCE_ID=2

  nginx:
    # Load balance between backend instances
    upstream backend {
      server backend-1:8000;
      server backend-2:8000;
    }
```

### Database Read Replicas

```bash
# Create read replica in production
aws rds create-db-instance-read-replica \
  --db-instance-identifier trackfleet-db-read \
  --source-db-instance-identifier trackfleet-db
```

## Troubleshooting Production

### Check Service Health

```bash
# All services running?
docker-compose ps

# Check logs
docker-compose logs --tail=100 backend
docker-compose logs --tail=100 postgres
docker-compose logs --tail=100 nginx

# Test connectivity
curl -I https://yourdomain.com
curl -I https://api.yourdomain.com/health

# Database connection
docker-compose exec postgres psql -U trackfleet -d trackfleet -c "SELECT 1"
```

### Performance Issues

```bash
# Check disk space
df -h

# Check memory
free -h

# Check CPU
top -b -n 1 | head -20

# Database query performance
docker-compose exec postgres psql -U trackfleet -d trackfleet -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

## Rollback Procedure

```bash
# Keep current version tagged
git tag production-v1.0.0
git push origin production-v1.0.0

# Rollback to previous version
docker-compose down
git checkout production-v0.9.9
docker-compose up -d

# Or use docker image version
docker-compose pull v0.9.9
docker-compose up -d
```

## Maintenance Windows

### Schedule downtime if needed

```bash
# Disable traffic at Nginx
sudo systemctl stop nginx

# Perform maintenance (DB migration, etc.)
docker-compose exec backend alembic upgrade head

# Re-enable traffic
sudo systemctl start nginx
```

## Security Hardening

### Firewall Rules

```bash
# UFW setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### SSH Hardening

```bash
# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Use SSH keys only
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Restart SSH
sudo systemctl restart sshd
```

## Cost Optimization

- Use spot instances for non-critical workloads
- Auto-scaling based on demand
- Archive old location data to cold storage
- Use CDN for static assets
- Optimize database instance size

---

**Need help?** Check `docs/ARCHITECTURE.md` for system design details.
