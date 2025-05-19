from typing import Dict, Any
from backend.orchestrator.agent_orchestrator import AgentOrchestrator
from backend.orchestrator.event_bus import EventBus
from backend.memory.base_memory import BaseMemory
from backend.memory.global_memory import GlobalMemory

# Singleton instances
_event_bus: EventBus = None
_global_memory: BaseMemory = None
_agent_orchestrator: AgentOrchestrator = None

def get_event_bus() -> EventBus:
    """Get or create EventBus singleton."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus

def get_global_memory() -> BaseMemory:
    """Get or create GlobalMemory singleton."""
    global _global_memory
    if _global_memory is None:
        _global_memory = GlobalMemory()
    return _global_memory

async def get_agent_orchestrator() -> AgentOrchestrator:
    """Get or create AgentOrchestrator singleton with proper dependencies."""
    global _agent_orchestrator
    if _agent_orchestrator is None:
        event_bus = get_event_bus()
        shared_memory = get_global_memory()
        
        _agent_orchestrator = AgentOrchestrator(
            agents={},  # Will be populated during runtime
            event_bus=event_bus,
            shared_memory=shared_memory,
            config={
                "max_concurrent_agents": 10,
                "default_timeout": 300  # 5 minutes
            }
        )
    return _agent_orchestrator