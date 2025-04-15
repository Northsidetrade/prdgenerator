"""User schemas for request/response validation."""

from typing import Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserBase(BaseModel):
    """Base user schema with shared attributes."""
    
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """User creation schema."""
    
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    """User update schema."""
    
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """Base user schema for DB, including hashed password."""
    
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class User(UserInDBBase):
    """User schema for response."""
    pass


class UserInDB(UserInDBBase):
    """User schema with password hash."""
    
    hashed_password: str


class Token(BaseModel):
    """Token schema."""
    
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema."""
    
    sub: Optional[str] = None
    exp: Optional[datetime] = None
