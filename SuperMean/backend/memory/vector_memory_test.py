# Directory: backend/memory/
# File: vector_memory_test.py
# Description: Tests for the VectorMemory implementation with multi-agent support.

import sys
import os
import unittest
import asyncio
from typing import Dict, Any, List, Optional

# Adjust path if necessary to run from root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    # Import the VectorMemory class
    from backend.memory.vector_memory import VectorMemory
    print("Imported VectorMemory successfully.")
    
    class TestVectorMemory(unittest.TestCase):
        
        def setUp(self):
            # Create a temporary directory for test indices
            self.test_index_path = "./test_vector_memory_index"
            os.makedirs(self.test_index_path, exist_ok=True)
            
            # Configuration for testing
            self.config = {
                "vector_dim": 128,  # Smaller dimension for testing
                "index_path": self.test_index_path
            }
            
            print(f"\n--- Starting test: {self._testMethodName} ---")
        
        def tearDown(self):
            # Clean up test files
            for file in os.listdir(self.test_index_path):
                try:
                    os.remove(os.path.join(self.test_index_path, file))
                except Exception as e:
                    print(f"Error removing file {file}: {e}")
            
            try:
                os.rmdir(self.test_index_path)
            except Exception as e:
                print(f"Error removing directory {self.test_index_path}: {e}")
        
        def run_async(self, coro):
            # Helper to run async tests
            return asyncio.run(coro)
        
        def test_basic_store_retrieve(self):
            """Test basic storage and retrieval functionality."""
            async def test_coroutine():
                # Create memory instance
                memory = VectorMemory(config=self.config)
                
                # Store a value
                key = "test_key"
                value = "This is a test value"
                result = await memory.store(key, value)
                self.assertTrue(result)
                
                # Retrieve the value
                retrieved = await memory.retrieve(key)
                self.assertIsNotNone(retrieved)
                self.assertEqual(retrieved.get("key"), key)
                
                print("Basic store/retrieve test passed.")
            
            self.run_async(test_coroutine())
        
        def test_multi_agent_isolation(self):
            """Test that different agents have isolated memory spaces."""
            async def test_coroutine():
                # Create memory instances for two agents
                agent1_memory = VectorMemory(config=self.config, agent_id="agent1")
                agent2_memory = VectorMemory(config=self.config, agent_id="agent2")
                
                # Agent 1 stores a value
                key = "private_data"
                value = "Agent 1's private data"
                result = await agent1_memory.store(key, value)
                self.assertTrue(result)
                
                # Agent 1 should be able to retrieve it
                retrieved = await agent1_memory.retrieve(key)
                self.assertIsNotNone(retrieved)
                
                # Agent 2 should not be able to retrieve it
                retrieved = await agent2_memory.retrieve(key)
                self.assertIsNone(retrieved)
                
                print("Multi-agent isolation test passed.")
            
            self.run_async(test_coroutine())
        
        def test_global_namespace_access(self):
            """Test that all agents can access the global namespace."""
            async def test_coroutine():
                # Create memory instances
                system_memory = VectorMemory(config=self.config)
                agent1_memory = VectorMemory(config=self.config, agent_id="agent1")
                
                # Store in global namespace
                key = "global_data"
                value = "Data for all agents"
                result = await system_memory.store(key, value)
                self.assertTrue(result)
                
                # Agent should be able to retrieve from global namespace
                retrieved = await agent1_memory.retrieve(key, namespace="global")
                self.assertIsNotNone(retrieved)
                
                print("Global namespace access test passed.")
            
            self.run_async(test_coroutine())
        
        def test_shared_context(self):
            """Test creating and using shared contexts between agents."""
            async def test_coroutine():
                # Create memory instances for two agents
                agent1_memory = VectorMemory(config=self.config, agent_id="agent1")
                agent2_memory = VectorMemory(config=self.config, agent_id="agent2")
                
                # Agent 1 creates a shared context
                context_id = "collaborative_task"
                namespace = await agent1_memory.create_shared_context(context_id, {
                    "task_description": "Collaborative task between agents"
                })
                
                # Agent 1 adds data to the shared context
                await agent1_memory.switch_namespace(namespace)
                await agent1_memory.store("agent1_contribution", "Data from Agent 1")
                
                # Agent 2 joins the shared context
                result = await agent2_memory.join_shared_context(context_id)
                self.assertTrue(result)
                
                # Agent 2 should be able to read Agent 1's data
                retrieved = await agent2_memory.retrieve("agent1_contribution")
                self.assertIsNotNone(retrieved)
                
                # Agent 2 adds its own data
                await agent2_memory.store("agent2_contribution", "Data from Agent 2")
                
                # Agent 1 should be able to read Agent 2's data
                retrieved = await agent1_memory.retrieve("agent2_contribution")
                self.assertIsNotNone(retrieved)
                
                print("Shared context test passed.")
            
            self.run_async(test_coroutine())
        
        def test_namespace_permissions(self):
            """Test granting and revoking namespace access permissions."""
            async def test_coroutine():
                # Create memory instances
                agent1_memory = VectorMemory(config=self.config, agent_id="agent1")
                agent2_memory = VectorMemory(config=self.config, agent_id="agent2")
                agent3_memory = VectorMemory(config=self.config, agent_id="agent3")
                
                # Agent 1 creates a namespace and stores data
                await agent1_memory.store("sensitive_data", "Confidential information")
                
                # Agent 2 should not have access initially
                retrieved = await agent2_memory.retrieve("sensitive_data", namespace="agent1")
                self.assertIsNone(retrieved)
                
                # Agent 1 grants access to Agent 2
                result = await agent1_memory.grant_namespace_access("agent1", "agent2")
                self.assertTrue(result)
                
                # Now Agent 2 should have access
                retrieved = await agent2_memory.retrieve("sensitive_data", namespace="agent1")
                self.assertIsNotNone(retrieved)
                
                # Agent 3 should still not have access
                retrieved = await agent3_memory.retrieve("sensitive_data", namespace="agent1")
                self.assertIsNone(retrieved)
                
                # Agent 1 revokes access from Agent 2
                result = await agent1_memory.revoke_namespace_access("agent1", "agent2")
                self.assertTrue(result)
                
                # Agent 2 should no longer have access
                retrieved = await agent2_memory.retrieve("sensitive_data", namespace="agent1")
                self.assertIsNone(retrieved)
                
                print("Namespace permissions test passed.")
            
            self.run_async(test_coroutine())
        
        def test_vector_search(self):
            """Test vector-based similarity search."""
            async def test_coroutine():
                # Create memory instance
                memory = VectorMemory(config=self.config)
                
                # Store some test data
                await memory.store("doc1", "The quick brown fox jumps over the lazy dog")
                await memory.store("doc2", "A fox that is quick and brown jumps over dogs that are lazy")
                await memory.store("doc3", "The five boxing wizards jump quickly")
                await memory.store("doc4", "How vexingly quick daft zebras jump")
                await memory.store("doc5", "Sphinx of black quartz, judge my vow")
                
                # Search for similar documents
                results = await memory.search("quick fox jumping", top_k=3)
                
                # Should return at least some results
                self.assertGreater(len(results), 0)
                
                # First result should be most similar (doc1 or doc2)
                first_key = results[0]["key"]
                self.assertIn(first_key, ["doc1", "doc2"])
                
                print("Vector search test passed.")
            
            self.run_async(test_coroutine())
        
        def test_sync_with_global(self):
            """Test synchronizing data from global namespace to agent namespace."""
            async def test_coroutine():
                # Create memory instances
                system_memory = VectorMemory(config=self.config)
                agent_memory = VectorMemory(config=self.config, agent_id="agent1")
                
                # Store data in global namespace
                await system_memory.store("global_key1", "Global value 1")
                await system_memory.store("global_key2", "Global value 2")
                
                # Sync specific keys to agent namespace
                synced = await agent_memory.sync_with_global(["global_key1"])
                self.assertEqual(synced, 1)
                
                # Agent should now have the synced key in its namespace
                retrieved = await agent_memory.retrieve("global_key1")
                self.assertIsNotNone(retrieved)
                
                # But not the other global key
                retrieved = await agent_memory.retrieve("global_key2")
                self.assertIsNone(retrieved)
                
                print("Sync with global test passed.")
            
            self.run_async(test_coroutine())
    
    # Run the tests
    print("\nRunning VectorMemory tests...")
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(TestVectorMemory))
    runner = unittest.TextTestRunner()
    runner.run(suite)

except ImportError as e:
    print(f"Failed to import VectorMemory: {e}")
    print("Ensure backend/memory/vector_memory.py exists and is importable.")
except Exception as e:
    print(f"An error occurred during VectorMemory test setup: {e}")