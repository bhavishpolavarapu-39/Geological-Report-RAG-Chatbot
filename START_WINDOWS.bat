@echo off
REM GeoMind AI - Windows Startup Script

setlocal enabledelayedexpansion

echo.
echo ====================================================================
echo  GeoMind AI - Geological Intelligence Platform
echo ====================================================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH
    echo.
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo [OK] Docker is installed
echo.

REM Check if Docker daemon is running
docker info >nul 2>nul
if errorlevel 1 (
    echo [WARNING] Docker daemon is not running
    echo.
    echo Please start Docker Desktop and try again
    echo.
    pause
    exit /b 1
)

echo [OK] Docker daemon is running
echo.

REM Check .env file
if not exist .env (
    echo [WARNING] .env file not found
    echo Creating .env with defaults...
) else (
    echo [OK] .env file found
)

echo.
echo ====================================================================
echo  Starting Services
echo ====================================================================
echo.

REM Build and start services
echo Building Docker images...
docker compose build --no-cache

if errorlevel 1 (
    echo [ERROR] Failed to build Docker images
    pause
    exit /b 1
)

echo.
echo Starting services...
docker compose up -d

if errorlevel 1 (
    echo [ERROR] Failed to start services
    echo.
    echo Try running: docker compose logs
    pause
    exit /b 1
)

echo.
echo [OK] Services started
echo.

REM Wait for services
echo Waiting for services to be ready...
timeout /t 15 /nobreak

echo.
echo ====================================================================
echo  Service Status
echo ====================================================================
echo.

docker compose ps

echo.
echo ====================================================================
echo  Access Points
echo ====================================================================
echo.
echo Frontend:       http://localhost:3000
echo Backend API:    http://localhost:8000
echo API Docs:       http://localhost:8000/docs
echo Database Mgmt:  http://localhost:5050
echo Monitoring:     http://localhost:3001
echo.

echo ====================================================================
echo  Useful Commands
echo ====================================================================
echo.
echo View logs:        docker compose logs -f
echo View backend:     docker compose logs -f backend
echo View frontend:    docker compose logs -f frontend
echo Stop services:    docker compose down
echo Restart service:  docker compose restart ^<service-name^>
echo.

echo [SUCCESS] GeoMind AI is running!
echo.
echo Open your browser and go to: http://localhost:3000
echo.

REM Keep window open
pause
