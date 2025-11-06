from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.router import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "message": "Construction Project Risk Monitor API",
        "version": settings.VERSION,
        "docs": "/docs"
    }