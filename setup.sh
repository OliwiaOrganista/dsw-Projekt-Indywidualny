#!/bin/bash
set -e

echo "🚀 Cloud File Ingestor - Setup Script"
echo "======================================"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi
echo "✅ Docker found"

# Check docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed"
    exit 1
fi
echo "✅ docker-compose found"

# Build images
echo ""
echo "📦 Building Docker images..."
docker-compose build

# Start services
echo ""
echo "🔧 Starting services..."
docker-compose up -d

# Wait for DB
echo ""
echo "⏳ Waiting for database..."
sleep 10

# Check health
echo ""
echo "🏥 Checking health..."
docker-compose exec -T api curl -f http://localhost:8000/health || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "📍 Services:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - MinIO: http://localhost:9001 (minioadmin/minioadmin)"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo ""
echo "🧪 Test upload:"
echo "  curl -X POST -F 'file=@test.csv' http://localhost:8000/files"
