# Complete Setup Guide - Construction AI

## 📋 Prerequisites (Install These First)

### 1. Install Node.js and npm
- Download from: https://nodejs.org/
- **Version:** 16.0.0 or higher
- Verify installation:
  ```bash
  node --version
  npm --version
  ```

### 2. Install Python
- Download from: https://www.python.org/downloads/
- **Version:** 3.9 or higher
- ⚠️ **IMPORTANT:** Check "Add Python to PATH" during installation
- Verify installation:
  ```bash
  python --version
  pip --version
  ```

### 3. Install Docker Desktop
- Download from: https://www.docker.com/products/docker-desktop/
- Start Docker Desktop and make sure it's running
- Verify installation:
  ```bash
  docker --version
  docker-compose --version
  ```

### 4. Install Git (if not already installed)
- Download from: https://git-scm.com/downloads
- Verify installation:
  ```bash
  git --version
  ```

---

## 🚀 Initial Setup (First Time Only)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd ConstructionAI
```

### Step 2: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### Step 3: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
cd ..
```

### Step 4: Start Docker Services (Database)
```bash
cd infrastructure/docker
docker-compose up -d
cd ../..
```

Wait 5-10 seconds for PostgreSQL to fully start.

### Step 5: Initialize the Database
```bash
cd backend
python scripts/init_db.py
cd ..
```

---

## ▶️ Running the Application (Every Time)

### Option 1: Using Scripts (Easiest - Windows Only)

**Start everything:**
```cmd
scripts\start-dev.bat
```

This will open:
- Backend server at http://localhost:8000
- Frontend at http://localhost:5173

---

### Option 2: Manual Start (Works on All Platforms)

You'll need **3 separate terminal windows**:

#### Terminal 1: Start Docker (if not already running)
```bash
cd infrastructure/docker
docker-compose up -d
```

#### Terminal 2: Start Backend
```bash
cd backend
python -m uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

#### Terminal 3: Start Frontend
```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.0.11  ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

---

### Option 3: From Root Directory (Using npm)

```bash
# Start both frontend and backend
npm run dev:all

# Or start individually:
npm run dev              # Frontend only
npm run dev:backend      # Backend only
```

---

## 🌐 Access the Application

Once everything is running:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main dashboard |
| **Backend API** | http://localhost:8000 | API server |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **PostgreSQL** | localhost:5432 | Database (internal) |

---

## 🛑 Stopping the Application

### Stop Frontend/Backend
Press `Ctrl+C` in each terminal window

### Stop Docker Services
```bash
cd infrastructure/docker
docker-compose down
```

Or from root:
```bash
npm run docker:down
```

---

## 🔧 Troubleshooting

### "uvicorn: command not found" or "uvicorn is not recognized"

**Solution:** Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

---

### "npm: command not found"

**Solution:** Install Node.js from https://nodejs.org/

---

### "python: command not found"

**Solution:** Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation
- Restart your terminal after installation

---

### Frontend shows "Connection Refused" errors

**Problem:** Backend is not running

**Solution:** Start the backend server:
```bash
cd backend
python -m uvicorn main:app --reload
```

---

### Backend error: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:** Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

---

### Database connection errors

**Problem:** PostgreSQL is not running

**Solution:** Start Docker services:
```bash
cd infrastructure/docker
docker-compose up -d
```

Wait 5-10 seconds, then try starting the backend again.

---

### Port already in use (8000 or 5173)

**Find what's using the port:**

**Windows:**
```bash
# Find process on port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Find and kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

---

### Browser shows blank page or old errors

**Solution:** Clear browser cache
1. Open browser DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

Or press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

---

### Docker Desktop not starting

**Solution:**
1. Make sure you have virtualization enabled in BIOS
2. On Windows: Enable WSL 2
3. Restart Docker Desktop
4. Restart your computer if needed

---

## 📁 Project Structure Quick Reference

```
ConstructionAI/
├── frontend/           # React application
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── styles/
│   └── package.json
│
├── backend/            # Python FastAPI
│   ├── src/
│   │   ├── agents/
│   │   ├── api/
│   │   ├── database/
│   │   └── core/
│   └── requirements.txt
│
├── infrastructure/
│   └── docker/
│       └── docker-compose.yml
│
└── scripts/            # Helper scripts
```

---

## 🔄 Pulling Updates

When you pull new changes from Git:

```bash
# Pull latest code
git pull

# Reinstall dependencies (if package.json or requirements.txt changed)
cd frontend
npm install
cd ../backend
pip install -r requirements.txt

# Restart services
# Stop everything (Ctrl+C in terminals)
# Then start again using the steps above
```

---

## ✅ Quick Start Checklist

- [ ] Node.js installed (node --version works)
- [ ] Python installed (python --version works)
- [ ] Docker Desktop installed and running
- [ ] Repository cloned
- [ ] Frontend dependencies installed (npm install in frontend/)
- [ ] Backend dependencies installed (pip install in backend/)
- [ ] Docker services started (docker-compose up -d)
- [ ] Database initialized (python scripts/init_db.py)
- [ ] Backend running (python -m uvicorn main:app --reload)
- [ ] Frontend running (npm run dev)
- [ ] Browser opens http://localhost:5173
- [ ] Dashboard loads without errors

---

## 📞 Getting Help

1. **Check the logs** - Look for error messages in the terminal
2. **Check this troubleshooting section** - Common issues listed above
3. **Verify all services are running:**
   ```bash
   docker ps              # Should show PostgreSQL and Redis
   ```
4. **Run validation script:**
   ```bash
   scripts\validate.bat   # Windows
   ./scripts/validate.sh  # Mac/Linux
   ```

---

## 🎯 Common Development Workflow

```bash
# Morning - Start working
cd ConstructionAI
cd infrastructure/docker && docker-compose up -d && cd ../..
cd backend && python -m uvicorn main:app --reload

# In another terminal
cd frontend && npm run dev

# Work on your code...

# Evening - Stop working
# Ctrl+C in both terminals
cd infrastructure/docker && docker-compose down
```

---

## 📚 Additional Documentation

- [PROJECT_STRUCTURE.txt](PROJECT_STRUCTURE.txt) - Detailed file structure
- [QUICKSTART.md](QUICKSTART.md) - Quick reference guide
- [VALIDATION_SUMMARY.md](VALIDATION_SUMMARY.md) - Validation and testing
- [docs/architecture.md](docs/architecture.md) - System architecture
- [docs/deployment.md](docs/deployment.md) - Deployment guide

---

**Last Updated:** 2025-11-05
**Status:** ✅ Tested and working
