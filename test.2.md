# How to Run and Interact with SuperMean (Backend + Frontend)

## 1. Prerequisites
- Python 3.12+
- Node.js (for frontend)
- Docker (optional, for containerized run)
- Install dependencies for both backend and frontend


2. In GitHub Codespaces (Online)
Start the Backend (API Server)
Open a terminal in Codespaces.
Run:

cd SuperMean/backend
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# The backend API will be available at: https://<your-codespace-id>-8000.app.github.dev/docs

Start the Frontend (Next.js React App)
1. Open a new terminal in Codespaces.
2. Run:
cd SuperMean/frontend
npm install
npm run dev

# The frontend will be available at: https://<your-codespace-id>-3000.app.github.dev

####### Interact
Open the URLs above in your browser to use the web UI and API docs.

3. In Local VS Code (Offline)
Start the Backend (API Server)
1. Open a terminal in your local VS Code.
2. Run:

cd SuperMean/backend
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# The backend API will be available at: http://localhost:8000/docs


Start the Frontend (Next.js React App)
1. Open a new terminal.
2. Run:

cd SuperMean/frontend
npm install
npm run dev

# The frontend will be available at: http://localhost:3000

5. Key Notes
Make sure both backend and frontend are running for full functionality.
If using Docker Compose, you can also run: docker-compose up from the project root.
In Codespaces, use the "Ports" tab to open forwarded ports in your browser.



## 2. Start the Backend (API Server)

### Option A: Using Python directly
```bash
cd SuperMean/backend
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
- The backend API will be available at: http://localhost:8000/docs (Swagger UI)

### Option B: Using Docker
```bash
docker build -f Dockerfile.backend -t supermean-backend .
docker run -p 8000:8000 supermean-backend
```

## 3. Start the Frontend (Next.js React App)
```bash
cd SuperMean/frontend
npm install
npm run dev
```
- The frontend will be available at: http://localhost:3000

## 4. Interact with SuperMean
- Open your browser and go to http://localhost:3000 to use the web UI.
- For API testing, visit http://localhost:8000/docs for interactive API docs.

## 5. Stopping the Project
- Use `Ctrl+C` in each terminal to stop the backend and frontend servers.

## 6. Notes
- Make sure both backend and frontend are running for full functionality.
- If using Docker Compose, you can also run: `docker-compose up` from the project root.


# Luckson Chanda.