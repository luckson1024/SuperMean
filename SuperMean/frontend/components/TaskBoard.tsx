import React from 'react';

export interface Task {
  id: string;
  title: string;
  status: 'todo' | 'in_progress' | 'done';
  assignee?: string;
}

export interface TaskBoardProps {
  tasks: Task[];
}

const statusMap = [
  { key: 'todo', label: 'To Do', color: 'bg-gray-100 dark:bg-gray-800' },
  { key: 'in_progress', label: 'In Progress', color: 'bg-blue-100 dark:bg-blue-900' },
  { key: 'done', label: 'Done', color: 'bg-green-100 dark:bg-green-900' },
];

const TaskBoard: React.FC<TaskBoardProps> = ({ tasks }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {statusMap.map(({ key, label, color }) => (
        <div key={key} className="rounded-xl shadow-lg p-4 border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
          <h4 className="font-bold text-primary dark:text-primary-light mb-3 text-lg">{label}</h4>
          <div className="space-y-3 min-h-[60px]">
            {tasks.filter(t => t.status === key).length === 0 && (
              <div className="text-gray-400 text-sm">No tasks</div>
            )}
            {tasks.filter(t => t.status === key).map(task => (
              <div key={task.id} className={`rounded-lg p-3 ${color} shadow-sm flex flex-col transition hover:scale-[1.01]`}>
                <span className="font-medium text-sm text-primary dark:text-primary-light">{task.title}</span>
                {task.assignee && <span className="text-xs text-gray-500 mt-1">Assigned: {task.assignee}</span>}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default TaskBoard;
