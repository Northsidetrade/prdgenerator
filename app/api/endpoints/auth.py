"""Authentication endpoints for user login and registration."""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.services.user_service import UserService
from app.schemas.user import Token, User as UserSchema, UserCreate

# Use router with no dependencies since auth is handled by OptionalOAuth2PasswordBearer in deps.py
router = APIRouter()


@router.post("/login", response_model=Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    Args:
        form_data: OAuth2 form data with username and password
        db: Database session
        
    Returns:
        Token with access token and token type
        
    Raises:
        HTTPException: If authentication fails
    """
    # Log the login attempt for debugging
    print(f"Login attempt for user: {form_data.username}")
    
    # Authenticate user
    user = UserService.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not UserService.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    # Log successful login
    print(f"Login successful for user: {form_data.username}")
    
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user.
    
    Args:
        user_in: User creation data
        db: Database session
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If user already exists
    """
    # Log registration attempt
    print(f"Registration attempt for email: {user_in.email}")
    
    # Check if user already exists
    user = UserService.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    
    # Create user
    user = UserService.create(db, user_in=user_in)
    
    # Log successful registration
    print(f"User registered successfully: {user_in.email}")
    
    return user
