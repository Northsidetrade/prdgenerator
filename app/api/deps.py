"""API dependencies for FastAPI endpoints."""

from typing import Optional
import uuid

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.session import get_db
from app.core.config import settings
from app.services.user_service import UserService
from app.models.user import User as UserModel

# Simple function to get token from Authorization header
def get_token(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract JWT token from Authorization header."""
    if not authorization:
        return None
        
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
        
    return parts[1]

# Function to get current user (without requiring authentication)
def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(get_token)
) -> Optional[UserModel]:
    """
    Get current user from JWT token without requiring authentication.
    
    Args:
        db: Database session
        token: JWT token
        
    Returns:
        User if token is valid, None otherwise
    """
    if not token:
        return None
        
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            return None
    except JWTError:
        return None
        
    user = UserService.get_by_id(db, uuid.UUID(user_id))
    return user

# Function to get current active user (requiring authentication)
def get_current_active_user(
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(get_current_user)
) -> UserModel:
    """
    Get current active user, requiring authentication.
    
    Args:
        db: Database session
        current_user: Current user from token
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If not authenticated or user is inactive
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    if not UserService.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
        
    return current_user

# For superuser access
def get_current_active_superuser(
    current_user: UserModel = Depends(get_current_active_user)
) -> UserModel:
    """
    Get current active superuser, raising exception if not a superuser.
    
    Args:
        current_user: Current active user
        
    Returns:
        Current active superuser
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not UserService.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
        
    return current_user
