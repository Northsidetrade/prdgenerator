"""Pydantic schemas for PRD generation."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Format(str, Enum):
    """Supported PRD output formats."""
    
    MARKDOWN = "markdown"
    JSON = "json"


class TemplateType(str, Enum):
    """Available PRD template types."""
    
    CRUD = "crud_application"
    AI_AGENT = "ai_agent"
    SAAS = "saas_platform"
    CUSTOM = "custom"


class PRDBase(BaseModel):
    """Base PRD model with common attributes."""
    
    title: str = Field(..., description="Title of the PRD")
    input_prompt: str = Field(..., description="User input describing the product")
    template_type: TemplateType = Field(
        default=TemplateType.CRUD, 
        description="Template to use for PRD generation"
    )
    format: Format = Field(
        default=Format.MARKDOWN, 
        description="Output format for the PRD"
    )


class PRDCreate(PRDBase):
    """Model for creating a new PRD."""
    
    user_id: Optional[UUID] = Field(None, description="ID of the user creating the PRD")
    project_id: Optional[UUID] = Field(None, description="ID of an existing project to link")


class PRDUpdate(BaseModel):
    """Model for updating an existing PRD."""
    
    title: Optional[str] = Field(None, description="Updated title of the PRD")
    content: Optional[str] = Field(None, description="Updated content of the PRD")
    format: Optional[Format] = Field(None, description="Updated format of the PRD")
    template_type: Optional[TemplateType] = Field(None, description="Updated template type")
    
    class Config:
        """Pydantic configuration."""
        
        from_attributes = True


class PRDInDB(PRDBase):
    """Model for a PRD as stored in the database."""
    
    id: UUID = Field(..., description="Unique identifier of the PRD")
    user_id: UUID = Field(..., description="ID of the user who created the PRD")
    content: str = Field(..., description="Generated PRD content")
    created_at: datetime = Field(..., description="Timestamp when the PRD was created")
    updated_at: datetime = Field(..., description="Timestamp when the PRD was last updated")
    
    class Config:
        """Pydantic configuration."""
        
        from_attributes = True


class PRDResponse(BaseModel):
    """Model for PRD response."""
    
    id: UUID = Field(..., description="Unique identifier of the PRD")
    title: str = Field(..., description="Title of the PRD")
    content: str = Field(..., description="Generated PRD content")
    format: Format = Field(..., description="Format of the PRD content")
    created_at: datetime = Field(..., description="Timestamp when the PRD was created")
    user_id: Optional[UUID] = Field(None, description="ID of the user who created the PRD")
    template_type: TemplateType = Field(..., description="Template type used for the PRD")

    class Config:
        """Pydantic configuration."""
        
        from_attributes = True
