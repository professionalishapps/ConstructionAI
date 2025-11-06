# 🏗️ Construction AI - Start Here

## 👋 Welcome!

This is a real-time AI-powered construction project risk monitoring system.

---

## 🚀 For New Team Members

**Never set this up before?**
👉 **Read this first:** [SETUP_GUIDE.md](SETUP_GUIDE.md) - Complete step-by-step instructions

**Already set up?**
👉 **Use this:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick daily commands

---

## ⚡ Super Quick Start

### Prerequisites
- Node.js 16+ ([Download](https://nodejs.org/))
- Python 3.9+ ([Download](https://www.python.org/downloads/))
- Docker Desktop ([Download](https://www.docker.com/products/docker-desktop/))

### Install & Run
```bash
# 1. Install dependencies
cd frontend && npm install && cd ..
cd backend && pip install -r requirements.txt && cd ..

# 2. Start database
cd infrastructure/docker && docker-compose up -d && cd ../..

# 3. Initialize database (first time only)
cd backend && python scripts/init_db.py && cd ..

# 4. Start backend (in one terminal)
cd backend && python -m uvicorn main:app --reload

# 5. Start frontend (in another terminal)
cd frontend && npm run dev
```

### Access
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Complete setup instructions |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Daily commands cheat sheet |
| [PROJECT_STRUCTURE.txt](PROJECT_STRUCTURE.txt) | Detailed file organization |
| [QUICKSTART.md](QUICKSTART.md) | Alternative quick start |
| [VALIDATION_SUMMARY.md](VALIDATION_SUMMARY.md) | Testing and validation |
| [RESTRUCTURE_CHANGELOG.md](RESTRUCTURE_CHANGELOG.md) | Recent changes log |

### Architecture & Deployment
- [docs/architecture.md](docs/architecture.md) - System architecture
- [docs/deployment.md](docs/deployment.md) - Production deployment

---

## 🎯 What This Project Does

Monitors construction projects in real-time to predict:
- **Cost overruns** 30-90 days in advance
- **Schedule delays** before they happen
- **Risk factors** from weather, supply chain, subcontractors

**Technology:**
- Frontend: React 18 + Vite + Material-UI
- Backend: Python FastAPI
- Database: PostgreSQL
- AI: 14 specialized agents (3 currently implemented)

---

## 🆘 Having Issues?

1. **Check:** [SETUP_GUIDE.md - Troubleshooting Section](SETUP_GUIDE.md#-troubleshooting)
2. **Run validation:** `scripts\validate.bat` (Windows) or `./scripts/validate.sh` (Mac/Linux)
3. **Common issues:**
   - "uvicorn not found" → Run `pip install -r requirements.txt`
   - "Connection refused" → Start the backend server
   - Port in use → Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for how to kill processes

---

## 📂 Project Structure

```
ConstructionAI/
├── frontend/              React dashboard
├── backend/               Python FastAPI + AI agents
├── infrastructure/        Docker configs
├── docs/                  Documentation
└── scripts/               Helper scripts
```

---

## 🔄 For Team Members Pulling Updates

```bash
git pull
cd frontend && npm install && cd ..
cd backend && pip install -r requirements.txt && cd ..
# Restart services
```

---

**Need more help?** → [SETUP_GUIDE.md](SETUP_GUIDE.md)

**Ready to code?** → [PROJECT_STRUCTURE.txt](PROJECT_STRUCTURE.txt)
