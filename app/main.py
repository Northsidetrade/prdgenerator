"""Main FastAPI application module."""

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.config import settings
from app.db.session import get_db
from app.api.endpoints import prd, users
from app.services.user_service import UserService
from app.core.security import create_access_token
from app.schemas.user import Token, User as UserSchema, UserCreate

# Create the FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered PRD Generator API",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PUBLIC ENDPOINTS - NO AUTHENTICATION REQUIRED

@app.get("/")
async def root():
    """Root endpoint - no authentication required."""
    return {"status": "healthy", "message": "PRD Generator API is running"}

# Direct health endpoint implementation without using router
@app.get(f"{settings.API_V1_STR}/health")
async def health_check():
    """Health check endpoint - no authentication required."""
    return {
        "status": "healthy",
        "service": "prd-generator",
        "version": "0.1.0"
    }

@app.post(f"{settings.API_V1_STR}/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint - no authentication required."""
    print(f"Login attempt for user: {form_data.username}")
    
    user = UserService.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not UserService.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    print(f"Login successful for user: {form_data.username}")
    return {"access_token": token, "token_type": "bearer"}

@app.post(f"{settings.API_V1_STR}/auth/register", response_model=UserSchema)
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """Register endpoint - no authentication required."""
    print(f"Registration attempt for email: {user_in.email}")
    
    user = UserService.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    
    user = UserService.create(db, user_in=user_in)
    
    print(f"User registered successfully: {user_in.email}")
    return user

# PROTECTED ENDPOINTS - AUTHENTICATION REQUIRED
# These routers have dependencies that enforce authentication
app.include_router(prd.router, prefix=f"{settings.API_V1_STR}/prd", tags=["prd"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
