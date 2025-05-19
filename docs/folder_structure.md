# Folder Structure

```
SuperMean/
├── backend/
│   ├── api/                 # API Layer
│   │   ├── controllers/     # HTTP endpoint handlers
│   │   ├── middleware/      # Request/response middleware
│   │   ├── models/         # Database models
│   │   └── schemas/        # Request/response schemas
│   │
│   ├── orchestrator/        # Orchestration Layer
│   │   ├── agent_orchestrator.py    # Agent management
│   │   ├── mission_control.py       # Mission coordination
│   │   └── event_bus.py            # Event system
│   │
│   ├── agents/             # Agent Layer
│   │   ├── base_agent.py   # Base agent class
│   │   ├── design_agent.py # Design specialist
│   │   ├── dev_agent.py    # Development specialist
│   │   └── medical_agent.py # Medical specialist
│   │
│   ├── memory/             # Memory Layer
│   │   ├── base_memory.py  # Memory interface
│   │   ├── agent_memory.py # Agent-specific storage
│   │   └── vector_memory.py # Vector storage
│   │
│   ├── super_agent/        # SuperAgent Layer
│   │   ├── planner.py      # Task planning
│   │   ├── builder.py      # Plan execution
│   │   ├── evaluator.py    # Result evaluation
│   │   └── tool_creator.py # Tool creation
│   │
│   └── utils/              # Shared utilities
│       ├── logger.py       # Logging
│       └── error_handler.py # Error handling
│
├── frontend/               # Frontend Layer
│   ├── components/         # React components
│   ├── pages/             # Page components
│   ├── services/          # API services
│   └── utils/             # Frontend utilities
│
├── docs/                  # Documentation
│   ├── architecture.md    # System architecture
│   └── api/              # API documentation
│
└── tests/                # Test suite
    ├── unit/            # Unit tests
    ├── integration/     # Integration tests
    └── e2e/            # End-to-end tests
```

## Key Notes

1. **API Layer Organization**:
   - Controllers are separated by domain
   - Middleware handles cross-cutting concerns
   - Models define database structure
   - Schemas validate request/response data

2. **Orchestration Layer Structure**:
   - Agent orchestrator manages agent lifecycle
   - Mission control handles task coordination
   - Event bus enables communication

3. **Agent Layer Components**:
   - Base agent defines common interface
   - Specialized agents implement domain logic
   - Each agent has corresponding tests

4. **Memory Layer Design**:
   - Base memory defines interface
   - Different memory implementations
   - Vector memory for efficient storage

5. **SuperAgent Layer**:
   - Core components for meta-agent system
   - Each component has single responsibility
   - Clear separation of concerns

6. **Testing Organization**:
   - Unit tests per component
   - Integration tests for layers
   - End-to-end tests for workflows

## Best Practices

1. **File Naming**:
   - Use lowercase with underscores
   - Add suffixes for types (_controller, _model, etc.)
   - Keep names descriptive and concise

2. **Module Organization**:
   - Group related functionality
   - Maintain clear dependencies
   - Avoid circular imports

3. **Documentation**:
   - Keep architecture docs updated
   - Document public interfaces
   - Include usage examples

4. **Testing**:
   - Match test structure to source
   - Include both positive and negative tests
   - Maintain high coverage
