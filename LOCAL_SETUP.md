# 🚀 Local Development Setup (No Docker Required)

Run GeoMind AI locally on Windows without Docker.

## Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 16** - [Download](https://www.postgresql.org/download/windows/)
- **Redis** - [Download](https://github.com/microsoftarchive/redis/releases) (or use Windows Subsystem for Linux)

---

## Step 1: Install Python Dependencies

```powershell
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI installed')"
```

---

## Step 2: Setup PostgreSQL Database

### Windows Installation

```powershell
# 1. Download PostgreSQL installer from https://www.postgresql.org/download/windows/
# 2. Run installer with these settings:
#    - Password: geomind_secure_password (or your choice)
#    - Port: 5432
#    - Default locale

# 3. After installation, open PostgreSQL Command Line (psql)
psql -U postgres

# 4. Create GeoMind database
CREATE DATABASE geomind_db;
CREATE USER geomind_user WITH PASSWORD 'geomind_secure_password';
GRANT ALL PRIVILEGES ON DATABASE geomind_db TO geomind_user;

# 5. Install pgvector extension
\c geomind_db
CREATE EXTENSION IF NOT EXISTS vector;

# 6. Exit psql
\q
```

---

## Step 3: Setup Redis

### Option A: Windows Native Redis

```powershell
# Download from: https://github.com/microsoftarchive/redis/releases
# Run: msi-redis-x64-3.0.504.msi
# Install to default location

# Start Redis (after installation, it runs as Windows service)
# Verify
redis-cli ping
# Should respond with: PONG
```

### Option B: WSL2 (Easier)

```powershell
# In WSL2 terminal
wsl

# Install Redis in Ubuntu
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
redis-server

# In another WSL terminal, verify
redis-cli ping
```

---

## Step 4: Install Node Dependencies

```powershell
# Navigate to frontend folder
cd frontend

# Install Node packages
npm install

# Verify
npm --version
node --version
```

---

## Step 5: Configure Environment

Create `.env.local` in project root:

```env
# Database
DATABASE_URL=postgresql://geomind_user:geomind_secure_password@localhost:5432/geomind_db

# Redis
REDIS_URL=redis://localhost:6379

# Gemini API
GEMINI_API_KEY=AIzaSyBlG_GoHsIhB7_nVIpyA8V29Zw9WbFNiwo

# JWT
JWT_SECRET_KEY=geomind-local-dev-key-change-in-production

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Logging
LOG_LEVEL=debug
```

---

## Step 6: Start Backend

### Terminal 1: Backend Server

```powershell
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start FastAPI server
python -m uvicorn main:app --reload --port 8000 --host 0.0.0.0

# Expected output:
# Uvicorn running on http://127.0.0.1:8000
# Application startup complete
```

---

## Step 7: Start Frontend

### Terminal 2: Frontend Server

```powershell
cd frontend

# Start Next.js dev server
npm run dev

# Expected output:
# ▲ Next.js 15.0.0
# - Local: http://localhost:3000
# - Environments: .env.local
```

---

## Step 8: Access the Platform

Open your browser:

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |

---

## Troubleshooting

### PostgreSQL Connection Error

```powershell
# Check if PostgreSQL is running
psql -U geomind_user -d geomind_db

# If connection refused:
# 1. Open Services (services.msc)
# 2. Find "postgresql-x64-16"
# 3. Right-click → Start

# Or restart PostgreSQL
net stop postgresql-x64-16
net start postgresql-x64-16
```

### Redis Connection Error

```powershell
# Check if Redis is running
redis-cli ping

# If connection refused:
# 1. Open Services (services.msc)
# 2. Find "Redis"
# 3. Right-click → Start

# Or run Redis manually
cd "C:\Program Files\Redis"
redis-server.exe
```

### Port Already in Use

```powershell
# Find what's using port 3000
netstat -ano | findstr :3000

# Kill the process (get PID from above)
taskkill /PID <PID> /F

# Or change port in startup command
python -m uvicorn main:app --port 8001
npm run dev -- -p 3001
```

### Module Not Found Error

```powershell
# Ensure virtual environment is activated
# Should see (venv) at start of prompt

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## Testing the API

### Upload Document

```powershell
# Using curl or Postman
curl -X POST http://localhost:8000/api/v1/documents/upload `
  -H "Authorization: Bearer dummy-token" `
  -F "file=@sample.pdf"
```

### RAG Query

```powershell
$body = @{
    query = "What are the copper grades?"
    top_k = 5
    hybrid = $true
} | ConvertTo-Json

curl -X POST http://localhost:8000/api/v1/rag/retrieve `
  -H "Authorization: Bearer dummy-token" `
  -H "Content-Type: application/json" `
  -Body $body
```

---

## Useful Commands

```powershell
# Stop all servers: Ctrl + C in each terminal

# Restart backend
# (In backend terminal)
# Ctrl + C
# python -m uvicorn main:app --reload --port 8000

# Restart frontend
# (In frontend terminal)
# Ctrl + C
# npm run dev

# View database
psql -U geomind_user -d geomind_db

# View Redis
redis-cli

# Check running processes
Get-Process | Where-Object {$_.Name -like "*python*" -or $_.Name -like "*node*"}
```

---

## Full Development Workflow

```powershell
# Terminal 1: Start PostgreSQL
# Services → postgresql-x64-16 → Start (or already running)

# Terminal 2: Start Redis
redis-server
# or Services → Redis → Start

# Terminal 3: Start Backend
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --port 8000

# Terminal 4: Start Frontend
cd frontend
npm run dev

# Browser
# Open http://localhost:3000
```

---

## Next Steps

1. ✅ Set up Python virtual environment
2. ✅ Create PostgreSQL database
3. ✅ Install Redis
4. ✅ Install Node packages
5. ✅ Configure .env.local
6. ✅ Start backend (Terminal 1)
7. ✅ Start frontend (Terminal 2)
8. ✅ Access http://localhost:3000
9. ✅ Upload geological report
10. ✅ Ask questions via chat

---

**GeoMind AI is now running locally without Docker!**

