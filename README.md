# SuperMean

## Project Description

SuperMean is a project designed to [Provide a concise description of what SuperMean does. Based on the file structure, it seems to be an agent-based system with backend APIs, memory, models, orchestration, and skills, and a frontend interface. You might want to elaborate on its purpose, target users, or the problem it solves.].

## Features

*   **Agent System:** [Describe the agent capabilities, e.g., different types of agents like design, dev, medical, research.]
*   **Memory Management:** [Describe the memory components, e.g., global, agent, vector memory.]
*   **Model Integration:** [Describe how different AI/ML models are integrated.]
*   **Orchestration:** [Describe the orchestration capabilities, e.g., mission control, event bus.]
*   **Skills:** [Describe the skills framework and examples of skills like API building, code writing, web search.]
*   **Backend API:** [Mention the FastAPI backend for interacting with the system.]
*   **Frontend Interface:** [Mention the Next.js frontend for user interaction.]
*   **Docker Support:** [Highlight the ability to run the project using Docker Compose.]

## Technologies Used

**Backend:**
*   Python
*   FastAPI
*   Pytest (for testing)
*   pytest-cov (for test coverage)
*   ChromaDB (for vector memory)
*   [List other significant Python libraries from requirements.txt]

**Frontend:**
*   TypeScript
*   Next.js
*   React
*   Tailwind CSS
*   Cypress (for end-to-end testing)
*   [List other significant Node.js libraries from package.json]

**Other:**
*   Docker
*   Docker Compose

## Prerequisites

Before you begin, ensure you have met the following requirements:

*   Python 3.8+
*   Node.js 18+ and npm or yarn
*   Docker and Docker Compose (optional, for containerized setup)
*   Git

## Setup and Installation

You can set up the project either directly on your machine or using Docker.

### Option 1: Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/billdeluck/superMean.git
    cd superMean
    ```

2.  **Backend Setup:**
    *   Navigate to the backend directory:
        ```bash
        cd SuperMean/backend
        ```
    *   Create a Python virtual environment (recommended):
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows use `venv\Scripts\activate`
        ```
    *   Install backend dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    *   [Mention any necessary environment variable setup, e.g., creating a `.env` file based on a template if one exists.]

3.  **Frontend Setup:**
    *   Navigate to the frontend directory:
        ```bash
        cd ../../SuperMean/frontend
        ```
    *   Install frontend dependencies:
        ```bash
        npm install # or yarn install
        ```
    *   [Mention any necessary environment variable setup for the frontend.]

### Option 2: Docker Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/billdeluck/superMean.git
    cd superMean
    ```
2.  **Build and run the Docker containers:**
    ```bash
    docker-compose up --build
    ```
    This will build the backend and frontend images and start the services.

## Running the Project

### Option 1: Local Execution

1.  **Start the Backend:**
    *   Navigate to the backend directory:
        ```bash
        cd SuperMean/backend
        ```
    *   Activate the virtual environment:
        ```bash
        source venv/bin/activate # On Windows use `venv\Scripts\activate`
        ```
    *   Run the backend server:
        ```bash
        uvicorn run:app --reload # Or the appropriate command to start your FastAPI app
        ```
        [Adjust the command based on how your FastAPI app is started, e.g., `python run.py`]

2.  **Start the Frontend:**
    *   Navigate to the frontend directory:
        ```bash
        cd ../../SuperMean/frontend
        ```
    *   Run the frontend development server:
        ```bash
        npm run dev # or yarn dev
        ```

The frontend should be accessible at `http://localhost:3000` (or the configured port) and the backend API at `http://localhost:8000` (or the configured port).

### Option 2: Docker Execution

If you used the Docker setup, the services should already be running after executing `docker-compose up --build`.

*   The frontend will be accessible at `http://localhost:3000`.
*   The backend API will be accessible at `http://localhost:8000`.

To stop the Docker containers:
```bash
docker-compose down
```

## Project Structure

```
superMean/
├── .github/workflows/  # GitHub Actions workflows (e.g., CI/CD)
├── SuperMean/
│   ├── backend/        # Backend Python application
│   │   ├── agents/     # Agent implementations
│   │   ├── api/        # FastAPI endpoints and related logic
│   │   ├── memory/     # Memory management components
│   │   ├── models/     # AI/ML model connectors and routing
│   │   ├── orchestrator/ # Task orchestration and event handling
│   │   ├── skills/     # Agent skills
│   │   ├── super_agent/ # Super agent logic
│   │   ├── utils/      # Utility functions
│   │   ├── requirements.txt # Python dependencies
│   │   └── ...
│   ├── frontend/       # Frontend Node.js/TypeScript application
│   │   ├── components/ # Reusable UI components
│   │   ├── cypress/    # End-to-end tests
│   │   ├── pages/      # Next.js pages
│   │   ├── services/   # API and WebSocket services
│   │   ├── store/      # State management (e.g., Zustand, Redux)
│   │   ├── utils/      # Frontend utility functions
│   │   ├── package.json # Node.js dependencies
│   │   └── ...
│   ├── docs/           # Documentation files
│   └── ...
├── docker-compose.yml  # Docker Compose configuration
├── Dockerfile.backend  # Dockerfile for the backend
├── Dockerfile.frontend # Dockerfile for the frontend
├── README.md           # Project README
└── ...
```

## Contributing

[Explain how others can contribute to the project. This might include guidelines for submitting issues, proposing features, or submitting pull requests.]

## License

[Specify the project's license, e.g., MIT, Apache 2.0. If you don't have a specific license yet, you can state that or add a LICENSE file.]
