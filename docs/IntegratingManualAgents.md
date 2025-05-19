# Integrating New Manual Agents

This document outlines the steps required to integrate new manual agents into the SuperMean system.

## 1. Backend Implementation

### 1.1 Agent Class

Create a new agent class that inherits from `SuperMean/backend/agents/base_agent.py`.

### 1.2 Agent Controller

Add the new agent to the `SuperMean/backend/api/agent_controller.py` file.

## 2. Frontend Implementation

### 2.1 Agent Card

Create a new agent card component in the `SuperMean/frontend/components/` directory.

### 2.2 Agent Page

Add the new agent to the `SuperMean/frontend/pages/agents.tsx` file.

## 3. Testing

Add integration tests for the new agent.