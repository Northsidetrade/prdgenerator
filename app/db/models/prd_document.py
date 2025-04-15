"""PRD Document model for the application."""

from sqlalchemy import Column, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_model import BaseModel
from app.db.session import Base
from app.schemas.prd import Format


class PRDDocument(BaseModel, Base):
    """
    PRD Document model.
    
    Attributes:
        project_id (UUID): Foreign key to Project
        format (Enum): Document format (markdown, json)
        content (Text): PRD content
        project (relationship): Project this PRD belongs to
    """
    
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("project.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    format = Column(
        Enum(Format, native_enum=False),
        default=Format.MARKDOWN,
        nullable=False,
        index=True
    )
    
    content = Column(Text, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="prd_documents")
