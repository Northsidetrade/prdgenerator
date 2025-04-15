"""Prompt Template model for the application."""

from sqlalchemy import Boolean, Column, String, Text

from app.db.base_model import BaseModel
from app.db.session import Base


class PromptTemplate(BaseModel, Base):
    """
    Prompt Template model.
    
    Attributes:
        title (str): Template title
        description (str): Template description
        template_body (str): Template content with placeholders
        model_hint (str): Optional hint for specific AI models
        is_default (bool): Whether this is a default template
        enabled (bool): Whether this template is available for use
    """
    
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    template_body = Column(Text, nullable=False)
    model_hint = Column(String, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False, index=True)
