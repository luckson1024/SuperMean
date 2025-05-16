import { create } from 'zustand';
import axios from 'axios';

export interface Mission {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  assigned_agents: string[];
}

interface MissionState {
  missions: Mission[];
  currentMission: Mission | null;
  isLoading: boolean;
  error: string | null;
  validationErrors: Record<string, string>;
  fetchMissions: () => Promise<void>;
  fetchMissionById: (id: string) => Promise<void>;
  createMission: (missionData: Partial<Mission>) => Promise<void>;
  updateMission: (id: string, missionData: Partial<Mission>) => Promise<void>;
  deleteMission: (id: string) => Promise<void>;
  assignAgentToMission: (missionId: string, agentId: string) => Promise<void>;
  removeAgentFromMission: (missionId: string, agentId: string) => Promise<void>;
  clearError: () => void;
  validateMissionData: (data: Partial<Mission>) => boolean;
  updateMissionFromWebSocket: (mission: Mission) => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const useMissionStore = create<MissionState>((set, get) => ({
  missions: [],
  currentMission: null,
  isLoading: false,
  error: null,
  validationErrors: {},

  fetchMissions: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await axios.get(`${API_URL}/missions`);
      set({ missions: response.data, isLoading: false });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to fetch missions', 
        isLoading: false 
      });
    }
  },

  fetchMissionById: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await axios.get(`${API_URL}/missions/${id}`);
      set({ currentMission: response.data, isLoading: false });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to fetch mission', 
        isLoading: false 
      });
    }
  },

  createMission: async (missionData: Partial<Mission>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await axios.post(`${API_URL}/missions`, missionData);
      set(state => ({ 
        missions: [...state.missions, response.data],
        isLoading: false 
      }));
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to create mission', 
        isLoading: false 
      });
    }
  },

  updateMission: async (id: string, missionData: Partial<Mission>) => {
    set({ isLoading: true, error: null });
    try {
      const response = await axios.put(`${API_URL}/missions/${id}`, missionData);
      set(state => ({
        missions: state.missions.map(mission => 
          mission.id === id ? { ...mission, ...response.data } : mission
        ),
        currentMission: state.currentMission?.id === id ? 
          { ...state.currentMission, ...response.data } : state.currentMission,
        isLoading: false
      }));
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to update mission', 
        isLoading: false 
      });
    }
  },

  deleteMission: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await axios.delete(`${API_URL}/missions/${id}`);
      set(state => ({
        missions: state.missions.filter(mission => mission.id !== id),
        currentMission: state.currentMission?.id === id ? null : state.currentMission,
        isLoading: false
      }));
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to delete mission', 
        isLoading: false 
      });
    }
  },

  assignAgentToMission: async (missionId: string, agentId: string) => {
    set({ isLoading: true, error: null });
    try {
      await axios.post(`${API_URL}/missions/${missionId}/agents/${agentId}`);
      // Refresh mission data after assignment
      get().fetchMissionById(missionId);
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to assign agent to mission', 
        isLoading: false 
      });
    }
  },

  removeAgentFromMission: async (missionId: string, agentId: string) => {
    set({ isLoading: true, error: null });
    try {
      await axios.delete(`${API_URL}/missions/${missionId}/agents/${agentId}`);
      // Refresh mission data after removal
      get().fetchMissionById(missionId);
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Failed to remove agent from mission', 
        isLoading: false 
      });
    }
  },

  clearError: () => set({ error: null }),

  validateMissionData: (data: Partial<Mission>) => {
    const errors: Record<string, string> = {};
    
    // Validate title
    if (!data.title) {
      errors.title = 'Title is required';
    } else if (data.title.length < 3) {
      errors.title = 'Title must be at least 3 characters';
    } else if (data.title.length > 100) {
      errors.title = 'Title must be less than 100 characters';
    }
    
    // Validate description
    if (!data.description) {
      errors.description = 'Description is required';
    } else if (data.description.length < 10) {
      errors.description = 'Description must be at least 10 characters';
    } else if (data.description.length > 1000) {
      errors.description = 'Description must be less than 1000 characters';
    }
    
    // Set validation errors in state
    set({ validationErrors: errors });
    
    // Return true if no errors
    return Object.keys(errors).length === 0;
  },
  
  updateMissionFromWebSocket: (mission: Mission) => {
    set(state => {
      // Check if mission already exists in state
      const missionExists = state.missions.some(m => m.id === mission.id);
      
      if (missionExists) {
        // Update existing mission
        return {
          missions: state.missions.map(m => 
            m.id === mission.id ? { ...m, ...mission } : m
          ),
          // Update current mission if it's the one being updated
          currentMission: state.currentMission?.id === mission.id ? 
            { ...state.currentMission, ...mission } : state.currentMission
        };
      } else {
        // Add new mission
        return {
          missions: [...state.missions, mission]
        };
      }
    });
  }
}));