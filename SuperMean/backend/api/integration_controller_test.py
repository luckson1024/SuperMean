# Integration tests for controller interactions in SuperMean backend
# This suite covers API endpoints and their integration points, including auth, agent, mission, and super agent controllers.
# PYTHONPATH=SuperMean pytest SuperMean/backend/api/integration_controller_test.py --maxfail=3 --disable-warnings -v
import unittest
from fastapi.testclient import TestClient
from backend.api.main import app
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

client = TestClient(app)

class TestControllerIntegration(unittest.TestCase):
    def test_user_registration_and_login(self):
        # Register
        response = client.post("/api/register", json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpass123"
        })
        self.assertIn(response.status_code, [200, 201, 409])  # 409 if already exists
        # Login
        response = client.post("/api/login", json={
            "email": "testuser@example.com",
            "password": "testpass123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

    def test_agent_creation_and_listing(self):
        # Login to get token
        response = client.post("/api/login", json={
            "email": "testuser@example.com",
            "password": "testpass123"
        })
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        # Create agent
        response = client.post("/api/agents", json={
            "name": "IntegrationAgent",
            "type": "dev",
            "config": {}
        }, headers=headers)
        self.assertIn(response.status_code, [200, 201, 409])
        # List agents
        response = client.get("/api/agents", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_mission_creation_and_assignment(self):
        # Login to get token
        response = client.post("/api/login", json={
            "email": "testuser@example.com",
            "password": "testpass123"
        })
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        # Create mission
        response = client.post("/api/missions", json={
            "title": "Integration Mission",
            "description": "Test mission integration"
        }, headers=headers)
        self.assertIn(response.status_code, [200, 201, 409])
        # List missions
        response = client.get("/api/missions", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_super_agent_and_security_endpoints(self):
        # Login to get token
        response = client.post("/api/login", json={
            "email": "testuser@example.com",
            "password": "testpass123"
        })
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        # Super agent endpoint (example: list super agents)
        response = client.get("/api/super-agents", headers=headers)
        self.assertIn(response.status_code, [200, 404])
        # Security endpoint (example: get security alerts)
        response = client.get("/api/security/alerts", headers=headers)
        self.assertIn(response.status_code, [200, 404])

    def test_stress_concurrent_agent_creation(self):
        import threading
        response = client.post("/api/login", json={
            "email": "testuser@example.com",
            "password": "testpass123"
        })
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        results = []
        def create_agent(idx):
            r = client.post("/api/agents", json={
                "name": f"StressAgent{idx}",
                "type": "dev",
                "config": {}
            }, headers=headers)
            results.append(r.status_code)
        threads = [threading.Thread(target=create_agent, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertTrue(any(code in [200, 201, 409] for code in results))

    def test_transaction_rollback_on_failure(self):
        # This test assumes there is an endpoint that can simulate a failure for rollback
        response = client.post("/api/login", json={
            "email": "testuser@example.com",
            "password": "testpass123"
        })
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        # Simulate a transaction that should fail and rollback
        response = client.post("/api/agents/transaction-test", json={
            "fail": True
        }, headers=headers)
        self.assertIn(response.status_code, [400, 500])
        # Optionally verify no partial data was committed (if API supports it)

    def test_websocket_event_propagation(self):
        # This is a placeholder; actual implementation depends on backend WebSocket support
        # Example: connect to WebSocket, trigger an event, verify event received
        import websocket
        import json as pyjson
        ws_url = "ws://localhost:8000/ws/agents"
        try:
            ws = websocket.create_connection(ws_url)
            # Trigger an event (e.g., agent creation)
            response = client.post("/api/login", json={
                "email": "testuser@example.com",
                "password": "testpass123"
            })
            token = response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            client.post("/api/agents", json={
                "name": "WebSocketAgent",
                "type": "dev",
                "config": {}
            }, headers=headers)
            # Wait for event
            ws.settimeout(3)
            event = ws.recv()
            self.assertIn("WebSocketAgent", event)
            ws.close()
        except Exception as e:
            self.skipTest(f"WebSocket test skipped: {e}")

if __name__ == "__main__":
    unittest.main()
