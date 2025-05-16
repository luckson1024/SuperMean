# SuperMean System

A powerful agent-based system with long-term memory capabilities for advanced AI tasks.

## System Overview

SuperMean is a comprehensive agent-based system that combines multiple specialized agents with a sophisticated memory architecture. The system enables complex AI tasks through agent collaboration, meta-planning, and persistent memory capabilities.

### Key Components

- **Specialized Agents**: Development, Design, Research, and Medical agents with specific capabilities
- **Memory System**: Hierarchical memory architecture with agent-specific and global memory
- **Super Agent**: Meta-planning and orchestration capabilities
- **Model Router**: Intelligent routing to appropriate AI models based on task requirements

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (recommended: venv or conda)

### Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/superMean.git
   cd superMean
   ```

2. Create and activate a virtual environment:
   ```bash
   # Using venv
   python -m venv venv
   
   # On Windows
   .\venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r SuperMean/backend/requirements.txt
   ```

### Configuration

1. Set up API keys for AI models:
   - Create a `.env` file in the `SuperMean/backend` directory
   - Add your API keys:
     ```
     OPENAI_API_KEY=your_openai_key
     GEMINI_API_KEY=your_gemini_key
     DEEPSEEK_API_KEY=your_deepseek_key
     ```

2. Configure memory storage:
   - By default, the system uses local vector storage
   - For production, configure a persistent database in the config files

## Usage

### Running Tests

To verify your installation, run the comprehensive test suite:

```bash
cd SuperMean/backend
python run.py
```

You can also run tests for specific modules:

```bash
python run.py --modules agents memory super_agent
```

Add the `--verbose` flag for more detailed output:

```bash
python run.py --verbose
```

### Starting the API Server

To start the API server:

```bash
cd SuperMean/backend
python -m api.main
```

The API will be available at `http://localhost:8000` by default.

### Using the System

1. **Creating a Mission**:
   - Send a POST request to `/mission/create` with your mission details
   - The system will analyze the mission and assign appropriate agents

2. **Agent Interaction**:
   - Agents can be directly accessed through their respective endpoints
   - For example, `/agents/dev` for the development agent

3. **Monitoring**:
   - Check mission status at `/mission/{mission_id}`
   - View agent activities at `/agents/{agent_id}/activities`

## Development

### Adding New Agents

To create a new specialized agent:

1. Extend the `BaseAgent` class in the `agents` directory
2. Implement the required methods (`run`, etc.)
3. Register the agent in the agent registry

### Extending Memory Capabilities

The memory system can be extended by:

1. Creating new memory types that inherit from `BaseMemory`
2. Implementing custom storage and retrieval methods
3. Registering the new memory type with the memory system

## Troubleshooting

### Common Issues

- **API Key Errors**: Ensure all required API keys are correctly set in the `.env` file
- **Memory Errors**: Check that the vector database is properly configured and accessible
- **Agent Failures**: Review the logs for specific agent errors in the `logs` directory

### Logging

Logs are stored in the `logs` directory with the following structure:

- `system.log`: Overall system logs
- `agents/*.log`: Individual agent logs
- `memory/*.log`: Memory system logs

## License

This project is licensed under the MIT License - see the LICENSE file for details.