"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import settings
from app.core.security import verify_password
from app.main import app


def test_register_user(client, db_session):
    """Test user registration endpoint."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "full_name": "New User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    
    # Check that user was created with correct data
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data
    assert "hashed_password" not in data
    
    # Verify user was created in the database
    from app.models.user import User
    user_in_db = db_session.query(User).filter(User.email == "newuser@example.com").first()
    assert user_in_db is not None
    assert user_in_db.email == "newuser@example.com"
    assert user_in_db.full_name == "New User"
    assert verify_password("StrongPassword123!", user_in_db.hashed_password)


def test_register_existing_user(client, test_user):
    """Test registration with existing email should fail."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": test_user.email,  # Using existing test user email
            "password": "AnotherPassword123!",
            "full_name": "Duplicate User"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already exists" in data["detail"].lower()


def test_login_success(client, test_user):
    """Test successful login returns a valid token."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": "test@example.com",  # Using existing test user
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Validate token contains correct user info
    token = data["access_token"]
    payload = jwt.decode(
        token, 
        settings.SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )
    assert payload["sub"] == str(test_user.id)


def test_login_wrong_password(client, test_user):
    """Test login with incorrect password fails."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "incorrect" in data["detail"].lower()


def test_login_nonexistent_user(client):
    """Test login with non-existent user fails."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "incorrect" in data["detail"].lower()


def test_get_current_user(client, test_auth_headers, test_user):
    """Test getting current user information."""
    response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=test_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == str(test_user.id)
    assert "hashed_password" not in data


def test_get_current_user_unauthorized(db_session):
    """Test that unauthorized access to user info fails."""
    # Create a fresh client without auth overrides
    with TestClient(app) as client:
        response = client.get(f"{settings.API_V1_STR}/users/me")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "not authenticated" in data["detail"].lower()
