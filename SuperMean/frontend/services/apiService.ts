import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor
api.interceptors.request.use(
  (config) => {
    // Add authorization token if available
    const token = localStorage.getItem('token'); // Assuming token is stored in localStorage
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Handle successful responses
    return response;
  },
  (error: AxiosError) => {
    // Handle errors
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API Error Response:', error.response.data);
      console.error('API Error Status:', error.response.status);
      console.error('API Error Headers:', error.response.headers);
      // You might want to throw a custom error here or return a specific error structure
      return Promise.reject(error.response.data);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('API Error Request:', error.request);
      return Promise.reject({ message: 'No response received from server' });
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('API Error Message:', error.message);
      return Promise.reject({ message: error.message });
    }
  }
);

// Define API service functions
const apiService = {
  // Authentication
  login: (credentials: any): Promise<AxiosResponse<any>> => {
    return api.post('/auth/login', credentials);
  },
  register: (userData: any): Promise<AxiosResponse<any>> => {
    return api.post('/auth/register', userData);
  },
  
  // User Settings
  getUserSettings: (): Promise<AxiosResponse<any>> => {
    return api.get('/users/settings');
  },
  updateUserSettings: (settings: any): Promise<AxiosResponse<any>> => {
    return api.put('/users/settings', settings);
  },

  // Missions
  getMissions: (): Promise<AxiosResponse<any>> => {
    return api.get('/missions');
  },
  getMissionById: (missionId: string): Promise<AxiosResponse<any>> => {
    return api.get(`/missions/${missionId}`);
  },
  createMission: (missionData: any): Promise<AxiosResponse<any>> => {
    return api.post('/missions', missionData);
  },
  updateMission: (missionId: string, missionData: any): Promise<AxiosResponse<any>> => {
    return api.put(`/missions/${missionId}`, missionData);
  },
  deleteMission: (missionId: string): Promise<AxiosResponse<any>> => {
    return api.delete(`/missions/${missionId}`);
  },

  // Agents
  getAgents: (): Promise<AxiosResponse<any>> => {
    return api.get('/agents');
  },
  getAgentById: (agentId: string): Promise<AxiosResponse<any>> => {
    return api.get(`/agents/${agentId}`);
  },
  createAgent: (agentData: any): Promise<AxiosResponse<any>> => {
    return api.post('/agents', agentData);
  },
  updateAgent: (agentId: string, agentData: any): Promise<AxiosResponse<any>> => {
    return api.put(`/agents/${agentId}`, agentData);
  },
  deleteAgent: (agentId: string): Promise<AxiosResponse<any>> => {
    return api.delete(`/agents/${agentId}`);
  },

  // Super Agents
  getSuperAgents: (): Promise<AxiosResponse<any>> => {
    return api.get('/super_agents');
  },
  getSuperAgentById: (superAgentId: string): Promise<AxiosResponse<any>> => {
    return api.get(`/super_agents/${superAgentId}`);
  },
  createSuperAgent: (superAgentData: any): Promise<AxiosResponse<any>> => {
    return api.post('/super_agents', superAgentData);
  },
  updateSuperAgent: (superAgentId: string, superAgentData: any): Promise<AxiosResponse<any>> => {
    return api.put(`/super_agents/${superAgentId}`, superAgentData);
  },
  deleteSuperAgent: (superAgentId: string): Promise<AxiosResponse<any>> => {
    return api.delete(`/super_agents/${superAgentId}`);
  },

  // Add other API calls as needed
};

export default apiService;