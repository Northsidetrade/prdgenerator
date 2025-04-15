"""PRD generation service module."""

import logging
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID, uuid4

from app.core.config import settings
from app.schemas.prd import Format, PRDCreate, PRDResponse, TemplateType
from app.services.llm.anthropic_provider import AnthropicProvider
from app.services.llm.base import LLMProvider
from app.services.llm.openai_provider import OpenAIProvider


class PRDGenerationService:
    """
    Service for generating PRD documents using LLM providers.
    
    This service coordinates between prompt templates and LLM providers
    to generate Product Requirement Documents.
    """
    
    def __init__(self):
        """Initialize the PRD generation service."""
        self.logger = logging.getLogger("app.services.prd.generator")
        self.providers: Dict[str, LLMProvider] = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
        }
        self.default_provider = settings.DEFAULT_MODEL_PROVIDER
    
    async def generate_prd(
        self,
        prd_data: PRDCreate,
        llm_provider: Optional[str] = None
    ) -> PRDResponse:
        """
        Generate a PRD document from the provided data.
        
        Args:
            prd_data: Input data for PRD generation
            llm_provider: Optional provider override (openai or anthropic)
        
        Returns:
            PRDResponse with the generated document
        """
        provider_name = llm_provider or self.default_provider
        
        if provider_name not in self.providers:
            self.logger.error(f"Unknown LLM provider: {provider_name}")
            raise ValueError(f"Unknown LLM provider: {provider_name}. Available providers: {', '.join(self.providers.keys())}")
        
        provider = self.providers[provider_name]
        
        # Get prompt template based on template type
        prompt_template = self._get_template(prd_data.template_type)
        
        # Generate the complete prompt
        full_prompt = self._build_prompt(prompt_template, prd_data)
        
        # Generate content using the selected LLM provider
        content = await provider.generate_text(
            prompt=full_prompt,
            max_tokens=4000,
            temperature=0.7
        )
        
        # Create response object
        return PRDResponse(
            id=uuid4(),
            title=prd_data.title,
            content=content,
            format=prd_data.format,
            created_at=datetime.utcnow()
        )
    
    def _get_template(self, template_type: TemplateType) -> str:
        """
        Get the appropriate prompt template based on template type.
        
        Args:
            template_type: Type of template to use
        
        Returns:
            Template string with placeholders
        """
        # In a real implementation, these would be loaded from the database
        # For now, we'll use hardcoded templates
        templates = {
            TemplateType.CRUD: """
                Create a detailed PRD for a CRUD application with the following title: {{title}}
                
                User description: {{input_prompt}}
                
                Include the following sections:
                1. Overview
                2. User Personas
                3. User Stories
                4. Functional Requirements
                5. Non-Functional Requirements
                6. UI/UX Requirements
                7. Technical Architecture
                8. Data Models
                9. API Specifications
                10. Testing Requirements
                11. Success Metrics
            """,
            TemplateType.AI_AGENT: """
                Create a detailed PRD for an AI agent application with the following title: {{title}}
                
                User description: {{input_prompt}}
                
                Include the following sections:
                1. Overview
                2. User Personas
                3. Agent Capabilities
                4. Functional Requirements
                5. Non-Functional Requirements
                6. Conversation Flows
                7. Integration Requirements
                8. Technical Architecture
                9. AI Model Selection
                10. Training and Evaluation
                11. Security and Privacy
                12. Success Metrics
            """,
            TemplateType.SAAS: """
                Create a detailed PRD for a SaaS platform with the following title: {{title}}
                
                User description: {{input_prompt}}
                
                Include the following sections:
                1. Overview
                2. User Personas
                3. User Stories
                4. Subscription Tiers
                5. Functional Requirements
                6. Non-Functional Requirements
                7. Technical Architecture
                8. Data Models
                9. API Specifications
                10. Security Requirements
                11. Analytics and Reporting
                12. Success Metrics
            """,
            TemplateType.CUSTOM: "{{input_prompt}}"
        }
        
        return templates.get(template_type, templates[TemplateType.CRUD])
    
    def _build_prompt(self, template: str, prd_data: PRDCreate) -> str:
        """
        Fill in template placeholders with data from PRD request.
        
        Args:
            template: Template string with placeholders
            prd_data: Input data for PRD generation
        
        Returns:
            Complete prompt ready for LLM processing
        """
        # Simple placeholder replacement
        prompt = template.replace("{{title}}", prd_data.title)
        prompt = prompt.replace("{{input_prompt}}", prd_data.input_prompt)
        
        # Add format-specific instructions
        if prd_data.format == Format.MARKDOWN:
            prompt += "\n\nPlease format the PRD in Markdown syntax."
        elif prd_data.format == Format.JSON:
            prompt += "\n\nPlease format the PRD as a structured JSON object."
        
        return prompt
