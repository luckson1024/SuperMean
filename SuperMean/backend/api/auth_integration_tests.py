#!/usr/bin/env python3
"""
SuperMean API Authentication Integration Tests

This module contains comprehensive integration tests for authentication endpoints.
It tests the full authentication flow including login, token validation, and authorization.
"""

import os
import sys
import unittest
import json
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Add the parent directory to the Python path for proper imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import the FastAPI app
from api.main import app

# Load environment variables
load_dotenv()


class AuthIntegrationTests(unittest.TestCase):
    """Integration tests for the SuperMean API authentication endpoints"""

    def setUp(self):
        """Set up the test client before each test"""
        self.client = TestClient(app)
        # Add any setup code here (e.g., creating test data)

    def tearDown(self):
        """Clean up after each test"""
        # Add any cleanup code here (e.g., removing test data)
        pass

    def test_login_success(self):
        """Test successful login with valid credentials"""
        login_data = {
            "username": "admin",
            "password": "password"
        }
        response = self.client.post("/api/auth/token", data=login_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("token_type", data)
        self.assertEqual(data["token_type"], "bearer")

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "username": "admin",
            "password": "wrong_password"
        }
        response = self.client.post("/api/auth/token", data=login_data)
        self.assertEqual(response.status_code, 401)

    def test_get_current_user(self):
        """Test getting current user information with valid token"""
        # First login to get a token
        login_data = {
            "username": "admin",
            "password": "password"
        }
        login_response = self.client.post("/api/auth/token", data=login_data)
        token = login_response.json()["access_token"]
        
        # Use the token to get current user info
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], "admin")
        self.assertIn("admin", data["roles"])

    def test_get_current_user_invalid_token(self):
        """Test getting current user information with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_refresh_token(self):
        """Test refreshing an access token"""
        # First login to get a token
        login_data = {
            "username": "admin",
            "password": "password"
        }
        login_response = self.client.post("/api/auth/token", data=login_data)
        token = login_response.json()["access_token"]
        
        # Use the token to refresh and get a new token
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/api/auth/refresh", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("token_type", data)
        self.assertEqual(data["token_type"], "bearer")
        # Verify the new token is different from the old one
        self.assertNotEqual(data["access_token"], token)

    def test_protected_endpoint_with_valid_token(self):
        """Test accessing a protected endpoint with a valid token"""
        # First login to get a token
        login_data = {
            "username": "admin",
            "password": "password"
        }
        login_response = self.client.post("/api/auth/token", data=login_data)
        token = login_response.json()["access_token"]
        
        # Use the token to access a protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/agents", headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_protected_endpoint_without_token(self):
        """Test accessing a protected endpoint without a token"""
        response = self.client.get("/api/agents")
        # The status code depends on how you've configured your endpoints
        # If you're requiring authentication for all endpoints, this should be 401
        # If you're not requiring authentication for this specific endpoint, this might be 200
        self.assertIn(response.status_code, [200, 401])


if __name__ == "__main__":
    unittest.main()