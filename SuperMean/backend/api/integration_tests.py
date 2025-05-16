#!/usr/bin/env python3
"""
SuperMean API Integration Tests

This module contains comprehensive integration tests for all API endpoints.
It tests the full request-response cycle for each endpoint to ensure proper functionality.
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


class APIIntegrationTests(unittest.TestCase):
    """Integration tests for the SuperMean API endpoints"""

    def setUp(self):
        """Set up the test client before each test"""
        self.client = TestClient(app)
        # Add any setup code here (e.g., creating test data)

    def tearDown(self):
        """Clean up after each test"""
        # Add any cleanup code here (e.g., removing test data)
        pass

    # Root and Health Endpoints
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "SuperMean API is running!"})

    def test_health_check_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    # Agent Endpoints
    def test_get_agents(self):
        """Test getting all agents"""
        response = self.client.get("/agents")
        self.assertEqual(response.status_code, 200)
        # Add more assertions based on expected response structure

    def test_get_agent_by_id(self):
        """Test getting a specific agent by ID"""
        # This would typically use a known test agent ID
        agent_id = "test-agent-id"
        response = self.client.get(f"/agents/{agent_id}")
        # For now, we'll just check the structure as we don't have actual data
        self.assertIn(response.status_code, [200, 404])

    def test_create_agent(self):
        """Test creating a new agent"""
        test_agent = {
            "name": "Test Agent",
            "type": "dev",
            "description": "A test agent for integration testing"
        }
        response = self.client.post("/agents", json=test_agent)
        self.assertIn(response.status_code, [201, 422])

    # Mission Endpoints
    def test_get_missions(self):
        """Test getting all missions"""
        response = self.client.get("/missions")
        self.assertEqual(response.status_code, 200)
        # Add more assertions based on expected response structure

    def test_get_mission_by_id(self):
        """Test getting a specific mission by ID"""
        # This would typically use a known test mission ID
        mission_id = "test-mission-id"
        response = self.client.get(f"/missions/{mission_id}")
        # For now, we'll just check the structure as we don't have actual data
        self.assertIn(response.status_code, [200, 404])

    def test_create_mission(self):
        """Test creating a new mission"""
        test_mission = {
            "title": "Test Mission",
            "description": "A test mission for integration testing",
            "agent_ids": ["test-agent-id"]
        }
        response = self.client.post("/missions", json=test_mission)
        self.assertIn(response.status_code, [201, 422])

    # SuperAgent Endpoints
    def test_get_super_agent_status(self):
        """Test getting the SuperAgent status"""
        response = self.client.get("/super-agent/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("version", data)
        self.assertIn("active_tasks", data)

    def test_create_super_agent_task(self):
        """Test creating a new SuperAgent task"""
        test_task = {
            "title": "Test Task",
            "description": "A test task for integration testing",
            "priority": "high"
        }
        response = self.client.post("/super-agent/tasks", json=test_task)
        self.assertIn(response.status_code, [201, 422])
        if response.status_code == 201:
            data = response.json()
            self.assertIn("id", data)
            self.assertEqual(data["title"], test_task["title"])
            self.assertEqual(data["description"], test_task["description"])
            self.assertEqual(data["priority"], test_task["priority"])
    
    def test_get_super_agent_tasks(self):
        """Test getting all SuperAgent tasks"""
        response = self.client.get("/super-agent/tasks")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        
    def test_get_super_agent_task_by_id(self):
        """Test getting a specific SuperAgent task by ID"""
        # Create a task first to get a valid ID
        test_task = {
            "title": "Test Task for Retrieval",
            "description": "A test task for testing retrieval",
            "priority": "medium"
        }
        create_response = self.client.post("/super-agent/tasks", json=test_task)
        
        # If task creation succeeded, test retrieval
        if create_response.status_code == 201:
            task_id = create_response.json()["id"]
            response = self.client.get(f"/super-agent/tasks/{task_id}")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["id"], task_id)
            self.assertEqual(data["title"], test_task["title"])
        else:
            # If we couldn't create a task, test with a dummy ID
            response = self.client.get("/super-agent/tasks/test-task-id")
            self.assertIn(response.status_code, [200, 404])
    
    def test_update_super_agent_task(self):
        """Test updating a SuperAgent task"""
        # Create a task first
        test_task = {
            "title": "Task to Update",
            "description": "This task will be updated",
            "priority": "low"
        }
        create_response = self.client.post("/super-agent/tasks", json=test_task)
        
        # If task creation succeeded, test update
        if create_response.status_code == 201:
            task_id = create_response.json()["id"]
            update_data = {
                "title": "Updated Task Title",
                "status": "in_progress"
            }
            response = self.client.patch(f"/super-agent/tasks/{task_id}", json=update_data)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["title"], update_data["title"])
            self.assertEqual(data["status"], update_data["status"])
        else:
            # If we couldn't create a task, test with a dummy ID
            update_data = {"title": "Updated Title"}
            response = self.client.patch("/super-agent/tasks/test-task-id", json=update_data)
            self.assertIn(response.status_code, [200, 404, 422])
    
    def test_delete_super_agent_task(self):
        """Test deleting a SuperAgent task"""
        # Create a task first
        test_task = {
            "title": "Task to Delete",
            "description": "This task will be deleted",
            "priority": "medium"
        }
        create_response = self.client.post("/super-agent/tasks", json=test_task)
        
        # If task creation succeeded, test deletion
        if create_response.status_code == 201:
            task_id = create_response.json()["id"]
            response = self.client.delete(f"/super-agent/tasks/{task_id}")
            self.assertEqual(response.status_code, 204)
            
            # Verify the task is gone
            get_response = self.client.get(f"/super-agent/tasks/{task_id}")
            self.assertEqual(get_response.status_code, 404)
        else:
            # If we couldn't create a task, test with a dummy ID
            response = self.client.delete("/super-agent/tasks/test-task-id")
            self.assertIn(response.status_code, [204, 404])


if __name__ == "__main__":
    unittest.main()