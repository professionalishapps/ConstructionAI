# Deployment Guide

## Local Development

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- Ollama (optional)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration

# Start database
cd ../infrastructure/docker
docker-compose up -d

# Run migrations
cd ../../backend
python scripts/init_db.py

# Start server
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Production Deployment

### Using Docker

```bash
# Build images
docker build -t construction-ai-backend -f infrastructure/docker/Dockerfile.backend .
docker build -t construction-ai-frontend -f infrastructure/docker/Dockerfile.frontend .

# Run with docker-compose
cd infrastructure/docker
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

See `.env.example` files in backend and frontend directories.

### Database Migrations

Use Alembic for database migrations:

```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```
