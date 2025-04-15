"""Tests for PRD generation using direct API calls."""

import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

# Use the client fixture from conftest.py
# This ensures app.state.testing is set properly

def test_generate_markdown_prd(client):
    """Test generating a PRD in markdown format"""
    # Check if API is running
    health_response = client.get("/api/v1/health/")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "healthy"
    
    # Data for generating a PRD in markdown format
    request_data = {
        "title": "Example Product",
        "input_prompt": "A video editing tool",
        "format": "markdown",
        "template_type": "crud_application"
    }
    
    # Send request to generate PRD
    response = client.post("/api/v1/prd/generate", json=request_data)
    
    # Check response
    assert response.status_code == 200
    response_data = response.json()
    assert "content" in response_data
    assert response_data["format"] == "markdown"
    assert response_data["content"].startswith("# Example Product")
    assert "A video editing tool" in response_data["content"]

def test_generate_json_prd(client):
    """Test generating a PRD in JSON format"""
    # Check if API is running
    health_response = client.get("/api/v1/health/")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "healthy"
    
    # Data for generating a PRD in JSON format
    request_data = {
        "title": "Example Product",
        "input_prompt": "A video editing tool",
        "format": "json",
        "template_type": "crud_application"
    }
    
    # Send request to generate PRD
    response = client.post("/api/v1/prd/generate", json=request_data)
    
    # Check response
    assert response.status_code == 200
    response_data = response.json()
    assert "content" in response_data
    assert response_data["format"] == "json"
    
    # Verify content has the title
    assert "Example Product" in response_data["content"]
    
    # Verify we can parse the JSON content
    try:
        json_content = json.loads(response_data["content"])
        assert isinstance(json_content, dict)
    except json.JSONDecodeError:
        assert False, "Response content is not valid JSON"

def test_generate_prd_with_invalid_format(client):
    """Test attempting to generate a PRD with an invalid format"""
    # Check if API is running
    health_response = client.get("/api/v1/health/")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "healthy"
    
    # Data with invalid format
    request_data = {
        "title": "Example Product",
        "input_prompt": "A video editing tool",
        "format": "invalid_format",
        "template_type": "crud_application"
    }
    
    # Send request to generate PRD
    response = client.post("/api/v1/prd/generate", json=request_data)
    
    # Verify validation error
    assert response.status_code == 422
