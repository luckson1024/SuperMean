# Directory: backend/agents/
# File: security_agent_test.py
# Description: Tests for SecurityAgent monitoring and threat detection.

import unittest
import asyncio
import tempfile
import os
import shutil
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pathlib import Path

from backend.agents.security_agent import SecurityAgent
from backend.models.model_router import ModelRouter
from backend.memory.base_memory import BaseMemory
from backend.skills import SkillError
from backend.utils.logger import setup_logger

class TestSecurityAgent(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        # Initialize mocks
        self.mock_router = Mock(spec=ModelRouter)
        self.mock_router.generate = AsyncMock()
        self.mock_router.generate.return_value = "Test LLM Response"
        
        self.mock_memory = Mock(spec=BaseMemory)
        self.mock_memory.remember = AsyncMock()
        self.mock_memory.recall = AsyncMock()
        self.mock_memory.recall.return_value = None
        
        self.mock_skill_executor = AsyncMock()
        
        # Initialize agent
        from backend.models.model_router import ModelRouter
        from backend.memory.agent_memory import AgentMemory
        from typing import Callable
        self.mock_router = Mock(spec=ModelRouter)
        self.mock_memory = Mock(spec=BaseMemory)
        self.mock_skill_executor = Mock()
        self.agent = SecurityAgent(
            name="test_security_agent",
            description="Security monitoring agent",
            model_router=self.mock_router,
            agent_memory=self.mock_memory,
            execute_skill_func=self.mock_skill_executor
        )
        
        # Create temporary directory for file tests
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: self.cleanup_test_dir())

    def run_async(self, coro):
        """Helper to run async code in tests."""
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_initialization(self):
        """Test agent initialization."""
        self.assertIsNotNone(self.agent.file_observer)
        self.assertIsNotNone(self.agent.event_handler)
        self.assertTrue(self.agent.file_observer.is_alive())

    def test_suspicious_patterns(self):
        """Test suspicious pattern detection."""
        patterns = self.agent._load_suspicious_patterns()
        self.assertIn('sql_injection', patterns)
        self.assertIn('xss', patterns)
        self.assertIn('command_injection', patterns)
        self.assertIn('file_operations', patterns)

    @patch('backend.agents.security_agent.open')
    async def test_file_security_analysis(self):
        """Test file security analysis."""
        test_file = Path(self.test_dir) / "test.py"
        test_content = """
        import os
        
        def unsafe_function():
            user_input = input()
            os.system(user_input)  # Command injection vulnerability
            eval(user_input)       # Code execution vulnerability
        """
        
        mock_open = MagicMock()
        mock_open.return_value.__enter__.return_value.read.return_value = test_content
        
        with patch('backend.agents.security_agent.open', mock_open):
            threats = await self.agent.analyze_file_security(str(test_file))
            
        self.assertTrue(any(t['type'] == 'command_injection' for t in threats))

    async def test_sql_injection_check(self):
        """Test SQL injection detection."""
        user_input = "1' OR '1'='1"  # Simulated malicious input
        unsafe_query = f"SELECT * FROM users WHERE id = '{user_input}'"
        safe_query = "SELECT * FROM users WHERE id = ?"
        
        unsafe_result = await self.agent.check_sql_injection(unsafe_query)
        safe_result = await self.agent.check_sql_injection(safe_query)
        
        self.assertFalse(unsafe_result['is_safe'])
        self.assertTrue(safe_result['is_safe'])
        self.assertTrue(any('parameterized' in r.lower() for r in unsafe_result['recommendations']))

    def test_cleanup(self):
        """Test cleanup of monitoring resources."""
        self.agent.cleanup()
        self.assertFalse(self.agent.file_observer.is_alive())

if __name__ == '__main__':
    unittest.main()
