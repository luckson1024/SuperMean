import React from 'react';

const MemoryViewer = () => {
  return (
    <div className="card bg-white dark:bg-gray-900 rounded-xl shadow-lg p-6 mt-6">
      <h2 className="text-2xl font-bold text-primary dark:text-primary-light mb-4">Memory Visualization</h2>
      <div className="text-gray-600 dark:text-gray-300">
        {/* TODO: Replace with a modern, interactive memory visualization (timeline, graph, etc.) */}
        <div className="flex flex-col items-center justify-center min-h-[120px]">
          <span className="text-lg">No memory data to display yet.</span>
          <span className="text-xs text-gray-400 mt-2">(This will show agent memory, task history, or vector memory in a future release.)</span>
        </div>
      </div>
    </div>
  );
};

export default MemoryViewer;