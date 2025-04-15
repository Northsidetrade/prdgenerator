"""Project model for the application."""

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_model import BaseModel
from app.db.session import Base


class Project(BaseModel, Base):
    """
    Project model.
    
    Attributes:
        user_id (UUID): Foreign key to User
        title (str): Project title
        input_prompt (str): Original user input prompt
        user (relationship): User who owns the project
        prd_documents (relationship): PRD documents for this project
    """
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title = Column(String, nullable=False)
    input_prompt = Column(Text, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    prd_documents = relationship("PRDDocument", back_populates="project")
