# SuperMean System Installation Guide

This document provides detailed instructions for installing and configuring the SuperMean system for development and production environments.

## System Requirements

### Hardware Requirements

- **CPU**: 4+ cores recommended for running multiple agents
- **RAM**: Minimum 8GB, 16GB+ recommended
- **Storage**: 10GB+ free space

### Software Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.8 or higher
- **Package Manager**: pip (latest version)
- **Virtual Environment**: venv, conda, or similar

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/superMean.git
cd superMean
```

### 2. Set Up Virtual Environment

#### Windows

```bash
python -m venv venv
.\venv\Scripts\activate
```

#### macOS/Linux

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r SuperMean/backend/requirements.txt
```

### 4. Configure Environment Variables

1. Navigate to the backend directory:
   ```bash
   cd SuperMean/backend
   ```

2. Create a `.env` file by copying the template:
   ```bash
   cp .env.template .env
   ```

3. Edit the `.env` file with your API keys and configuration:
   ```
   # Environment
   LOG_LEVEL=INFO
   ENVIRONMENT=development
   
   # API Keys
   GEMINI_API_KEY=your_gemini_key_here
   SERPAPI_KEY=your_serpapi_key_here
   DEEPSEEK_API_KEY=your_deepseek_key_here  # Optional
   ROUTERAPI_KEY=your_routerapi_key_here    # Optional
   
   # Memory Configuration
   VECTOR_DB_PATH=./data/vector_store
   
   # Model Preferences
   DEFAULT_MODEL=gemini
   FALLBACK_MODEL=deepseek
   ```

### 5. Initialize Vector Database

Create the directory for the vector database:

```bash
mkdir -p ./data/vector_store
```

## Verification

### Run Tests

Verify your installation by running the test suite:

```bash
python run.py --verbose
```

All tests should pass successfully. If you encounter any failures, check the error messages and ensure all dependencies and API keys are correctly configured.

### Start the API Server

Start the development server to verify the API is working:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Navigate to `http://localhost:8000/docs` in your web browser to access the Swagger UI documentation.

## Production Deployment

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t supermean:latest .
   ```

2. Run the container:
   ```bash
   docker run -d -p 8000:8000 --env-file .env supermean:latest
   ```

### Server Deployment

For production deployment on a server:

1. Set up a production-ready ASGI server:
   ```bash
   pip install gunicorn uvicorn
   ```

2. Run with Gunicorn:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app
   ```

3. Set up a reverse proxy (Nginx or similar) to handle HTTPS and load balancing.

## Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Ensure all required API keys are correctly set in the `.env` file
   - Check for any whitespace or special characters in the keys

2. **Module Import Errors**:
   - Verify that all dependencies are installed: `pip install -r requirements.txt`
   - Check that you're running commands from the correct directory

3. **Memory System Errors**:
   - Ensure the vector database directory exists and is writable
   - Check for disk space issues

4. **Model Connection Errors**:
   - Verify internet connectivity
   - Check API key validity and rate limits

### Getting Help

If you encounter issues not covered in this guide:

1. Check the logs in the `logs` directory for detailed error information
2. Review the documentation in the `docs` directory
3. Open an issue on the GitHub repository with detailed information about the problem

## Updating

To update to the latest version:

```bash
git pull
pip install -r SuperMean/backend/requirements.txt
```

Run the tests to ensure everything is working correctly after updating:

```bash
python run.py
```