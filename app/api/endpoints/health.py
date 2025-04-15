"""Health check endpoint module."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check():
    """Health check endpoint for monitoring and uptime checks."""
    return {
        "status": "healthy",
        "service": "prd-generator",
        "version": "0.1.0"
    }
