# 🪟 Windows 11 Home - Docker Desktop Fix

## Issue: WSL2 Docker Engine Not Responding

This is a common issue on Windows 11 Home with Docker Desktop's WSL2 backend.

---

## Solution: Reset WSL2 and Docker

### **Method 1: Full Docker Reset (Recommended)**

**Step 1: Close Docker Desktop**
```
1. Right-click Docker icon in taskbar
2. Click "Quit Docker Desktop"
3. Wait 30 seconds
```

**Step 2: Reset Docker**
```
1. Open Windows Settings (Win + I)
2. Go to: Apps → Apps & Features
3. Find "Docker Desktop"
4. Click it, then click "Uninstall"
5. Click "Uninstall" again to confirm
6. Wait for uninstall to complete
```

**Step 3: Reinstall Docker**
```
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Run the installer
3. Accept all defaults
4. Restart Windows when prompted
```

**Step 4: Verify**
```powershell
# Open PowerShell as Administrator
docker ps
# Should show empty output (no errors)
```

---

### **Method 2: Reset WSL2 Without Uninstalling Docker**

**Step 1: Close Docker**
```
Right-click Docker icon → Quit Docker Desktop
Wait 1 minute
```

**Step 2: Reset WSL**
```powershell
# Open PowerShell as Administrator

# Shutdown WSL
wsl --shutdown

# Wait 10 seconds

# Restart Docker Desktop
# (Double-click Docker Desktop app)

# Wait 2-3 minutes for full startup
```

**Step 3: Verify**
```powershell
# Open new PowerShell
docker ps
```

---

### **Method 3: Enable Required Windows Features**

**Step 1: Open Windows Features**
```powershell
# Run as Administrator
optionalfeatures
```

**Step 2: Enable:**
- ✓ Hyper-V
- ✓ Virtual Machine Platform
- ✓ Windows Subsystem for Linux

**Step 3: Restart Windows**

**Step 4: Update WSL**
```powershell
# Open PowerShell as Administrator
wsl --update
wsl --update --pre-release
wsl --set-default-version 2
```

---

## Verification Checklist

After applying fixes, verify each step:

```powershell
# 1. Check Docker is installed
docker --version
# Expected: Docker version 20.10+

# 2. Check Docker Compose
docker compose version
# Expected: Docker Compose version 2.0+

# 3. Check Docker daemon
docker ps
# Expected: Empty list, no errors

# 4. Test Docker
docker run hello-world
# Expected: Hello from Docker!

# 5. Check WSL
wsl --list --verbose
# Expected: Ubuntu or similar with VERSION 2
```

---

## Alternative: Run Services Manually

If Docker still won't work, run the backend and frontend locally:

**Terminal 1: Start Backend**
```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2: Start Frontend**
```powershell
cd frontend
npm install
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

---

## Advanced: Docker Logs

If Docker still fails, check the logs:

```powershell
# Get Docker daemon info
docker info

# Check Docker Desktop logs
# Location: C:\Users\{YourUsername}\AppData\Local\Docker\log

# View in PowerShell
Get-Content "C:\Users\kinki\AppData\Local\Docker\log\host.log" -Tail 50
```

---

## If All Else Fails

**Option 1: Use Windows Subsystem for Linux (WSL2) Directly**
```bash
# Install WSL2 with Ubuntu
wsl --install -d Ubuntu

# Open Ubuntu
wsl

# Install Docker in Ubuntu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Run Docker Compose
cd /mnt/c/Users/kinki/Downloads/RAG\ geology\ report\ chatbot
docker compose up -d
```

**Option 2: Use Alternative Container Tool (Podman)**
```powershell
# Download Podman
# https://podman-desktop.io/downloads

# Or via PowerShell
winget install containers.podman

# Use same docker compose commands
# (Podman is Docker-compatible)
```

---

## System Requirements Check

```powershell
# Open Settings → About
# Check:
- Windows 11 (build 22000+)
- Processor: Intel/AMD with virtualization enabled
- RAM: 8GB minimum (16GB recommended)
- Storage: 20GB free

# Enable Virtualization in BIOS (if needed)
# Restart computer → Press Del/F12 during startup
# Find "Virtualization" or "VT-x" and enable
```

---

## Contact Support

If issues persist:
1. Check Docker Desktop system requirements
2. Review Docker logs at: `C:\Users\{username}\AppData\Local\Docker\log`
3. Visit: https://docs.docker.com/desktop/troubleshoot/
4. Open Docker support issue

---

## Quick Command Reference

```powershell
# Restart Docker
Restart-Service Docker

# Stop Docker
Stop-Service Docker

# Start Docker
Start-Service Docker

# Check Docker processes
Get-Process | Where-Object {$_.Name -like "*docker*"}

# List Docker containers
docker ps -a

# Remove all containers
docker system prune -a

# View Docker resource usage
docker stats
```

---

**Once Docker is working, run:**
```powershell
cd "C:\Users\kinki\Downloads\RAG geology report chatbot"
docker compose up -d
```

