# SuperMean Memory System

## Overview

The SuperMean memory system provides a flexible and powerful way to store and retrieve information for AI agents. The system includes several memory implementations:

- **BaseMemory**: Abstract base class that defines the memory interface
- **AgentMemory**: Simple in-memory implementation for single agent use
- **GlobalMemory**: Persistent memory using ChromaDB for system-wide storage
- **VectorMemory**: Advanced vector-based memory with multi-agent support

## VectorMemory: Multi-Agent Memory System

The `VectorMemory` class extends the existing memory implementation to support shared contexts between agents. It enables robust integration between SuperAgent and specialized agents while supporting dynamic skill loading requirements.

### Key Features

1. **Namespaced Memory Segments**
   - Each agent has its own isolated memory namespace
   - System-level global namespace accessible by all agents
   - Custom shared namespaces for collaborative tasks

2. **Memory Isolation Controls**
   - Fine-grained access permissions for each namespace
   - Ability to grant and revoke access to specific agents
   - Protection of sensitive information between agents

3. **Cross-Agent Memory Permissions**
   - Explicit permission management for shared contexts
   - Default isolation with opt-in sharing model
   - Hierarchical permission structure

4. **Memory Synchronization**
   - Thread-safe operations with namespace locks
   - Ability to sync specific data between namespaces
   - Persistent storage with automatic saving

5. **Vector-Based Similarity Search**
   - Efficient retrieval of semantically similar information
   - Configurable embedding function support
   - Metadata filtering capabilities

## Usage Examples

### Basic Usage

```python
# Create a memory instance
memory = VectorMemory(config={"vector_dim": 1536})

# Store a value
await memory.store("key1", "This is some important information")

# Retrieve a value
value = await memory.retrieve("key1")

# Search for similar information
results = await memory.search("important info", top_k=5)
```

### Multi-Agent Usage

```python
# Create agent-specific memory instances
agent1_memory = VectorMemory(config=config, agent_id="agent1")
agent2_memory = VectorMemory(config=config, agent_id="agent2")

# Store private data for agent1
await agent1_memory.store("private_key", "Agent 1's private data")

# Store in global namespace (accessible by all)
await agent1_memory.store("shared_key", "Globally shared data", namespace="global")

# Agent2 can access global data
shared_data = await agent2_memory.retrieve("shared_key", namespace="global")
```

### Shared Contexts

```python
# Agent1 creates a shared context
context_id = "collaborative_task"
namespace = await agent1_memory.create_shared_context(context_id, {
    "task_description": "Collaborative task between agents"
})

# Agent1 adds data to the shared context
await agent1_memory.switch_namespace(namespace)
await agent1_memory.store("agent1_contribution", "Data from Agent 1")

# Agent2 joins the shared context
await agent2_memory.join_shared_context(context_id)

# Agent2 can now read and write to the shared context
data = await agent2_memory.retrieve("agent1_contribution")
await agent2_memory.store("agent2_contribution", "Data from Agent 2")
```

## Installation

The VectorMemory implementation requires the following dependencies:

- faiss-cpu: For efficient vector storage and similarity search
- numpy: Required by faiss for vector operations

Install dependencies using:

```bash
pip install -r requirements.txt
```

## Testing

Run the tests to verify the multi-agent memory functionality:

```bash
python -m backend.memory.vector_memory_test
```