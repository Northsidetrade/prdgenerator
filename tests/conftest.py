"""Pytest configuration for PRD Generator tests."""

import os
import pytest
import uuid
from typing import Dict, Optional
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db
from app.models.user import User
from app.core.security import get_password_hash
from app.core.config import settings
from app.services.user_service import UserService
from app.api.deps import get_current_active_user, get_current_user


# Test database URL - using in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    # Clean up after tests
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture
def db_session(test_engine):
    """Create a fresh database session for each test."""
    Session = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def test_user(db_session):
    """Create a test user for authentication tests."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        id=uuid.uuid4()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    yield user
    db_session.delete(user)
    db_session.commit()


@pytest.fixture
def test_superuser(db_session):
    """Create a test superuser for admin tests."""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin User",
        is_active=True,
        is_superuser=True,
        id=uuid.uuid4()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    yield user
    db_session.delete(user)
    db_session.commit()


@pytest.fixture
def test_auth_headers(test_user):
    """Create authentication headers for test user."""
    access_token = UserService.create_access_token_for_user(test_user.id)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_superuser_auth_headers(test_superuser):
    """Create authentication headers for test superuser."""
    access_token = UserService.create_access_token_for_user(test_superuser.id)
    return {"Authorization": f"Bearer {access_token}"}


# Global dictionaries to store test users
TEST_USER = None
TEST_SUPERUSER = None


@pytest.fixture
def client(db_session, test_user, test_superuser):
    """Create test client with proper auth dependency overrides."""
    global TEST_USER, TEST_SUPERUSER
    TEST_USER = test_user
    TEST_SUPERUSER = test_superuser
    
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass
    
    # Override DB dependency
    app.dependency_overrides[get_db] = _get_test_db
    
    # Create a custom auth dependency that looks at the request headers
    def _get_current_user_override():
        # This function will be replaced with an async function at runtime
        # that looks at the request headers
        pass
    
    # Override the async function at runtime with the TestClient
    from fastapi import Request
    
    # Create a proper dependency that can read Authorization headers
    async def get_test_current_user(request: Request):
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check which user to return based on the header
        if "admin@example.com" in auth_header:
            return TEST_SUPERUSER
        return TEST_USER
    
    # Set dependency overrides
    app.dependency_overrides[get_current_user] = get_test_current_user
    app.dependency_overrides[get_current_active_user] = get_test_current_user
    
    # Set testing flag
    app.state.testing = True
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Reset
    app.state.testing = False
    app.dependency_overrides = {}
    TEST_USER = None
    TEST_SUPERUSER = None


@pytest.fixture
def debug_response():
    """Helper fixture to print response details."""
    def _debug_response(response):
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Body: {response.text}")
        return response
    return _debug_response
