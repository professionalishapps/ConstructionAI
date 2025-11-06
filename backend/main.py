from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router

from fastapi import APIRouter

app = FastAPI(title="Construction Project Risk Monitor API")

# Configure CORS - allow both localhost forms used by dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Construction Project Risk Monitor API"}


# Small health endpoint for the MVP
@app.get("/api/health")
def health():
    return {"status": "ok"}
