# Directory: backend/orchestrator/
# File: agent_orchestrator.py
# Description: Advanced orchestration system for managing multi-agent collaboration and communication.

import asyncio
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from backend.agents.base_agent import BaseAgent
from backend.orchestrator.event_bus import EventBus
from backend.memory.base_memory import BaseMemory
from backend.memory.agent_memory import AgentMemory
from backend.utils.logger import setup_logger
from backend.utils.error_handler import SuperMeanException

# Logger setup
log = setup_logger(name="agent_orchestrator")

class OrchestrationError(SuperMeanException):
    """Custom exception for agent orchestration failures."""
    def __init__(self, message="Agent orchestration operation failed", status_code=500, cause: Optional[Exception] = None):
        super().__init__(message, status_code)
        if cause:
            self.__cause__ = cause

class AgentOrchestrator:
    """
    Advanced orchestration system for managing multi-agent collaboration and communication.
    Enables dynamic agent allocation, parallel execution, and robust communication between agents.
    
    Features:
    - Dynamic agent allocation based on task requirements
    - Parallel execution of compatible agent tasks
    - Robust inter-agent communication channels
    - Centralized context management for shared knowledge
    - Automatic fallback mechanisms for agent failures
    - Performance monitoring and optimization
    """
    
    def __init__(
        self,
        agents: Dict[str, BaseAgent],
        event_bus: EventBus,
        shared_memory: Optional[BaseMemory] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the AgentOrchestrator with available agents and communication channels.
        
        Args:
            agents: Dictionary of available agent instances by name
            event_bus: Event bus for inter-agent communication
            shared_memory: Optional shared memory for cross-agent context
            config: Optional configuration settings
        """
        self.agents = agents
        self.event_bus = event_bus
        self.shared_memory = shared_memory
        self.config = config or {}
        
        # Track active agent tasks
        self.active_tasks: Dict[str, asyncio.Task] = {}
        # Track agent capabilities for dynamic allocation
        self.agent_capabilities: Dict[str, Set[str]] = {}
        
        # Initialize agent capabilities map
        for agent_name, agent in self.agents.items():
            if hasattr(agent, 'capabilities') and isinstance(agent.capabilities, (list, set)):
                self.agent_capabilities[agent_name] = set(agent.capabilities)
            else:
                self.agent_capabilities[agent_name] = set()
                log.warning(f"Agent {agent_name} does not define capabilities")
        
        # Maximum concurrent agents (configurable with fallback to system default)
        self.max_concurrent_agents = self.config.get("max_concurrent_agents", 10)
        
        log.info(f"AgentOrchestrator initialized with {len(agents)} agents")
    
    async def allocate_agent(self, required_capabilities: List[str]) -> Optional[str]:
        """
        Dynamically allocate the most suitable agent based on required capabilities.
        
        Args:
            required_capabilities: List of capabilities needed for the task
            
        Returns:
            Name of the most suitable agent, or None if no suitable agent found
        """
        if not required_capabilities:
            log.warning("No capabilities specified for agent allocation")
            return None
            
        # Convert to set for faster lookups
        required_set = set(required_capabilities)
        
        # Find agents that match all required capabilities
        matching_agents = []
        for agent_name, capabilities in self.agent_capabilities.items():
            # Check if agent is available (not at capacity)
            if agent_name in self.active_tasks and len(self.active_tasks) >= self.max_concurrent_agents:
                continue
                
            # Calculate capability match score (percentage of required capabilities)
            if capabilities.intersection(required_set):
                match_score = len(capabilities.intersection(required_set)) / len(required_set)
                matching_agents.append((agent_name, match_score))
        
        # Sort by match score (highest first)
        matching_agents.sort(key=lambda x: x[1], reverse=True)
        
        if matching_agents:
            best_agent = matching_agents[0][0]
            log.info(f"Allocated agent {best_agent} for capabilities {required_capabilities}")
            return best_agent
        else:
            log.warning(f"No suitable agent found for capabilities {required_capabilities}")
            return None
    
    async def execute_agent_task(self, agent_name: str, task_data: Dict[str, Any], task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a task with the specified agent.
        
        Args:
            agent_name: Name of the agent to execute the task
            task_data: Task data including instructions and context
            task_id: Optional task ID (generated if not provided)
            
        Returns:
            Task result dictionary
        """
        if agent_name not in self.agents:
            raise OrchestrationError(f"Agent '{agent_name}' not found")
            
        task_id = task_id or str(uuid.uuid4())
        agent = self.agents[agent_name]
        
        try:
            # Create task context with shared memory access
            context = {
                "task_id": task_id,
                "shared_memory": self.shared_memory,
                **task_data
            }
            
            # Execute agent task
            log.info(f"Executing task {task_id} with agent {agent_name}")
            result = await agent.execute_task(context)
            
            # Publish task completion event
            await self.event_bus.publish(
                "agent.task.completed",
                {
                    "task_id": task_id,
                    "agent": agent_name,
                    "status": "completed",
                    "result": result
                }
            )
            
            return {
                "task_id": task_id,
                "agent": agent_name,
                "status": "completed",
                "result": result
            }
            
        except Exception as e:
            log.exception(f"Error executing task {task_id} with agent {agent_name}: {e}")
            
            # Publish task failure event
            await self.event_bus.publish(
                "agent.task.failed",
                {
                    "task_id": task_id,
                    "agent": agent_name,
                    "status": "failed",
                    "error": str(e)
                }
            )
            
            raise OrchestrationError(f"Task execution failed with agent {agent_name}", cause=e)
    
    async def execute_parallel_tasks(self, task_assignments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple agent tasks in parallel.
        
        Args:
            task_assignments: List of task assignment dictionaries, each containing:
                - agent_name: Name of the agent to execute the task
                - task_data: Task data including instructions and context
                - task_id: Optional task ID
                
        Returns:
            List of task result dictionaries
        """
        if len(task_assignments) > self.max_concurrent_agents:
            log.warning(f"Requested {len(task_assignments)} parallel tasks, but max is {self.max_concurrent_agents}")
        
        # Create tasks
        tasks = []
        for assignment in task_assignments:
            agent_name = assignment.get("agent_name")
            task_data = assignment.get("task_data", {})
            task_id = assignment.get("task_id")
            
            if not agent_name:
                log.error(f"Missing agent_name in task assignment: {assignment}")
                continue
                
            task = asyncio.create_task(
                self.execute_agent_task(agent_name, task_data, task_id)
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Handle exception
                task_id = task_assignments[i].get("task_id", f"unknown-{i}")
                agent_name = task_assignments[i].get("agent_name", "unknown")
                log.error(f"Task {task_id} with agent {agent_name} failed: {result}")
                
                processed_results.append({
                    "task_id": task_id,
                    "agent": agent_name,
                    "status": "failed",
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def create_agent_collaboration(self, agents: List[str], shared_context: Dict[str, Any]) -> str:
        """
        Create a collaboration session between multiple agents with shared context.
        
        Args:
            agents: List of agent names to include in the collaboration
            shared_context: Shared context data for the collaboration
            
        Returns:
            Collaboration session ID
        """
        # Generate collaboration ID
        collaboration_id = str(uuid.uuid4())
        
        # Validate agents
        valid_agents = [agent for agent in agents if agent in self.agents]
        if len(valid_agents) != len(agents):
            invalid_agents = set(agents) - set(valid_agents)
            log.warning(f"Some agents not found for collaboration: {invalid_agents}")
        
        if not valid_agents:
            raise OrchestrationError("No valid agents specified for collaboration")
        
        # Create shared memory for collaboration
        if self.shared_memory:
            # Store collaboration context in shared memory
            await self.shared_memory.store(
                f"collaboration:{collaboration_id}:context",
                shared_context,
                {"agents": valid_agents, "created_at": asyncio.get_event_loop().time()}
            )
            
            # Register agents in collaboration
            await self.shared_memory.store(
                f"collaboration:{collaboration_id}:agents",
                valid_agents
            )
        
        # Publish collaboration creation event
        await self.event_bus.publish(
            "agent.collaboration.created",
            {
                "collaboration_id": collaboration_id,
                "agents": valid_agents,
                "context": shared_context
            }
        )
        
        log.info(f"Created collaboration {collaboration_id} with agents {valid_agents}")
        return collaboration_id
    
    async def send_collaboration_message(self, collaboration_id: str, sender: str, message: Dict[str, Any]) -> bool:
        """
        Send a message within a collaboration session.
        
        Args:
            collaboration_id: Collaboration session ID
            sender: Name of the sending agent
            message: Message data
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        if not self.shared_memory:
            log.error("Shared memory required for collaboration messaging")
            return False
        
        # Verify collaboration exists
        agents_data = await self.shared_memory.retrieve(f"collaboration:{collaboration_id}:agents")
        if not agents_data:
            log.error(f"Collaboration {collaboration_id} not found")
            return False
        
        # Verify sender is part of collaboration
        if sender not in agents_data:
            log.error(f"Agent {sender} is not part of collaboration {collaboration_id}")
            return False
        
        # Add message to collaboration history
        message_id = str(uuid.uuid4())
        message_data = {
            "id": message_id,
            "sender": sender,
            "timestamp": asyncio.get_event_loop().time(),
            "content": message
        }
        
        # Store message in shared memory
        await self.shared_memory.store(
            f"collaboration:{collaboration_id}:message:{message_id}",
            message_data
        )
        
        # Update message index
        message_index = await self.shared_memory.retrieve(f"collaboration:{collaboration_id}:messages") or []
        message_index.append(message_id)
        await self.shared_memory.store(f"collaboration:{collaboration_id}:messages", message_index)
        
        # Publish message event
        await self.event_bus.publish(
            "agent.collaboration.message",
            {
                "collaboration_id": collaboration_id,
                "message": message_data
            }
        )
        
        log.info(f"Sent message in collaboration {collaboration_id} from {sender}")
        return True
    
    async def get_collaboration_messages(self, collaboration_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent messages from a collaboration session.
        
        Args:
            collaboration_id: Collaboration session ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        if not self.shared_memory:
            log.error("Shared memory required for collaboration messaging")
            return []
        
        # Get message index
        message_index = await self.shared_memory.retrieve(f"collaboration:{collaboration_id}:messages") or []
        
        # Get most recent messages up to limit
        recent_message_ids = message_index[-limit:] if len(message_index) > limit else message_index
        
        # Retrieve message data
        messages = []
        for message_id in recent_message_ids:
            message_data = await self.shared_memory.retrieve(f"collaboration:{collaboration_id}:message:{message_id}")
            if message_data:
                messages.append(message_data)
        
        return messages
    
    async def close_collaboration(self, collaboration_id: str) -> bool:
        """
        Close a collaboration session.
        
        Args:
            collaboration_id: Collaboration session ID
            
        Returns:
            True if collaboration was closed successfully, False otherwise
        """
        if not self.shared_memory:
            log.error("Shared memory required for collaboration management")
            return False
        
        # Verify collaboration exists
        agents_data = await self.shared_memory.retrieve(f"collaboration:{collaboration_id}:agents")
        if not agents_data:
            log.error(f"Collaboration {collaboration_id} not found")
            return False
        
        # Publish collaboration closure event
        await self.event_bus.publish(
            "agent.collaboration.closed",
            {"collaboration_id": collaboration_id}
        )
        
        log.info(f"Closed collaboration {collaboration_id}")
        return True
    
    async def initialize_agent(self, agent_name: str, agent_type: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initialize a new agent of the specified type with the given configuration.
        
        Args:
            agent_name: Name of the agent
            agent_type: Type of agent to create
            config: Optional configuration for the agent
            
        Returns:
            Initialization result
        """
        # Create task data for initialization
        task_data = {
            "action": "initialize",
            "agent_type": agent_type,
            "config": config or {}
        }
        
        try:
            result = await self.execute_agent_task(agent_name, task_data)
            
            if result.get("status") == "completed":
                # Store agent type and config
                if self.shared_memory:
                    await self.shared_memory.store(
                        f"agent:{agent_name}:config",
                        {
                            "agent_type": agent_type,
                            "config": config
                        }
                    )
                
                log.info(f"Successfully initialized agent {agent_name} of type {agent_type}")
                return {
                    "status": "success",
                    "message": f"Agent {agent_name} initialized successfully",
                    "agent_type": agent_type
                }
            else:
                raise OrchestrationError(f"Failed to initialize agent {agent_name}: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            log.error(f"Error initializing agent {agent_name}: {e}")
            raise OrchestrationError(f"Failed to initialize agent {agent_name}", cause=e)