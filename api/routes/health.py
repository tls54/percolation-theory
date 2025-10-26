"""Health check endpoints."""

from fastapi import APIRouter
from api.models import HealthResponse
from api.config import settings
from Search import HAS_CPP

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and availability of optimizations."""
    try:
        import numba
        numba_available = True
    except ImportError:
        numba_available = False
    
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        cpp_available=HAS_CPP,
        numba_available=numba_available
    )