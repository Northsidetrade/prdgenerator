"""Test module for the PRD generation endpoint."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_generate_prd_success(client):
    """
    Test that the PRD generation endpoint successfully returns a PRD.
    
    Given: A running FastAPI application
    When: A POST request is made to the PRD generation endpoint with valid data
    Then: The response should contain a generated PRD with status code 200
    """
    test_data = {
        "title": "Test PRD",
        "input_prompt": "Create a PRD for a video editing app",
        "template_type": "crud_application",
        "format": "markdown"
    }
    
    response = client.post("/api/v1/prd/generate", json=test_data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["title"] == "Test PRD"
    assert "content" in result
    assert "id" in result
    assert "created_at" in result
    assert result["format"] == "markdown"


def test_generate_prd_invalid_format(client):
    """
    Test that the PRD generation endpoint returns an error for invalid format.
    
    Given: A running FastAPI application
    When: A POST request is made with an invalid format value
    Then: The response should return a 422 validation error
    """
    test_data = {
        "title": "Test PRD",
        "input_prompt": "Create a PRD for a video editing app",
        "template_type": "crud_application",
        "format": "invalid_format"  # Invalid format
    }
    
    response = client.post("/api/v1/prd/generate", json=test_data)
    
    assert response.status_code == 422  # Validation error
    assert "detail" in response.json()


def test_generate_prd_missing_required_field(client):
    """
    Test that the PRD generation endpoint returns an error when required fields are missing.
    
    Given: A running FastAPI application
    When: A POST request is made with missing required fields
    Then: The response should return a 422 validation error
    """
    # Missing title and input_prompt
    test_data = {
        "template_type": "crud_application",
        "format": "markdown"
    }
    
    response = client.post("/api/v1/prd/generate", json=test_data)
    
    assert response.status_code == 422  # Validation error
    assert "detail" in response.json()
