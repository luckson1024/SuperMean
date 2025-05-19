export interface Agent {
  id: string;
  name: string;
  type: string;
  description: string;
  status: 'idle' | 'busy' | 'error';
  skills: string[];
  created_at: string;
  updated_at: string;
  missions?: any[];
}