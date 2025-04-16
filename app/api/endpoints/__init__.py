"""API endpoints package."""

from app.api.endpoints import auth
from app.api.endpoints import health
from app.api.endpoints import prd
from app.api.endpoints import users

# Make routers accessible from the endpoints package
__all__ = ["auth", "health", "prd", "users"]
