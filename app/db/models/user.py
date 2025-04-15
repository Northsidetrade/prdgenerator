"""User model for the application."""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.db.base_model import BaseModel
from app.db.session import Base


class User(BaseModel, Base):
    """
    User model.
    
    Attributes:
        name (str): User's name
        email (str): User's email (unique)
        projects (relationship): User's projects
    """
    
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)

    # Relationships
    projects = relationship("Project", back_populates="user")
