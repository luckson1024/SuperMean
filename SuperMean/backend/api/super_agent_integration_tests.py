#!/usr/bin/env python3
"""
SuperMean SuperAgent API Integration Tests

This module contains comprehensive integration tests for SuperAgent API endpoints.
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

# Import schemas for validation
from api.super_agent_schemas import (
    PlanRequest, PlanResponse, PlanStep,
    EvaluationRequest, EvaluationResponse,
    MetaPlanRequest, MetaPlanResponse,
    ToolCreationRequest, ToolCreationResponse,
    ExecutionRequest, ExecutionResponse
)

# Load environment variables
load_dotenv()


class SuperAgentIntegrationTests(unittest.TestCase):
    """Integration tests for the SuperMean SuperAgent API endpoints"""

    def setUp(self):
        """Set up the test client before each test"""
        self.client = TestClient(app)
        self.base_url = "/super-agent"
        
        # Test data for various requests
        self.plan_request_data = {
            "goal": "Build a simple web application",
            "context": {
                "user_requirements": "The app should have a login page and dashboard",
                "technical_constraints": "Must use React and FastAPI"
            }
        }
        
        self.evaluation_request_data = {
            "goal": "Build a simple web application",
            "plan": [
                {"step_number": 1, "description": "Setup project structure", "status": "completed"},
                {"step_number": 2, "description": "Create login page", "status": "completed"},
                {"step_number": 3, "description": "Implement dashboard", "status": "completed"}
            ],
            "execution_result": {
                "success": True,
                "artifacts": ["login.jsx", "dashboard.jsx", "api.py"],
                "metrics": {"time_taken": 120, "resources_used": "minimal"}
            },
            "context": {
                "user_feedback": "The login page looks good but dashboard needs improvement"
            }
        }
        
        self.meta_plan_request_data = {
            "goal": "Create a full-stack e-commerce application",
            "constraints": ["Must be mobile responsive", "Should include payment processing"],
            "resources": ["React", "Node.js", "MongoDB"],
            "context": {
                "user_expertise": "intermediate",
                "timeline": "2 weeks"
            }
        }
        
        self.tool_creation_request_data = {
            "goal": "Generate API documentation",
            "specifications": {
                "input_format": "OpenAPI spec",
                "output_format": "Markdown",
                "include_examples": True
            },
            "context": {
                "existing_tools": ["code_generator", "test_runner"]
            }
        }
        
        self.execution_request_data = {
            "plan": [
                {"step_number": 1, "description": "Setup project structure", "status": "pending"},
                {"step_number": 2, "description": "Create login page", "status": "pending"},
                {"step_number": 3, "description": "Implement dashboard", "status": "pending"}
            ],
            "context": {
                "repository_url": "https://github.com/example/project",
                "branch": "main"
            },
            "execution_parameters": {
                "timeout": 300,
                "environment": "development"
            }
        }

    def tearDown(self):
        """Clean up after each test"""
        pass

    # Plan Endpoint Tests
    def test_create_plan_success(self):
        """Test successful plan creation"""
        with patch('backend.super_agent.planner.Planner.create_plan') as mock_create_plan:
            # Mock the planner's create_plan method to return a predefined plan
            mock_plan = [
                {"step_number": 1, "description": "Setup project structure"},
                {"step_number": 2, "description": "Create login page"},
                {"step_number": 3, "description": "Implement dashboard"}
            ]
            mock_create_plan.return_value = mock_plan
            
            # Make the request
            response = self.client.post(f"{self.base_url}/plan", json=self.plan_request_data)
            
            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertEqual(data["message"], "Plan created successfully")
            self.assertEqual(len(data["plan"]), 3)
            
            # Verify the mock was called with the correct arguments
            mock_create_plan.assert_called_once_with(
                goal=self.plan_request_data["goal"],
                context=self.plan_request_data["context"]
            )

    def test_create_plan_failure(self):
        """Test plan creation failure"""
        with patch('backend.super_agent.planner.Planner.create_plan') as mock_create_plan:
            # Mock the planner to raise an exception
            from backend.super_agent.planner import PlanningError
            mock_create_plan.side_effect = PlanningError("Failed to create plan")
            
            # Make the request
            response = self.client.post(f"{self.base_url}/plan", json=self.plan_request_data)
            
            # Assertions
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertEqual(data["detail"], "Planning failed: Failed to create plan")

    # Evaluation Endpoint Tests
    def test_evaluate_execution_success(self):
        """Test successful execution evaluation"""
        with patch('backend.super_agent.evaluator.Evaluator.evaluate_execution') as mock_evaluate:
            # Mock the evaluator's evaluate_execution method
            mock_evaluation = {
                "score": 85,
                "feedback": "Good implementation but dashboard needs improvement",
                "suggestions": ["Add more interactive elements to dashboard", "Improve error handling"]
            }
            mock_evaluate.return_value = mock_evaluation
            
            # Make the request
            response = self.client.post(f"{self.base_url}/evaluate", json=self.evaluation_request_data)
            
            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertEqual(data["message"], "Evaluation completed successfully")
            self.assertEqual(data["evaluation"]["score"], 85)
            self.assertEqual(len(data["evaluation"]["suggestions"]), 2)

    def test_evaluate_execution_failure(self):
        """Test execution evaluation failure"""
        with patch('backend.super_agent.evaluator.Evaluator.evaluate_execution') as mock_evaluate:
            # Mock the evaluator to raise an exception
            from backend.super_agent.evaluator import EvaluationError
            mock_evaluate.side_effect = EvaluationError("Failed to evaluate execution")
            
            # Make the request
            response = self.client.post(f"{self.base_url}/evaluate", json=self.evaluation_request_data)
            
            # Assertions
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertEqual(data["detail"], "Evaluation failed: Failed to evaluate execution")

    # Meta Plan Endpoint Tests
    def test_create_meta_plan_success(self):
        """Test successful meta plan creation"""
        with patch('backend.super_agent.meta_planner.MetaPlanner.create_meta_plan') as mock_meta_plan:
            # Mock the meta planner's create_meta_plan method
            mock_plan = {
                "phases": [
                    {"name": "Planning", "steps": ["Define requirements", "Create architecture"]},
                    {"name": "Development", "steps": ["Setup backend", "Develop frontend", "Integrate payment"]},
                    {"name": "Testing", "steps": ["Unit tests", "Integration tests", "User acceptance tests"]}
                ],
                "tools_required": ["code_generator", "test_runner", "deployment_tool"],
                "estimated_timeline": "14 days"
            }
            mock_meta_plan.return_value = mock_plan
            
            # Make the request
            response = self.client.post(f"{self.base_url}/meta-plan", json=self.meta_plan_request_data)
            
            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertEqual(data["message"], "Meta plan created successfully")
            self.assertEqual(len(data["meta_plan"]["phases"]), 3)
            self.assertEqual(len(data["meta_plan"]["tools_required"]), 3)

    # Tool Creation Endpoint Tests
    def test_create_tool_success(self):
        """Test successful tool creation"""
        with patch('backend.super_agent.tool_creator.ToolCreator.create_tool') as mock_create_tool:
            # Mock the tool creator's create_tool method
            mock_tool = {
                "name": "api_doc_generator",
                "description": "Generates API documentation from OpenAPI specs",
                "input_schema": {"type": "object", "properties": {"spec_file": {"type": "string"}}},
                "output_schema": {"type": "object", "properties": {"markdown": {"type": "string"}}},
                "implementation": "def generate_docs(spec_file):\n    # Implementation\n    return {'markdown': '# API Documentation'}"
            }
            mock_create_tool.return_value = mock_tool
            
            # Make the request
            response = self.client.post(f"{self.base_url}/create-tool", json=self.tool_creation_request_data)
            
            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertEqual(data["message"], "Tool created successfully")
            self.assertEqual(data["tool"]["name"], "api_doc_generator")

    # Execution Endpoint Tests
    def test_execute_plan_success(self):
        """Test successful plan execution"""
        with patch('backend.super_agent.builder.Builder.execute_plan') as mock_execute_plan:
            # Mock the builder's execute_plan method
            mock_result = {
                "success": True,
                "completed_steps": 3,
                "artifacts": ["login.jsx", "dashboard.jsx", "api.py"],
                "metrics": {"time_taken": 120, "resources_used": "minimal"}
            }
            mock_execute_plan.return_value = mock_result
            
            # Make the request
            response = self.client.post(f"{self.base_url}/execute", json=self.execution_request_data)
            
            # Assertions
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertEqual(data["message"], "Plan executed successfully")
            self.assertEqual(data["result"]["completed_steps"], 3)
            self.assertEqual(len(data["result"]["artifacts"]), 3)


if __name__ == "__main__":
    unittest.main()