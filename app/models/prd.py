"""PRD model for storing generated Product Requirement Documents."""

from sqlalchemy import Column, String, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.schemas.prd import Format, TemplateType
from app.models.base import BaseModel


class PRD(BaseModel):
    """PRD model for storing generated Product Requirement Documents."""
    
    title = Column(String(255), nullable=False, index=True)
    input_prompt = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    format = Column(
        Enum(Format),
        nullable=False,
        default=Format.MARKDOWN
    )
    template_type = Column(
        Enum(TemplateType),
        nullable=False,
        default=TemplateType.CRUD
    )
    
    # Foreign keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Relationships
    user = relationship("User", back_populates="prds")
    
    def __repr__(self) -> str:
        """String representation of the PRD."""
        return f"<PRD {self.title}>"
