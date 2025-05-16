#!/usr/bin/env python3
"""
SuperMean Mission API Integration Tests

This module contains comprehensive integration tests for Mission API endpoints.
It tests the full request-response cycle for each endpoint to ensure proper functionality.
"""

import os
import sys
import unittest
import json
from fastapi.testclient import TestClient
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock

# Add the parent directory to the Python path for proper imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import the FastAPI app
from api.main import app

# Load environment variables
load_dotenv()


class MissionIntegrationTests(unittest.TestCase):
    """Integration tests for the SuperMean Mission API endpoints"""

    def setUp(self):
        """Set up the test client before each test"""
        self.client = TestClient(app)
        self.base_url = "/missions"
        
        # Test data for various requests
        self.mission_create_data = {
            "title": "Build E-commerce Platform",
            "description": "Create a full-featured e-commerce platform with user authentication, product catalog, and payment processing",
            "agent_ids": ["dev-agent-1", "design-agent-1"],
            "priority": "high",
            "deadline": "2023-12-31T23:59:59Z",
            "tags": ["e-commerce", "web-development", "payment-processing"],
            "requirements": [
                "Must support multiple payment gateways",
                "Mobile responsive design",
                "Product search and filtering"
            ]
        }
        
        self.mission_update_data = {
            "title": "Build E-commerce Platform - Updated",
            "description": "Create a full-featured e-commerce platform with enhanced features",
            "priority": "medium",
            "tags": ["e-commerce", "web-development", "payment-processing", "inventory-management"]
        }
        
        self.mission_status_update_data = {
            "status": "in_progress",
            "progress": 25,
            "notes": "Initial setup completed, working on user authentication"
        }
        
        self.mission_assignment_data = {
            "agent_ids": ["dev-agent-1", "design-agent-1", "research-agent-1"],
            "roles": {
                "dev-agent-1": "lead_developer",
                "design-agent-1": "ui_designer",
                "research-agent-1": "market_researcher"
            }
        }
        
        # Mock mission data for responses
        self.mock_mission = {
            "id": "mission-123",
            "title": "Build E-commerce Platform",
            "description": "Create a full-featured e-commerce platform with user authentication, product catalog, and payment processing",
            "agent_ids": ["dev-agent-1", "design-agent-1"],
            "status": "pending",
            "progress": 0,
            "priority": "high",
            "created_at": "2023-01-15T10:00:00Z",
            "updated_at": "2023-01-15T10:00:00Z",
            "deadline": "2023-12-31T23:59:59Z",
            "tags": ["e-commerce", "web-development", "payment-processing"],
            "requirements": [
                "Must support multiple payment gateways",
                "Mobile responsive design",
                "Product search and filtering"
            ]
        }

    def tearDown(self):
        """Clean up after each test"""
        pass

    # Mission Endpoints Tests
    def test_get_all_missions(self):
        """Test getting all missions"""
        with patch('api.mission_controller.get_missions_from_db') as mock_get_missions:
            # Mock the database function to return a list of missions
            mock_get_missions.return_value = [self.mock_mission]
            
            # Make the request
            response = self.client.get(self.base_url)
            
            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["id"], "mission-123")
            self.assertEqual(data[0]["title"], "Build E-commerce Platform")

    def test_get_mission_by_id_success(self):
        """Test getting a specific mission by ID successfully"""
        mission_id = "mission-123"
        with patch('api.mission_controller.get_mission_by_id_from_db') as mock_get_mission:
            # Mock the database function to return a mission
            mock_get_mission.return_value = self.mock_mission
            
            # Make the request
            response = self.client.get(f"{self.base_url}/{mission_id}")
            
            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["id"], mission_id)
            self.assertEqual(data["title"], "Build E-commerce Platform")

    def test_get_mission_by_id_not_found(self):
        """Test getting a mission by ID that doesn't exist"""
        mission_id = "non-existent-id"
        with patch('api.mission_controller.get_mission_by_id_from_db') as mock_get_mission:
            # Mock the database function to return None (mission not found)
            mock_get_mission.return_value = None
            
            # Make the request
            response = self.client.get(f"{self.base_url}/{mission_id}")
            
            # Assertions
            self.assertEqual(response.status_code, 404)
            data = response.json()
            self.assertEqual(data["detail"], f"Mission with ID {mission_id} not found")

    def test_create_mission_success(self):
        """Test creating a new mission successfully"""
        with patch('api.mission_controller.create_mission_in_db') as mock_create_mission:
            # Mock the database function to return the created mission
            created_mission = self.mock_mission.copy()
            mock_create_mission.return_value = created_mission
            
            # Make the request
            response = self.client.post(self.base_url, json=self.mission_create_data)
            
            # Assertions
            self.assertEqual(response.status_code, 201)
            data = response.json()
            self.assertEqual(data["title"], self.mission_create_data["title"])
            self.assertEqual(data["status"], "pending")
            self.assertEqual(data["progress"], 0)

    def test_create_mission_validation_error(self):
        """Test creating a mission with invalid data"""
        # Create invalid data (missing required fields)
        invalid_data = {
            "title": "Invalid Mission"
            # Missing description and agent_ids which are required
        }
        
        # Make the request
        response = self.client.post(self.base_url, json=invalid_data)
        
        # Assertions
        self.assertEqual(response.status_code, 422)  # Validation error

    def test_update_mission_success(self):
        """Test updating a mission successfully"""
        mission_id = "mission-123"
        with patch('api.mission_controller.get_mission_by_id_from_db') as mock_get_mission, \
             patch('api.mission_controller.update_mission_in_db') as mock_update_mission:
            # Mock the database functions
            mock_get_mission.return_value = self.mock_mission
            
            updated_mission = self.mock_mission.copy()
            updated_mission["title"] = self.mission_update_data["title"]
            updated_mission["description"] = self.mission_update_data["description"]
            updated_mission["priority"] = self.mission_update_data["priority"]
            updated_mission["tags"] = self.mission_update_data["tags"]
            updated_mission["updated_at"] = "2023-01-16T15:30:00Z"
            
            mock_update_mission.return_value = updated_mission
            
            # Make the request
            response = self.client.put(f"{self.base_url}/{mission_id}", json=self.mission_update_data)
            
            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["title"], self.mission_update_data["title"])
            self.assertEqual(data["description"], self.mission_update_data["description"])
            self.assertEqual(data["priority"], self.mission_update_data["priority"])
            self.assertEqual(data["tags"], self.mission_update_data["tags"])

    def test_update_mission_not_found(self):
        """Test updating a mission that doesn't exist"""
        mission_id = "non-existent-id"
        with patch('api.mission_controller.get_mission_by_id_from_db') as mock_get_mission:
            # Mock the database function to return None (mission not found)
            mock_get_mission.return_value = None
            
            # Make the request
            response = self.client.put(f"{self.base_url}/{mission_id}", json=self.mission_update_data)
            
            # Assertions
            self.assertEqual(response.status_code, 404)
            data = response.json()
            self.assertEqual(data["detail"], f"Mission with ID {mission_id} not found")

    def test_update_mission_status_success(self):
        """Test updating a mission's status successfully"""
        mission_id = "mission-123"
        with patch('api.mission_controller.get_mission_by_id_from_db') as mock_get_mission, \
             patch('api.mission_controller.update_mission_status_in_db') as mock_update_status:
            # Mock the database functions
            mock_get_mission.return_value = self.mock_mission
            
            updated_mission = self.mock_mission.copy()
            updated_mission["status"] = self.mission_status_update_data["status"]
            updated_mission["progress"] = self.mission_status_update_data["progress"]
            updated_mission["updated_at"] = "2023-01-16T15:30:00Z"
            
            mock_update_status.return_value = updated_mission
            
            # Make the request
            response = self.client.patch(f"{self.base_url}/{mission_id}/status", json=self.mission_status_update_data)
            
            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], self.mission_status_update_data["status"])
            self.assertEqual(data["progress"], self.mission_status_update_data["progress"])

    def test_delete_mission_success(self):
        """Test deleting a mission successfully"""
        mission_id = "mission-123"
        with patch('api.mission_controller.get_mission_by_id_from_db') as mock_get_mission, \
             patch('api.mission_controller.delete_mission_from_db') as mock_delete_mission:
            # Mock the database functions
            mock_get_mission.return_value = self.mock_mission
            mock_delete_mission.return_value = True
            
            # Make the request
            response = self.client.delete(f"{self.base_url}/{mission_id}")
            
            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertEqual(data["message"], f"Mission with ID {mission_id} deleted successfully")

    def test_delete_mission_not_found(self):
        """Test deleting a mission that doesn't exist"""
        mission_id = "non-existent-id"
        with patch('api.mission_controller.get_mission_by_id_from_db') as mock_get_mission:
            # Mock the database function to return None (mission not found)
            mock_get_mission.return_value = None
            
            # Make the request
            response = self.client.delete(f"{self.base_url}/{mission_id}")
            
            # Assertions
            self.assertEqual(response.status_code, 404)
            data = response.json()
            self.assertEqual(data["detail"], f"Mission with ID {mission_id} not found")

    def test_assign_agents_to_mission_success(self):
        """Test assigning agents to a mission successfully"""
        mission_id = "mission-123"
        with patch('api.mission_controller.get_mission_by_id_from_db') as mock_get_mission, \
             patch('api.mission_controller.assign_agents_to_mission_in_db') as mock_assign_agents:
            # Mock the database functions
            mock_get_mission.return_value = self.mock_mission
            
            updated_mission = self.mock_mission.copy()
            updated_mission["agent_ids"] = self.mission_assignment_data["agent_ids"]
            updated_mission["agent_roles"] = self.mission_assignment_data["roles"]
            updated_mission["updated_at"] = "2023-01-16T15:30:00Z"
            
            mock_assign_agents.return_value = updated_mission
            
            # Make the request
            response = self.client.post(f"{self.base_url}/{mission_id}/agents", json=self.mission_assignment_data)
            
            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["agent_ids"], self.mission_assignment_data["agent_ids"])
            self.assertEqual(data["agent_roles"], self.mission_assignment_data["roles"])


if __name__ == "__main__":
    unittest.main()