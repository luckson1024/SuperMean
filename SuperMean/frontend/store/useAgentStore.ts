import { create } from 'zustand';
import axios from 'axios';

export interface Agent {
  id: string;
  name: string;
  type: string;
  description: string;
  status: 'idle' | 'busy' | 'error';
  skills: string[];
  created_at: string;
  updated_at: string;
}

interface AgentState {
  agents: Agent[];
  currentAgent: Agent | null;
  isLoading: boolean;
  error: string | null;
  validationErrors: Record<string, string>;
  fetchAgents: () => Promise<void>;
  fetchAgentById: (id: string) => Promise<void>;
  createAgent: (agentData: Partial<Agent>) => Promise<void>;
  updateAgent: (id: string, agentData: Partial<Agent>) => Promise<void>;
  deleteAgent: (id: string) => Promise<void>;
  clearError: () => void;
  validateAgentData: (data: Partial<Agent>) => boolean;
  updateAgentFromWebSocket: (agent: Agent) => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const useAgentStore = create<AgentState>((set, get) => ({
  agents: [],
  currentAgent: null,
  isLoading: false,
  error: null,
  validationErrors: {},

  fetchAgents: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await axios.get(`${API_URL}/agents`);
      set({ agents: response.data, isLoading: false });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to fetch agents', 
        isLoading: false 
      });
    }
  },

  fetchAgentById: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await axios.get(`${API_URL}/agents/${id}`);
      set({ currentAgent: response.data, isLoading: false });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to fetch agent', 
        isLoading: false 
      });
    }
  },

  createAgent: async (agentData: Partial<Agent>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await axios.post(`${API_URL}/agents`, agentData);
      set(state => ({ 
        agents: [...state.agents, response.data],
        isLoading: false 
      }));
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to create agent', 
        isLoading: false 
      });
    }
  },

  updateAgent: async (id: string, agentData: Partial<Agent>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await axios.put(`${API_URL}/agents/${id}`, agentData);
      set(state => ({
        agents: state.agents.map(agent => 
          agent.id === id ? { ...agent, ...response.data } : agent
        ),
        currentAgent: state.currentAgent?.id === id ? 
          { ...state.currentAgent, ...response.data } : state.currentAgent,
        isLoading: false
      }));
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to update agent', 
        isLoading: false 
      });
    }
  },

  deleteAgent: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await axios.delete(`${API_URL}/agents/${id}`);
      set(state => ({
        agents: state.agents.filter(agent => agent.id !== id),
        currentAgent: state.currentAgent?.id === id ? null : state.currentAgent,
        isLoading: false
      }));
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to delete agent', 
        isLoading: false 
      });
    }
  },

  clearError: () => set({ error: null }),

  validateAgentData: (data: Partial<Agent>) => {
    const errors: Record<string, string> = {};
    
    // Validate name
    if (!data.name) {
      errors.name = 'Name is required';
    } else if (data.name.length < 2) {
      errors.name = 'Name must be at least 2 characters';
    } else if (data.name.length > 50) {
      errors.name = 'Name must be less than 50 characters';
    }
    
    // Validate type
    if (!data.type) {
      errors.type = 'Type is required';
    }
    
    // Validate description
    if (!data.description) {
      errors.description = 'Description is required';
    } else if (data.description.length < 10) {
      errors.description = 'Description must be at least 10 characters';
    } else if (data.description.length > 500) {
      errors.description = 'Description must be less than 500 characters';
    }
    
    // Set validation errors in state
    set({ validationErrors: errors });
    
    // Return true if no errors
    return Object.keys(errors).length === 0;
  },
  
  updateAgentFromWebSocket: (agent: Agent) => {
    set(state => {
      // Check if agent already exists in state
      const agentExists = state.agents.some(a => a.id === agent.id);
      
      if (agentExists) {
        // Update existing agent
        return {
          agents: state.agents.map(a => 
            a.id === agent.id ? { ...a, ...agent } : a
          ),
          // Update current agent if it's the one being updated
          currentAgent: state.currentAgent?.id === agent.id ? 
            { ...state.currentAgent, ...agent } : state.currentAgent
        };
      } else {
        // Add new agent
        return {
          agents: [...state.agents, agent]
        };
      }
    });
  }
}));