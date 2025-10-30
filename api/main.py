"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.config import settings
from api.routes import health, simulation, visualization  

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api")
app.include_router(simulation.router, prefix="/api")
app.include_router(visualization.router, prefix="/api") 


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Percolation Theory API",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/api/health"
    }