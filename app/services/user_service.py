"""User service for managing user data and authentication."""

from typing import Optional
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Service for managing user authentication and data."""
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get a user by email address.
        
        Args:
            db: Database session
            email: User email address
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            user_in: User data
            
        Returns:
            Created user
        """
        # Create user model
        db_user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            is_active=True,
            is_superuser=False
        )
        
        # Add to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def update(db: Session, db_user: User, user_in: UserUpdate) -> User:
        """
        Update a user.
        
        Args:
            db: Database session
            db_user: Existing user model
            user_in: User update data
            
        Returns:
            Updated user
        """
        # Update attributes
        if user_in.email is not None:
            db_user.email = user_in.email
        if user_in.full_name is not None:
            db_user.full_name = user_in.full_name
        if user_in.password is not None:
            db_user.hashed_password = get_password_hash(user_in.password)
        
        # Commit changes
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.
        
        Args:
            db: Database session
            email: User email address
            password: User plain password
            
        Returns:
            User if authentication succeeds, None otherwise
        """
        # Get user by email
        user = UserService.get_by_email(db, email)
        if not user:
            return None
        
        # Check password
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    def create_access_token_for_user(user_id: uuid.UUID) -> str:
        """
        Create a JWT access token for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            JWT access token
        """
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(subject=str(user_id), expires_delta=expires_delta)
    
    @staticmethod
    def is_active(user: User) -> bool:
        """
        Check if a user is active.
        
        Args:
            user: User model
            
        Returns:
            True if user is active, False otherwise
        """
        return user.is_active
    
    @staticmethod
    def is_superuser(user: User) -> bool:
        """
        Check if a user is a superuser.
        
        Args:
            user: User model
            
        Returns:
            True if user is a superuser, False otherwise
        """
        return user.is_superuser
