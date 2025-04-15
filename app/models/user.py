"""User model for authentication and authorization."""

from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """User model for authentication and authorization."""
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    prds = relationship("PRD", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User {self.email}>"
