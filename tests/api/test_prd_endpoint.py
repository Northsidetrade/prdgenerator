"""Tests for PRD generation endpoints."""

from fastapi.testclient import TestClient
import pytest
import uuid
from app.models.prd import Format, TemplateType, PRD
from app.core.config import settings
from app.main import app


def test_generate_prd_unauthorized(db_session):
    """Test that generating a PRD requires authentication."""
    # Create a fresh client without auth overrides
    with TestClient(app) as client:
        response = client.post(
            f"{settings.API_V1_STR}/prd/generate",
            json={
                "title": "Test Product",
                "input_prompt": "Create a test product for developers in the technology industry",
                "format": "markdown",
                "template_type": "crud_application"
            },
        )
        assert response.status_code == 401
        assert "Not authenticated" in response.text


def test_generate_prd_authorized(client, test_auth_headers, db_session, debug_response):
    """Test generating a PRD with authentication."""
    # When a user is authenticated, they should be able to generate a PRD
    response = client.post(
        f"{settings.API_V1_STR}/prd/generate",
        json={
            "title": "Test Product",
            "input_prompt": "Create a test product for developers in the technology industry",
            "format": "markdown",
            "template_type": "crud_application"
        },
        headers=test_auth_headers
    )
    # Print detailed response for debugging
    debug_response(response)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that the PRD has been created with expected fields
    assert "id" in data
    assert data["title"] == "Test Product"
    assert "content" in data
    assert data["format"] == "markdown"
    assert data["template_type"] == "crud_application"
    
    # Verify that the PRD was saved to the database
    # Convert string UUID to UUID object for database query
    prd_id = uuid.UUID(data["id"])
    prd_in_db = db_session.query(PRD).filter(PRD.id == prd_id).first()
    assert prd_in_db is not None
    assert prd_in_db.title == "Test Product"
    assert prd_in_db.format == Format.MARKDOWN
    assert prd_in_db.template_type == TemplateType.CRUD


def test_get_user_prds(client, test_auth_headers, test_user, db_session):
    """Test retrieving a user's PRDs."""
    # First generate a PRD
    response = client.post(
        f"{settings.API_V1_STR}/prd/generate",
        json={
            "title": "Another Test Product",
            "input_prompt": "Create a healthcare SAAS product for doctors",
            "format": "markdown",
            "template_type": "saas_platform"
        },
        headers=test_auth_headers
    )
    assert response.status_code == 200
    
    # Then get all PRDs for the user
    response = client.get(f"{settings.API_V1_STR}/prd/", headers=test_auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    # User should have at least one PRD
    assert len(data) >= 1
    
    # Check that the PRD we just created is in the list
    found = False
    for prd in data:
        if prd["title"] == "Another Test Product":
            found = True
            assert prd["format"] == "markdown"
            assert prd["template_type"] == "saas_platform"
    assert found, "The newly created PRD was not found in the user's PRDs"


def test_get_prd_by_id(client, test_auth_headers, test_user, db_session):
    """Test retrieving a specific PRD by ID."""
    # First generate a PRD
    response = client.post(
        f"{settings.API_V1_STR}/prd/generate",
        json={
            "title": "Specific Product",
            "input_prompt": "Create an AI agent for education targeting students",
            "format": "json",
            "template_type": "ai_agent"
        },
        headers=test_auth_headers
    )
    assert response.status_code == 200
    prd_data = response.json()
    prd_id = prd_data["id"]
    
    # Then get that specific PRD by ID
    response = client.get(f"{settings.API_V1_STR}/prd/{prd_id}", headers=test_auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    # Check that it's the correct PRD
    assert data["id"] == prd_id
    assert data["title"] == "Specific Product"
    assert data["format"] == "json"
    assert data["template_type"] == "ai_agent"
    
    # Verify in the database
    db_prd = db_session.query(PRD).filter(PRD.id == uuid.UUID(prd_id)).first()
    assert db_prd is not None
    assert db_prd.title == "Specific Product"


def test_get_other_user_prd_forbidden(client, test_auth_headers, test_user, test_superuser, db_session, debug_response):
    """Test that a user cannot access another user's PRD."""
    # Directly create a PRD in the database owned by the superuser
    superuser_prd = PRD(
        title="Admin Product",
        input_prompt="Create a finance product for banks using a custom template",
        content="# Admin Product\n\nTest content created by admin.",
        format=Format.MARKDOWN,
        template_type=TemplateType.CUSTOM,
        user_id=test_superuser.id  # Essential - this associates the PRD with the superuser
    )
    db_session.add(superuser_prd)
    db_session.commit()
    db_session.refresh(superuser_prd)
    
    # Get PRD ID
    prd_id = str(superuser_prd.id)
    
    # Verify the PRD exists and belongs to superuser
    db_prd = db_session.query(PRD).filter(PRD.id == superuser_prd.id).first()
    assert db_prd is not None
    assert db_prd.user_id == test_superuser.id
    assert db_prd.user_id != test_user.id  # Confirm different user
    
    # Try to access it as regular user
    response = client.get(
        f"{settings.API_V1_STR}/prd/{prd_id}", 
        headers=test_auth_headers
    )
    
    # Debug the response
    debug_response(response)
    
    # It should be forbidden since the PRD belongs to superuser
    assert response.status_code == 403, "Regular user should not be able to access superuser's PRD"
