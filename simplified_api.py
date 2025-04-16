"""Simplified API for PRD Generator with clear authentication separation."""

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import uuid
import os
import uvicorn

# Import from our actual application to reuse components
from app.db.session import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.config import settings
from app.services.user_service import UserService
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema, Token
from app.schemas.prd import PRDCreate, PRD as PRDSchema

# Create FastAPI app
app = FastAPI(title="Simplified PRD Generator API")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define token bearer scheme for protected routes - but don't apply it globally
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False  # Don't auto-raise 401 errors
)

def extract_token(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract token from Authorization header."""
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
        
    return parts[1]

def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(extract_token)
) -> Optional[User]:
    """Get current user from token."""
    if not token:
        return None
    
    try:
        from jose import jwt, JWTError
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            return None
    except Exception:
        return None
    
    user = UserService.get_by_id(db, uuid.UUID(user_id))
    return user

def require_auth(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user)
) -> User:
    """Dependency to use on protected routes - raises 401 if no authenticated user."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if user is active
    if not UserService.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user

# PUBLIC ROUTES
# ============================================================

@app.get("/")
async def root():
    """Root endpoint - no auth required."""
    return {"message": "Welcome to PRD Generator API"}

@app.get("/api/v1/health")
async def health():
    """Health check endpoint - no auth required."""
    return {"status": "healthy", "service": "prd-generator"}

@app.post("/api/v1/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint - no auth required."""
    # Log login attempt
    print(f"Login attempt: {form_data.username}")
    
    user = UserService.authenticate(
        db=db, 
        email=form_data.username, 
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires
    )
    
    # Log success
    print(f"Login successful: {form_data.username}")
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/auth/register", response_model=UserSchema)
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """Register endpoint - no auth required."""
    # Log registration attempt
    print(f"Registration attempt: {user_in.email}")
    
    # Check if user exists
    existing_user = UserService.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user
    user = UserService.create(db, user_in=user_in)
    
    # Log success
    print(f"Registration successful: {user_in.email}")
    
    return user

# PROTECTED ROUTES
# ============================================================
# These all use the require_auth dependency

@app.get("/api/v1/users/me", response_model=UserSchema)
async def get_me(current_user: User = Depends(require_auth)):
    """Get current user - auth required."""
    return current_user

@app.post("/api/v1/prd/generate", response_model=PRDSchema)
async def generate_prd(
    prd_in: PRDCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """Generate a PRD - auth required."""
    from app.services.prd_service import PRDService
    
    # Create PRD
    prd = PRDService.create(db, user_id=current_user.id, prd_in=prd_in)
    return prd

@app.get("/api/v1/prd", response_model=List[PRDSchema])
async def get_prds(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """Get user's PRDs - auth required."""
    from app.services.prd_service import PRDService
    
    # Get PRDs
    prds = PRDService.get_multi_by_user(
        db=db, 
        user_id=current_user.id,
        skip=0,
        limit=100
    )
    return prds

if __name__ == "__main__":
    print("Starting simplified API on port 8000...")
    uvicorn.run("simplified_api:app", host="0.0.0.0", port=8000, reload=True)
