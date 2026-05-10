# 🚀 GeoMind AI - Setup & Deployment Guide

## Quick Start

### Prerequisites
- **Docker Desktop** (v4.0+) - [Download](https://www.docker.com/products/docker-desktop)
- **Docker Compose** (included with Docker Desktop)
- **Git** (for cloning)
- **System Requirements**: 8GB RAM minimum, 20GB disk space

### Step 1: Verify Docker Installation

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker compose version

# Verify Docker is running
docker info
```

### Step 2: Clone/Setup Project

```bash
cd /path/to/Geological-Report-RAG-Chatbot
```

### Step 3: Configure Environment

The `.env` file is already created with:
```
GEMINI_API_KEY=AIzaSyBlG_GoHsIhB7_nVIpyA8V29Zw9WbFNiwo
```

Add additional API keys if needed:
```bash
# Edit .env file
# Optional: Add OpenAI and Anthropic keys
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 4: Start Services

#### Option A: Using Docker Compose (Recommended)

```bash
# Start all services
docker compose up -d

# Monitor logs
docker compose logs -f

# Stop all services
docker compose down
```

#### Option B: Using Startup Script (Linux/Mac)

```bash
# Make script executable
chmod +x startup.sh

# Run startup script
./startup.sh
```

### Step 5: Access the Platform

Once services are healthy, access:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database Admin**: http://localhost:5050 (pgAdmin)
- **Monitoring**: http://localhost:3001 (Grafana)

---

## Services Overview

### 1. PostgreSQL + pgvector (Port 5432)
- Vector database for semantic search
- Credentials: `geomind_user` / `geomind_secure_password`
- Database: `geomind_db`

### 2. Redis (Port 6379)
- Caching layer
- Task queue backend

### 3. FastAPI Backend (Port 8000)
- REST API server
- WebSocket support
- Automatically starts with `uvicorn`

### 4. Next.js Frontend (Port 3000)
- React 18 + TypeScript
- Production build

### 5. Nginx (Port 80)
- Reverse proxy
- Load balancer
- SSL termination (optional)

### 6. Celery Worker
- Async task processing
- Document ingestion
- Background jobs

### 7. Celery Beat
- Scheduled tasks
- Periodic operations

### 8. Prometheus (Port 9090)
- Metrics collection
- Monitoring

### 9. Grafana (Port 3001)
- Visualization dashboards
- Alerts

---

## Common Commands

### Docker Compose Commands

```bash
# Start services in background
docker compose up -d

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v

# Rebuild images
docker compose build --no-cache

# Run single service
docker compose up backend

# Access container shell
docker compose exec backend bash
```

### Database Management

```bash
# Access PostgreSQL
docker compose exec postgres psql -U geomind_user -d geomind_db

# View Redis data
docker compose exec redis redis-cli

# Database backup
docker compose exec postgres pg_dump -U geomind_user geomind_db > backup.sql

# Database restore
docker compose exec -T postgres psql -U geomind_user geomind_db < backup.sql
```

### API Testing

```bash
# Upload a document
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@sample.pdf"

# Retrieve documents
curl http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer YOUR_TOKEN"

# RAG retrieval
curl -X POST http://localhost:8000/api/v1/rag/retrieve \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the copper grades?",
    "top_k": 5,
    "hybrid": true
  }'
```

---

## Troubleshooting

### Docker daemon not running
**Error**: `Docker daemon is not running`
**Solution**: Start Docker Desktop

### Port already in use
**Error**: `Error starting userland proxy: listen tcp 0.0.0.0:3000: bind: address already in use`
**Solution**:
```bash
# Find process using port
lsof -i :3000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Out of disk space
**Solution**:
```bash
# Clean up Docker
docker system prune -a --volumes

# Remove unused images
docker image prune -a

# Remove unused containers
docker container prune
```

### Database connection error
**Solution**:
```bash
# Check PostgreSQL is healthy
docker compose exec postgres pg_isready -U geomind_user

# Restart database
docker compose restart postgres
```

### Frontend not loading
**Solution**:
```bash
# Check frontend logs
docker compose logs frontend

# Rebuild frontend
docker compose up -d --build frontend
```

---

## Environment Variables

Key variables in `.env`:

```bash
# API Keys
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Database
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/db
REDIS_URL=redis://redis:6379

# JWT
JWT_SECRET_KEY=your-secret-key

# Frontend
NEXT_PUBLIC_API_URL=http://backend:8000/api/v1
```

---

## Production Deployment

### Docker Stack Deployment
```bash
# Deploy to Docker Swarm
docker stack deploy -c docker-compose.yml geomind
```

### Kubernetes Deployment
```bash
# Create ConfigMap
kubectl create configmap geomind-config --from-env-file=.env

# Deploy
kubectl apply -f k8s/deployment.yaml
```

### AWS Deployment
1. Push images to ECR
2. Deploy with ECS/EKS
3. Use RDS for PostgreSQL
4. Use ElastiCache for Redis
5. Use ALB for load balancing

---

## Monitoring & Logging

### Prometheus Metrics
Access: http://localhost:9090

**Common queries:**
```
# API response time
http_request_duration_seconds

# Request count
http_requests_total

# Error rate
rate(http_requests_total{status=~"5.."}[5m])
```

### Grafana Dashboards
Access: http://localhost:3001 (admin/admin)

**Pre-configured dashboards:**
- API Performance
- Database Metrics
- System Resource Usage
- Error Tracking

### Centralized Logging
Logs are available via:
- Docker: `docker compose logs`
- Application: `/app/logs/` (inside container)
- Volumes: `./logs/` (host machine)

---

## Development Workflow

### Local Development (Without Docker)

```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Install Node dependencies
cd frontend && npm install

# Run backend
uvicorn backend.main:app --reload

# Run frontend (in separate terminal)
cd frontend && npm run dev
```

### Code Structure
```
.
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── rag_pipeline_core.py       # RAG engine
│   ├── document_ingestion.py      # Document processing
│   ├── multi_agent_orchestration.py
│   └── requirements.txt
├── frontend/
│   ├── pages/
│   ├── components/
│   ├── package.json
│   └── next.config.js
├── docker-compose.yml
├── .env
└── README.md
```

---

## Next Steps

1. ✅ Start services: `docker compose up -d`
2. ✅ Verify health: `docker compose ps`
3. ✅ Access frontend: http://localhost:3000
4. ✅ Upload test document
5. ✅ Run RAG query
6. ✅ Monitor in Grafana

---

## Support & Documentation

- **API Docs**: http://localhost:8000/docs
- **Project README**: [README.md](./11_README.md)
- **Architecture**: [ARCHITECTURE.md](./12_ARCHITECTURE.md)
- **Integration Guide**: [INTEGRATION_GUIDE.md](./13_INTEGRATION_GUIDE.md)

---

**Happy exploring! 🎯**
