# INSTALLATION & DEPLOYMENT GUIDE

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Git
- curl (for testing)
- SSH key (for DigitalOcean deployment)

---

## Local Setup

### Option 1: Automatic (Recommended)

```bash
# Linux/macOS
chmod +x setup.sh
./setup.sh

# Windows
setup.bat
```

### Option 2: Manual

```bash
# Clone repository
git clone https://github.com/YOUR_REPO/frond.git
cd frond

# Build images
docker-compose build

# Start services
docker-compose up -d

# Wait for database to be ready
sleep 30

# Test API
curl http://localhost:8000/health
```

---

## Quick Test

```bash
# Upload file
curl -X POST -F "file=@README.md" http://localhost:8000/files

# List files
curl http://localhost:8000/files

# Check status
curl http://localhost:8000/files/{file_id}

# Get result (after processing)
curl http://localhost:8000/files/{file_id}/result

# API Documentation
open http://localhost:8000/docs
```

---

## Docker Compose Services

### API (FastAPI)
```
Port: 8000
Health: GET /health
Docs: GET /docs
```

### Worker (Celery)
```
Processes async tasks
Connects to Redis
```

### Database (PostgreSQL)
```
Port: 5432
User: user
Password: password
Database: filedb
```

### Cache/Queue (Redis)
```
Port: 6379
Broker for Celery
```

### Storage (MinIO)
```
Console: http://localhost:9001
Access: http://localhost:9000
User: minioadmin
Password: minioadmin
```

---

## Production Deployment

### Prerequisites

1. **DigitalOcean Droplet** (Ubuntu 22.04+, 2GB RAM)
2. **GitHub Secrets** configured:
   - `DIGITALOCEAN_HOST` – Droplet IP/domain
   - `DIGITALOCEAN_USER` – SSH user (default: root)
   - `DIGITALOCEAN_PRIVATE_KEY` – SSH private key

3. **SSH Setup** on Droplet:
```bash
ssh root@DROPLET_IP

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create app directory
mkdir -p /app/file-ingestor
cd /app/file-ingestor

# Clone repository
git clone <YOUR_REPO_URL> .

# Copy env file
cp .env.example .env
# Edit .env with production values
```

### Automated Deployment

Push to `main` branch → GitHub Actions automatically deploys:

```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

Pipeline will:
1. Run tests
2. Build Docker images
3. Publish to GitHub Container Registry
4. Deploy to DigitalOcean
5. Run health check

### Manual Deployment

```bash
# Using deploy script
chmod +x deploy.sh
./deploy.sh <DROPLET_IP> root <PATH_TO_SSH_KEY>

# Or using make
make deploy
```

---

## Monitoring & Logs

```bash
# View all logs
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f db

# Check services status
docker-compose ps
```

---

## Database Migrations

```bash
# Connect to database
docker-compose exec db psql -U user -d filedb

# Or with migrations tool (if added later)
docker-compose exec api alembic upgrade head
```

---

## Troubleshooting

### Port already in use
```bash
# Find process using port
lsof -i :8000

# Or change port in docker-compose.yml
```

### Database connection failed
```bash
# Check DB logs
docker-compose logs db

# Restart DB
docker-compose restart db
```

### Worker not processing files
```bash
# Check worker logs
docker-compose logs worker

# Check Redis
docker-compose logs redis
```

### MinIO not accessible
```bash
# Check MinIO logs
docker-compose logs minio

# Access console
http://localhost:9001
```

---

## Cleanup

```bash
# Stop services
docker-compose down

# Remove volumes
docker-compose down -v

# Remove images
docker image rm frond_api frond_worker
```

---

## Performance Tuning

### For more workers
Edit `docker-compose.yml`:
```yaml
worker:
  scale: 3  # Run 3 worker instances
```

### For more API instances
```yaml
api:
  scale: 2  # Run 2 API instances with load balancer
```

### Increase memory
```yaml
services:
  api:
    mem_limit: 1g
```

---

## Security Notes

- 🔒 Change default MinIO credentials in production
- 🔒 Use strong PostgreSQL password
- 🔒 Enable HTTPS for production (reverse proxy: nginx/caddy)
- 🔒 Use secrets manager (HashiCorp Vault)
- 🔒 Implement rate limiting
- 🔒 Add authentication to API endpoints

---

## Backup Strategy

```bash
# Backup database
docker-compose exec db pg_dump -U user filedb > backup.sql

# Backup MinIO data
docker-compose exec minio mc mirror minio/uploads ./backups/

# Restore from backup
docker-compose exec db psql -U user filedb < backup.sql
```

---

## Support & Resources

- 📚 FastAPI: https://fastapi.tiangolo.com/
- 📚 Celery: https://docs.celeryproject.io/
- 📚 MinIO: https://min.io/docs/
- 📚 Docker: https://docs.docker.com/
- 📚 GitHub Actions: https://docs.github.com/en/actions

---

**Version:** 1.0.0  
**Last Updated:** February 2026
