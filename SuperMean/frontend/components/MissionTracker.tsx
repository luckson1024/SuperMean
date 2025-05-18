import React from 'react';

export interface MissionTrackerProps {
  title: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  assignedAgents: string[];
  progress: number; // 0-100
  description?: string;
}

const statusColors = {
  pending: 'bg-gray-100 text-gray-600',
  in_progress: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
};

const MissionTracker: React.FC<MissionTrackerProps> = ({ title, status, assignedAgents, progress, description }) => (
  <div className="card shadow-lg rounded-xl p-6 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 transition hover:scale-[1.01] hover:shadow-xl duration-200">
    <div className="flex items-center justify-between mb-2">
      <h3 className="text-lg font-bold text-primary dark:text-primary-light truncate">{title}</h3>
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${statusColors[status]}`}>{status.replace('_', ' ')}</span>
    </div>
    {description && <div className="mb-2 text-gray-700 dark:text-gray-300 text-sm">{description}</div>}
    <div className="mb-2">
      <span className="font-semibold text-xs text-gray-400 uppercase">Assigned Agents:</span>
      <div className="flex flex-wrap gap-2 mt-1">
        {assignedAgents.length > 0 ? assignedAgents.map(agent => (
          <span key={agent} className="bg-accent/10 dark:bg-accent/20 text-accent px-2 py-0.5 rounded text-xs font-medium">
            {agent}
          </span>
        )) : <span className="text-gray-400">None</span>}
      </div>
    </div>
    <div className="mt-2">
      <div className="w-full bg-gray-200 dark:bg-gray-800 rounded-full h-2.5">
        <div className="bg-primary dark:bg-primary-light h-2.5 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
      </div>
      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Progress: {progress}%</div>
    </div>
  </div>
);

export default MissionTracker;
