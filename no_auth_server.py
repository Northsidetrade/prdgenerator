"""Direct FastAPI implementation for PRD Generator API with NO AUTHENTICATION."""

from fastapi import FastAPI, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict
from datetime import datetime, UTC
import uuid
import os
import json
import asyncio
from enum import Enum
from typing import Optional
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv

import openai
from openai import OpenAI
import anthropic

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Direct PRD Generator API - NO AUTH")

# Mount static files
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEFAULT_MODEL_PROVIDER = os.getenv("DEFAULT_MODEL_PROVIDER", "openai")

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Mock database
USERS_DB = {}
PRDS_DB = {}

# Template types
class TemplateType(str, Enum):
    CRUD = "crud"
    AI_AGENT = "ai_agent"
    SAAS = "saas"
    CUSTOM = "custom"

# Output formats
class Format(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"

# Model providers
class ModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    TEST = "test"

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

# Models
class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: str
    password: str
    full_name: str

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    full_name: str
    is_active: bool = True

class PRDCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    input_prompt: str
    template_type: str
    format: str = "markdown"

class PRD(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    content: str
    format: str
    template_type: str
    created_at: datetime
    user_id: str

# LLM Service Functions
async def generate_prd_content(
    title: str,
    input_prompt: str,
    template_type: str,
    output_format: str,
    provider: Optional[str] = None
) -> str:
    """
    Generate PRD content using the specified LLM provider.
    """
    if not provider:
        provider = DEFAULT_MODEL_PROVIDER
    
    # Special case for TEST provider - used for testing without API calls
    if provider == "test":
        return _generate_test_content(title, input_prompt, template_type, output_format)
    
    # Prepare the prompt based on template type
    template = TEMPLATE_PROMPTS.get(template_type, TEMPLATE_PROMPTS[TemplateType.CUSTOM])
    prompt = template.format(title=title, input_prompt=input_prompt)
    
    # Add format instructions
    if output_format == "json":
        prompt += "\n\nReturn the PRD as a valid JSON object with keys for each section."
    else:
        prompt += "\n\nReturn the PRD in markdown format with proper headings and formatting."
    
    try:
        if provider == "openai":
            return await _generate_with_openai(prompt, output_format)
        elif provider == "anthropic":
            return await _generate_with_anthropic(prompt, output_format)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    except Exception as e:
        print(f"Error generating PRD content: {str(e)}")
        return _generate_test_content(title, input_prompt, template_type, output_format)

async def _generate_with_openai(prompt: str, output_format: str) -> str:
    """Generate content using OpenAI's API."""
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a product manager who writes detailed, well-structured PRDs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        raise

async def _generate_with_anthropic(prompt: str, output_format: str) -> str:
    """Generate content using Anthropic's API."""
    try:
        message = anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            temperature=0.7,
            system="You are a product manager who writes detailed, well-structured PRDs.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Anthropic API error: {str(e)}")
        raise

def _generate_test_content(
    title: str,
    input_prompt: str,
    template_type: str,
    output_format: str
) -> str:
    """
    Generate test PRD content that doesn't require API calls.
    """
    if output_format == "json":
        # Create a realistic JSON structure
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

# Public endpoints
@app.get("/")
def root():
    return {"status": "healthy", "message": "Direct PRD Generator API - NO AUTH"}

@app.get("/api/v1/health")
def health():
    return {"status": "healthy", "service": "prd-generator", "version": "0.1.0"}

@app.post("/api/v1/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Always successful login"""
    return {"access_token": str(uuid.uuid4()), "token_type": "bearer"}

@app.post("/api/v1/auth/register")
def register(user_in: UserCreate):
    """Simulate registration - always successful"""
    user_id = str(uuid.uuid4())
    return {"message": "Registration successful", "user_id": user_id}

@app.get("/api/v1/users/me")
def get_me():
    """Return a default user"""
    default_user = {
        "id": str(uuid.uuid4()),
        "email": "default@example.com",
        "full_name": "Default User",
        "is_active": True
    }
    return default_user

@app.post("/api/v1/prd/generate")
async def generate_prd(prd_in: PRDCreate):
    """Generate a PRD using the LLM service"""
    prd_id = str(uuid.uuid4())
    
    # Generate PRD content using the LLM service
    content = await generate_prd_content(
        title=prd_in.title,
        input_prompt=prd_in.input_prompt,
        template_type=prd_in.template_type,
        output_format=prd_in.format
    )
    
    prd = {
        "id": prd_id,
        "title": prd_in.title,
        "content": content,
        "format": prd_in.format,
        "template_type": prd_in.template_type,
        "created_at": datetime.now(UTC),
        "user_id": str(uuid.uuid4())  # Random user ID
    }
    
    PRDS_DB[prd_id] = prd
    return prd

@app.get("/api/v1/prd")
def get_prds():
    """Return all PRDs"""
    return list(PRDS_DB.values())

if __name__ == "__main__":
    print("Starting direct server on port 8888 with NO AUTHENTICATION")
    import uvicorn
    uvicorn.run("no_auth_server:app", host="0.0.0.0", port=8888, reload=True)
