# Quick Reference Card

## ⚡ Daily Startup (3 Steps)

### 1. Start Docker
```bash
cd infrastructure/docker
docker-compose up -d
```

### 2. Start Backend
```bash
cd backend
python -m uvicorn main:app --reload
```

### 3. Start Frontend
```bash
cd frontend
npm run dev
```

**Then open:** http://localhost:5173

---

## 🛑 Shutdown

```bash
# Stop frontend/backend: Ctrl+C in terminals
# Stop Docker:
cd infrastructure/docker
docker-compose down
```

---

## 🔧 First Time Setup

```bash
# Install dependencies
cd frontend && npm install && cd ..
cd backend && pip install -r requirements.txt && cd ..

# Start database
cd infrastructure/docker && docker-compose up -d && cd ../..

# Initialize database
cd backend && python scripts/init_db.py && cd ..
```

---

## 📍 URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## 🆘 Common Fixes

**Backend won't start:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend errors:**
```bash
cd frontend
npm install
# Clear cache: Ctrl+Shift+R in browser
```

**Database connection failed:**
```bash
cd infrastructure/docker
docker-compose down
docker-compose up -d
# Wait 10 seconds
```

---

**Full Guide:** [SETUP_GUIDE.md](SETUP_GUIDE.md)
