"""Test module for the health check endpoint."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_health_check(client):
    """
    Test that the health check endpoint returns the expected response.
    
    Given: A running FastAPI application 
    When: A GET request is made to the health endpoint
    Then: The response should return a 200 status code with healthy status
    """
    response = client.get("/api/v1/health/")
    
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "prd-generator",
        "version": "0.1.0"
    }
