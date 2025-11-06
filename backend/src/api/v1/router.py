"""
API v1 Router
Main router for API version 1
"""
from fastapi import APIRouter
from src.api.v1.endpoints import projects

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}
