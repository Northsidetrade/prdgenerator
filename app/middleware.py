"""Custom middleware for authentication bypass."""

from typing import Callable, List
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class PublicEndpointMiddleware(BaseHTTPMiddleware):
    """Middleware to bypass authentication for specific endpoints."""
    
    def __init__(self, app: ASGIApp, public_paths: List[str]):
        """Initialize middleware with a list of public paths."""
        super().__init__(app)
        self.public_paths = public_paths
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Dispatch the request to the next middleware or route handler.
        
        If the path is in the public_paths list, remove the Authorization header
        to bypass authentication.
        """
        # Check if the path is in the list of public paths
        path = request.url.path
        
        # Debug output
        print(f"Request path: {path}")
        print(f"Public paths: {self.public_paths}")
        print(f"Is public: {any(path.startswith(p) for p in self.public_paths)}")
        
        if any(path.startswith(p) for p in self.public_paths):
            # This is a public path, remove any Authorization header to bypass auth
            # We can't actually modify the request headers, but we can create a modified scope
            headers = []
            for header_name, header_value in request.headers.items():
                if header_name.lower() != 'authorization':
                    headers.append((header_name.encode(), header_value.encode()))
            
            # Create new request with modified headers
            request._headers = headers
            
            # Debug output
            print(f"Headers after modification: {headers}")
        
        # Call the next middleware/route handler
        response = await call_next(request)
        return response


def add_public_endpoints_middleware(app: FastAPI, public_paths: List[str]):
    """Add the PublicEndpointMiddleware to the FastAPI app."""
    app.add_middleware(PublicEndpointMiddleware, public_paths=public_paths)
