import React from 'react';

export interface AgentCardProps {
  name: string;
  type: string;
  status: 'idle' | 'busy' | 'error';
  skills: string[];
  description?: string;
}

const statusColors = {
  idle: 'bg-green-100 text-green-800',
  busy: 'bg-blue-100 text-blue-800',
  error: 'bg-red-100 text-red-800',
};

const AgentCard: React.FC<AgentCardProps> = ({ name, type, status, skills, description }) => (
  <div className="card shadow-lg rounded-xl p-6 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 transition hover:scale-[1.02] hover:shadow-xl duration-200">
    <div className="flex items-center justify-between mb-2">
      <h3 className="text-xl font-bold text-primary dark:text-primary-light truncate">{name}</h3>
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${statusColors[status]}`}>{status}</span>
    </div>
    <div className="text-sm text-gray-500 dark:text-gray-400 mb-2">{type}</div>
    {description && <div className="mb-2 text-gray-700 dark:text-gray-300 text-sm">{description}</div>}
    <div className="mt-2">
      <span className="font-semibold text-xs text-gray-400 uppercase">Skills:</span>
      <div className="flex flex-wrap gap-2 mt-1">
        {skills.length > 0 ? skills.map(skill => (
          <span key={skill} className="bg-primary/10 dark:bg-primary-dark/20 text-primary dark:text-primary-light px-2 py-0.5 rounded text-xs font-medium">
            {skill}
          </span>
        )) : <span className="text-gray-400">None</span>}
      </div>
    </div>
  </div>
);

export default AgentCard;
