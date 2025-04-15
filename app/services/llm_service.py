"""LLM Service for generating PRD content."""

import os
import json
from typing import Dict, Any, Literal
import logging
from enum import Enum
import asyncio
from functools import partial

import openai
from openai import OpenAI
import anthropic

from app.core.config import settings
from app.schemas.prd import TemplateType, Format

# Configure logging
logger = logging.getLogger(__name__)

class ModelProvider(str, Enum):
    """Supported LLM providers."""
    
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    TEST = "test"  # Special provider for testing without API calls

# Initialize clients
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

# Template prompts for different PRD types
TEMPLATE_PROMPTS = {
    TemplateType.CRUD: """
Create a detailed Product Requirements Document (PRD) for a CRUD application with these sections:
1. Executive Summary
2. Problem Statement
3. User Personas
4. Features and Requirements (including CRUD operations)
5. UI/UX Requirements
6. Technical Architecture
7. API Specifications
8. Security Requirements
9. Testing Strategy (with focus on TDD/BDD)
10. Implementation Timeline

Title: {title}
Product Description: {input_prompt}
    """,
    
    TemplateType.AI_AGENT: """
Create a detailed Product Requirements Document (PRD) for an AI agent with these sections:
1. Executive Summary
2. Problem Statement
3. Agent Capabilities
4. User Interaction Model
5. AI Model Requirements
6. Training Data Requirements
7. Integration Points
8. Performance Metrics
9. Monitoring and Feedback Loop
10. Testing Strategy (with focus on TDD/BDD)
11. Implementation Timeline

Title: {title}
Product Description: {input_prompt}
    """,
    
    TemplateType.SAAS: """
Create a detailed Product Requirements Document (PRD) for a SaaS platform with these sections:
1. Executive Summary
2. Problem Statement
3. User Personas and Roles
4. Subscription Tiers
5. Core Features
6. UI/UX Requirements
7. Technical Architecture
8. Integration Requirements
9. Security and Compliance
10. Testing Strategy (with focus on TDD/BDD)
11. Implementation Timeline

Title: {title}
Product Description: {input_prompt}
    """,
    
    TemplateType.CUSTOM: """
Create a detailed Product Requirements Document (PRD) with these sections:
1. Executive Summary
2. Problem Statement
3. User Personas
4. Feature Requirements
5. Technical Requirements
6. Success Metrics
7. Testing Strategy (with focus on TDD/BDD)
8. Implementation Timeline

Title: {title}
Product Description: {input_prompt}
    """
}

async def generate_prd_content(
    title: str,
    input_prompt: str,
    template_type: TemplateType,
    output_format: Format,
    provider: ModelProvider = None
) -> str:
    """
    Generate PRD content using the specified LLM provider.
    
    Args:
        title: The title of the PRD
        input_prompt: User input describing the product
        template_type: The template type to use
        output_format: The desired output format (markdown or json)
        provider: The LLM provider to use (defaults to settings.DEFAULT_MODEL_PROVIDER)
        
    Returns:
        The generated PRD content as a string
    """
    if not provider:
        provider = ModelProvider(settings.DEFAULT_MODEL_PROVIDER)
    
    # Special case for TEST provider - used for actual testing without API calls
    if provider == ModelProvider.TEST:
        return _generate_test_content(title, input_prompt, template_type, output_format)
    
    # Prepare the prompt based on template type
    template = TEMPLATE_PROMPTS.get(template_type, TEMPLATE_PROMPTS[TemplateType.CUSTOM])
    prompt = template.format(title=title, input_prompt=input_prompt)
    
    # Add format instructions
    if output_format == Format.JSON:
        prompt += "\n\nReturn the PRD as a valid JSON object with keys for each section."
    else:
        prompt += "\n\nReturn the PRD in markdown format with proper headings and formatting."
    
    try:
        if provider == ModelProvider.OPENAI:
            return await _generate_with_openai(prompt, output_format)
        elif provider == ModelProvider.ANTHROPIC:
            return await _generate_with_anthropic(prompt, output_format)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    except Exception as e:
        logger.error(f"Error generating PRD content: {str(e)}")
        raise

def _generate_test_content(
    title: str,
    input_prompt: str,
    template_type: TemplateType,
    output_format: Format
) -> str:
    """
    Generate test PRD content that doesn't require API calls.
    This function creates real, usable content following a structure similar
    to what the AI would generate, making it suitable for integration testing
    while avoiding external API dependencies.
    
    Args:
        title: The title of the PRD
        input_prompt: User input describing the product
        template_type: The template type to use
        output_format: The desired output format (markdown or json)
        
    Returns:
        The generated test PRD content as a string
    """
    if output_format == Format.JSON:
        # Create a realistic JSON structure based on the template type
        content = {
            "title": title,
            "overview": f"An overview of {title}: {input_prompt}",
            "sections": {
                "problemStatement": f"This PRD addresses the need for: {input_prompt}",
                "userPersonas": ["Power Users", "Administrators", "Regular Users"],
                "features": [
                    {"name": "Core Feature 1", "description": "Description of feature"},
                    {"name": "Core Feature 2", "description": "Description of feature"}
                ],
                "technicalRequirements": {
                    "frontend": "React.js with TypeScript",
                    "backend": "FastAPI with Python",
                    "database": "PostgreSQL"
                },
                "timeline": "3 months development timeline"
            }
        }
        return json.dumps(content, indent=2)
    else:
        # Create a realistic markdown structure
        return f"""# {title}

## Executive Summary

This PRD outlines the requirements for {title}, which aims to {input_prompt}.

## Problem Statement

This product solves the problem of {input_prompt} by providing a comprehensive solution.

## User Personas

- **Power Users**: Advanced users who need full functionality
- **Administrators**: System administrators who manage the application
- **Regular Users**: Everyday users with basic needs

## Features and Requirements

### Core Features

1. **Feature 1**: Description and user stories
2. **Feature 2**: Description and user stories

### Technical Requirements

- Frontend: React.js with TypeScript
- Backend: FastAPI with Python
- Database: PostgreSQL

## Testing Strategy

We will follow a TDD/BDD approach with:

1. Unit tests for all components
2. Integration tests for API endpoints
3. End-to-end tests for critical user flows

## Implementation Timeline

The estimated timeline for development is 3 months.
"""

async def _generate_with_openai(prompt: str, output_format: Format) -> str:
    """Generate content using OpenAI's API."""
    try:
        # Run the synchronous OpenAI API call in a thread pool
        loop = asyncio.get_event_loop()
        completion_func = partial(
            openai_client.chat.completions.create,
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a product manager who writes detailed, well-structured PRDs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        completion = await loop.run_in_executor(None, completion_func)
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise

async def _generate_with_anthropic(prompt: str, output_format: Format) -> str:
    """Generate content using Anthropic's API."""
    try:
        # Run the synchronous Anthropic API call in a thread pool
        loop = asyncio.get_event_loop()
        message_func = partial(
            anthropic_client.messages.create,
            model="claude-3-opus-20240229",
            max_tokens=4000,
            temperature=0.7,
            system="You are a product manager who writes detailed, well-structured PRDs.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        message = await loop.run_in_executor(None, message_func)
        return message.content[0].text
    except Exception as e:
        logger.error(f"Anthropic API error: {str(e)}")
        raise
