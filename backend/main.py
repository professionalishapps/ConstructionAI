from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from api.routes_full import router as full_router
from api.routes_input import router as input_router

app = FastAPI(
    title="Construction Project Risk Monitor API",
    description="14-Agent AI System for Construction Risk Analysis",
    version="1.0.0"
)

# Configure CORS - allow both localhost forms used by dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include both routers
app.include_router(api_router)
app.include_router(full_router)
app.include_router(input_router)


@app.get("/")
async def root():
    return {
        "message": "Construction Project Risk Monitor API",
        "version": "1.0.0",
        "agents": 14,
        "status": "operational"
    }


# Health endpoint
@app.get("/api/health")
def health():
    return {"status": "ok", "agents": 14}
