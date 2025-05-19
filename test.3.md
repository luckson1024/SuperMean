# SuperMean Full System Manual Testing Instructions

This guide explains how to fully test the SuperMean system by interacting with the frontend locally. It covers starting the backend and frontend, tools to use, and what to check for a complete manual test.

---

## 1. Prerequisites
- Node.js (v18+ recommended)
- Python 3.10+
- Docker (optional, for containerized testing)

## 2. Install Dependencies

### Backend
```bash
cd SuperMean/backend
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Frontend
```bash
cd SuperMean/frontend
npm install
```

## 3. Start the Backend

### Option 1: Directly
```bash
cd SuperMean/backend
python server.py
```

### Option 2: Docker (if configured)
```bash
docker-compose up backend
```

## 4. Start the Frontend
```bash
cd SuperMean/frontend
npm run dev
```
- The frontend will be available at [http://localhost:3000](http://localhost:3000)

## 5. Tools to Use
- **Browser**: Chrome, Firefox, or Edge (test on desktop and mobile view)
- **DevTools**: Inspect for errors, responsiveness, and accessibility
- **Cypress**: For automated E2E tests (`npm run test:e2e` in frontend)
- **Jest**: For unit/component tests (`npm run test` in frontend)

## 6. Manual Testing Checklist
- [ ] Register a new user and login/logout
- [ ] Test dark/light mode toggle
- [ ] Navigate all pages (Dashboard, Agents, Missions, Security, Settings, Analytics)
- [ ] Create, edit, and delete missions and agents
- [ ] View agent and mission details (check real-time updates)
- [ ] Test error/404 and loading states
- [ ] Change user settings and system settings
- [ ] Interact with security dashboard and alerts
- [ ] Check accessibility (keyboard nav, contrast, ARIA)
- [ ] Test on mobile and desktop

## 7. Automated Testing (Optional)
- Run Cypress E2E tests:
  ```bash
  cd SuperMean/frontend
  npm run test:e2e
  ```
- Run Jest unit/component tests:
  ```bash
  cd SuperMean/frontend
  npm run test
  ```

## 8. Stopping the System
- Stop backend and frontend servers with `Ctrl+C` in each terminal
- If using Docker: `docker-compose down`

---

**For any issues, check browser console, backend logs, and refer to the README files.**
