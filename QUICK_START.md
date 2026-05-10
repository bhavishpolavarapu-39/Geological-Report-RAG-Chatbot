# ⚡ GeoMind AI - Quick Start Guide

## 🎯 In 5 Minutes

### Prerequisites
✅ **Docker Desktop** installed - [Download](https://www.docker.com/products/docker-desktop)

### 3-Step Startup

#### Windows
```batch
# 1. Double-click START_WINDOWS.bat
# 2. Wait for "Services started" message
# 3. Open browser → http://localhost:3000
```

#### Linux/Mac
```bash
# 1. Make startup script executable
chmod +x startup.sh

# 2. Run startup script
./startup.sh

# 3. Open browser → http://localhost:3000
```

#### Manual Docker Compose
```bash
# Build and start all services
docker compose up -d

# Check service health
docker compose ps

# View logs (optional)
docker compose logs -f
```

---

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Chat interface, document upload |
| **API** | http://localhost:8000 | REST API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Database** | http://localhost:5050 | PgAdmin - Manage PostgreSQL |
| **Monitoring** | http://localhost:3001 | Grafana dashboards (admin/admin) |

---

## 🔑 Key Configuration

### API Keys Already Set Up
✅ **Gemini API**: `AIzaSyBlG_GoHsIhB7_nVIpyA8V29Zw9WbFNiwo`

### To Add More LLM Keys
Edit `.env` file:
```bash
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
```

Then restart:
```bash
docker compose restart backend
```

---

## 🧪 Quick Test

### Upload a Geological Document

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer dummy-token" \
  -F "file=@sample_geology_report.pdf"
```

### Query with RAG

```bash
curl -X POST http://localhost:8000/api/v1/rag/retrieve \
  -H "Authorization: Bearer dummy-token" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the copper grades?",
    "top_k": 5,
    "hybrid": true
  }'
```

---

## 📊 What's Running

```
Services Started:
├─ PostgreSQL (Port 5432)      - Vector database with pgvector
├─ Redis (Port 6379)           - Caching & task queue
├─ FastAPI (Port 8000)         - REST API server
├─ Next.js (Port 3000)         - React frontend
├─ Celery Worker               - Async document processing
├─ Celery Beat                 - Scheduled tasks
├─ Nginx (Port 80)             - Reverse proxy
├─ Prometheus (Port 9090)      - Metrics collection
├─ Grafana (Port 3001)         - Monitoring dashboards
└─ pgAdmin (Port 5050)         - Database management

Total: 9 interconnected services
```

---

## 🛑 Common Issues

### Docker not running
**Fix**: Start Docker Desktop and wait 30 seconds before retrying

### Port already in use
**Fix**:
```bash
# List what's using port 3000
netstat -ano | findstr :3000

# Kill process (Windows)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

### Services won't start
**Fix**: Check logs
```bash
docker compose logs backend
docker compose logs frontend
docker compose logs postgres
```

### Out of memory
**Fix**: Increase Docker Desktop memory limit
- Docker Desktop → Settings → Resources → Memory: Set to 8GB+

---

## 📚 Full Documentation

- **Setup Guide**: [SETUP_GUIDE.md](./SETUP_GUIDE.md)
- **Architecture**: [ARCHITECTURE.md](./12_ARCHITECTURE.md)
- **Project README**: [README.md](./11_README.md)
- **Integration Guide**: [INTEGRATION_GUIDE.md](./13_INTEGRATION_GUIDE.md)

---

## 🚀 Next Steps

1. ✅ Services running at http://localhost:3000
2. 📄 Upload a geological report (PDF/DOCX)
3. 🤖 Ask questions via chat interface
4. 📊 View RAG sources and citations
5. 🧠 Run multi-agent analysis

---

## 💡 Pro Tips

### View live logs
```bash
docker compose logs -f backend
```

### Restart a specific service
```bash
docker compose restart backend
```

### Stop all services
```bash
docker compose down
```

### Full clean reset
```bash
docker compose down -v
docker compose up -d
```

### Access database shell
```bash
docker compose exec postgres psql -U geomind_user -d geomind_db
```

---

## 🎓 Learning Resources

- **Gemini API**: https://ai.google.dev/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/docs
- **pgvector**: https://github.com/pgvector/pgvector
- **Docker**: https://docs.docker.com/

---

**You're all set! 🎉 Access the platform at http://localhost:3000**

