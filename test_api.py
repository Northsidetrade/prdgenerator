"""Test script to verify the PRD Generator API functionality."""

import requests
import json

# API Configuration
API_URL = 'http://localhost:8000/api/v1'

def test_health_endpoint():
    """Test the health endpoint."""
    url = f"{API_URL}/health/"
    try:
        response = requests.get(url)
        print(f"Health Endpoint Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error testing health endpoint: {e}")

def test_register_endpoint():
    """Test the user registration endpoint."""
    url = f"{API_URL}/auth/register"
    payload = {
        "email": "testuser123@example.com",
        "password": "testpassword123",
        "full_name": "Test User 123"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Register Endpoint Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error testing register endpoint: {e}")

def test_login_endpoint():
    """Test the login endpoint."""
    url = f"{API_URL}/auth/login"
    payload = {
        "username": "testuser123@example.com",
        "password": "testpassword123"
    }
    try:
        # Use form data for OAuth2 password flow
        response = requests.post(url, data=payload)
        print(f"Login Endpoint Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            try:
                token = response.json()["access_token"]
                print(f"Successfully obtained token: {token[:10]}...")
                return token
            except Exception as e:
                print(f"Error parsing token: {e}")
                return None
        else:
            return None
    except Exception as e:
        print(f"Error testing login endpoint: {e}")
        return None

def test_me_endpoint(token):
    """Test the 'me' endpoint with authentication."""
    if not token:
        print("No token available, skipping me endpoint test")
        return
        
    url = f"{API_URL}/users/me"
    try:
        response = requests.get(
            url, 
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"Me Endpoint Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error testing me endpoint: {e}")

def main():
    """Run all API tests."""
    print("\n1. Testing Health Endpoint")
    test_health_endpoint()
    
    print("\n2. Testing Register Endpoint")
    test_register_endpoint()
    
    print("\n3. Testing Login Endpoint")
    token = test_login_endpoint()
    
    print("\n4. Testing Me Endpoint")
    test_me_endpoint(token)

if __name__ == "__main__":
    main()
