@echo off
setlocal enabledelayedexpansion

echo 🚀 Cloud File Ingestor - Setup Script (Windows)
echo ==============================================

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed
    exit /b 1
)
echo ✅ Docker found

REM Check docker-compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ docker-compose is not installed
    exit /b 1
)
echo ✅ docker-compose found

REM Build images
echo.
echo 📦 Building Docker images...
docker-compose build

REM Start services
echo.
echo 🔧 Starting services...
docker-compose up -d

REM Wait for DB
echo.
echo ⏳ Waiting for database...
timeout /t 15 /nobreak

REM Check health
echo.
echo 🏥 Checking health...
curl http://localhost:8000/health

echo.
echo ✅ Setup complete!
echo.
echo 📍 Services:
echo   - API: http://localhost:8000
echo   - Docs: http://localhost:8000/docs
echo   - MinIO: http://localhost:9001 (minioadmin/minioadmin)
echo   - PostgreSQL: localhost:5432
echo   - Redis: localhost:6379
echo.
echo 🧪 Test upload:
echo   curl -X POST -F "file=@test.csv" http://localhost:8000/files
