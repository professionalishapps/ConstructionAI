# Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- **Node.js** 16+ and npm 8+
- **Python** 3.9+
- **Docker** and Docker Compose
- **Git**

---

## 📦 Installation

### Option 1: Automated Setup (Recommended)

**Windows:**
```cmd
scripts\setup.bat
```

**Unix/Linux/Mac:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Option 2: Manual Setup

1. **Install dependencies from root:**
```bash
npm run install:all
```

2. **Or install separately:**
```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
pip install -r requirements.txt
```

3. **Start Docker services:**
```bash
npm run docker:up
# or
cd infrastructure/docker
docker-compose up -d
```

4. **Initialize database:**
```bash
cd backend
python scripts/init_db.py
```

---

## 🏃 Running the Application

### Option 1: From Root Directory (Easiest)

```bash
# Start everything (frontend + backend)
npm run dev:all

# Or start individually:
npm run dev              # Frontend only
npm run dev:frontend     # Frontend only (explicit)
npm run dev:backend      # Backend only
```

### Option 2: Using Scripts

**Windows:**
```cmd
scripts\start-dev.bat
```

**Unix/Linux/Mac:**
```bash
./scripts/start-dev.sh
```

### Option 3: Manual Start (Classic)

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## 🌐 Access Points

Once running, access the application at:

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **PostgreSQL** | localhost:5432 |
| **Redis** | localhost:6379 |

---

## 🛠️ Useful Commands

### Root-level Commands

```bash
# Development
npm run dev:all          # Start frontend + backend
npm run dev              # Start frontend only
npm run dev:backend      # Start backend only

# Building
npm run build            # Build frontend for production

# Testing
npm run test:frontend    # Run frontend tests
npm run test:backend     # Run backend tests

# Docker
npm run docker:up        # Start Docker services
npm run docker:down      # Stop Docker services

# Linting
npm run lint:frontend    # Lint frontend code
```

### Frontend-specific

```bash
cd frontend

npm run dev              # Development server
npm run build            # Production build
npm run preview          # Preview production build
npm run lint             # ESLint check
```

### Backend-specific

```bash
cd backend

# Development
uvicorn main:app --reload

# Testing
pytest                   # Run all tests
pytest -v               # Verbose output
pytest tests/unit       # Run unit tests only

# Database
python scripts/init_db.py         # Initialize database
python scripts/seed_data.py       # Seed test data (TODO)

# Code quality
black .                  # Format code
flake8                   # Lint code
mypy .                   # Type checking
```

---

## 📁 Project Structure

```
ConstructionAI/
├── frontend/           # React app (npm workspace)
├── backend/            # FastAPI app
├── infrastructure/     # Docker, K8s, Terraform
├── docs/              # Documentation
├── scripts/           # Helper scripts
└── package.json       # Root package (workspaces)
```

**Key Point:** The `node_modules` stays in `frontend/` where it belongs, but you can run all commands from the root using npm workspaces!

---

## 🐛 Troubleshooting

### Port already in use
```bash
# Backend (8000)
lsof -ti:8000 | xargs kill -9  # Unix
netstat -ano | findstr :8000   # Windows (find PID, then kill)

# Frontend (5173)
lsof -ti:5173 | xargs kill -9  # Unix
```

### Database connection errors
```bash
# Restart Docker services
npm run docker:down
npm run docker:up

# Wait 5 seconds, then reinitialize
cd backend
python scripts/init_db.py
```

### Module not found errors (Backend)
```bash
# Make sure you're in the backend directory
cd backend
pip install -r requirements.txt

# Or install dev dependencies
pip install -r requirements-dev.txt
```

### Cannot find module errors (Frontend)
```bash
# From root
npm run install:frontend

# Or from frontend directory
cd frontend
npm install
```

---

## 🔄 Development Workflow

1. **Make changes** to code
2. **Hot reload** - Both frontend (Vite) and backend (--reload) auto-refresh
3. **Check logs** in terminal
4. **Test** - Run tests before committing
5. **Commit** - Make clean commits

---

## 📚 Next Steps

- Read [docs/architecture.md](docs/architecture.md) for system overview
- Read [docs/deployment.md](docs/deployment.md) for production deployment
- Check [PROJECT_STRUCTURE.txt](PROJECT_STRUCTURE.txt) for detailed file organization

---

## 💡 Tips

- **Work from root**: All npm commands work from project root
- **Use workspaces**: `npm run <script> --workspace=frontend`
- **Backend needs `cd`**: Python commands need to be run from `backend/`
- **Database persistence**: Docker volumes persist data between restarts
- **API exploration**: Use http://localhost:8000/docs for interactive API testing

---

## ✅ Checklist

Before you start developing:

- [ ] Docker is running
- [ ] PostgreSQL is accessible (port 5432)
- [ ] Backend starts without errors
- [ ] Frontend loads at localhost:5173
- [ ] Can access API docs at localhost:8000/docs
- [ ] Database has sample data

Happy coding! 🎉
