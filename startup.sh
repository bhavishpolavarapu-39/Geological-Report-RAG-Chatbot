#!/bin/bash

# GeoMind AI - Project Startup Script

set -e

echo "🚀 Starting GeoMind AI Platform..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    echo "   Windows: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is installed and running"
echo ""

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  Using docker compose (v2) instead of docker-compose"
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Load environment variables
if [ -f .env ]; then
    echo "✅ Loaded environment variables from .env"
else
    echo "⚠️  .env file not found. Using defaults."
fi

echo ""
echo "📦 Building and starting services..."
echo ""

# Build images
$COMPOSE_CMD build --no-cache

# Start services
$COMPOSE_CMD up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo ""
echo "🏥 Service Health Status:"
echo ""

if $COMPOSE_CMD ps | grep -q "geomind_postgres.*healthy"; then
    echo "✅ PostgreSQL: Running"
else
    echo "⚠️  PostgreSQL: Starting/Unhealthy"
fi

if $COMPOSE_CMD ps | grep -q "geomind_redis"; then
    echo "✅ Redis: Running"
else
    echo "⚠️  Redis: Not running"
fi

if $COMPOSE_CMD ps | grep -q "geomind_backend"; then
    echo "✅ Backend API: Running"
else
    echo "⚠️  Backend API: Not running"
fi

if $COMPOSE_CMD ps | grep -q "geomind_frontend"; then
    echo "✅ Frontend: Running"
else
    echo "⚠️  Frontend: Not running"
fi

echo ""
echo "🌐 Service URLs:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Nginx:        http://localhost:80"
echo "   Prometheus:   http://localhost:9090"
echo "   Grafana:      http://localhost:3001 (admin/admin)"
echo "   PgAdmin:      http://localhost:5050 (admin@geomind.local/admin)"
echo ""

echo "📝 Logs:"
echo "   View all logs:    $COMPOSE_CMD logs -f"
echo "   Backend logs:     $COMPOSE_CMD logs -f backend"
echo "   Frontend logs:    $COMPOSE_CMD logs -f frontend"
echo ""

echo "🛑 To stop services: $COMPOSE_CMD down"
echo ""
echo "✨ GeoMind AI is ready! Access the platform at http://localhost:3000"
