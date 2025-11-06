#!/bin/bash

# Validation script for Unix/Linux/Mac

echo "===================================="
echo "Construction AI - Validation Script"
echo "===================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "[1/4] Validating Frontend Build..."
cd frontend
if npm run build > /dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} Frontend builds successfully"
else
    echo -e "${RED}[FAIL]${NC} Frontend build failed"
    echo "Run: cd frontend && npm run build"
fi
cd ..

echo ""
echo "[2/4] Validating Backend Imports..."
cd backend
if python -c "import sys; sys.path.insert(0, '.'); from src.core.config import settings; print('[OK] Backend imports work')" 2>/dev/null; then
    :
else
    echo -e "${RED}[FAIL]${NC} Backend imports failed"
    echo "Run: cd backend && pip install -r requirements.txt"
fi
cd ..

echo ""
echo "[3/4] Checking Docker Services..."
if docker ps | grep -q postgres; then
    echo -e "${GREEN}[OK]${NC} PostgreSQL is running"
else
    echo -e "${YELLOW}[WARN]${NC} PostgreSQL not running"
    echo "Run: npm run docker:up"
fi

echo ""
echo "[4/4] Checking Ports..."
if lsof -i:8000 > /dev/null 2>&1 || netstat -an 2>/dev/null | grep -q :8000; then
    echo -e "${GREEN}[OK]${NC} Backend is running on port 8000"
else
    echo -e "${YELLOW}[INFO]${NC} Backend not running"
fi

if lsof -i:5173 > /dev/null 2>&1 || netstat -an 2>/dev/null | grep -q :5173; then
    echo -e "${GREEN}[OK]${NC} Frontend is running on port 5173"
else
    echo -e "${YELLOW}[INFO]${NC} Frontend not running"
fi

echo ""
echo "===================================="
echo "Validation Complete"
echo "===================================="
