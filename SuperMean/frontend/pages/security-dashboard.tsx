import React from 'react';

const SecurityDashboard = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-red-100 via-background to-accent dark:from-gray-900 dark:via-gray-800 dark:to-red-900 transition-colors duration-500">
      <nav className="bg-white/90 dark:bg-gray-900/90 shadow-sm rounded-b-xl px-4 py-2 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-red-700 dark:text-red-300 tracking-tight">Security Dashboard</h1>
        <div className="flex space-x-4">
          <a href="/dashboard" className="btn-primary px-4 py-2">Dashboard</a>
          <a href="/agents" className="btn-primary px-4 py-2">Agents</a>
          <a href="/missions" className="btn-primary px-4 py-2">Missions</a>
        </div>
      </nav>
      <main className="max-w-5xl mx-auto py-10 px-4">
        <section className="mb-8">
          <h2 className="text-3xl font-bold mb-2 text-red-700 dark:text-red-300">Threat Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card flex flex-col items-center justify-center bg-red-50 dark:bg-gray-800">
              <span className="text-5xl mb-2">🛡️</span>
              <span className="text-lg font-semibold">Active Threats</span>
              <span className="text-2xl font-bold text-red-600 dark:text-red-400">0</span>
            </div>
            <div className="card flex flex-col items-center justify-center bg-yellow-50 dark:bg-gray-800">
              <span className="text-5xl mb-2">⚠️</span>
              <span className="text-lg font-semibold">Recent Alerts</span>
              <span className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">0</span>
            </div>
            <div className="card flex flex-col items-center justify-center bg-green-50 dark:bg-gray-800">
              <span className="text-5xl mb-2">✅</span>
              <span className="text-lg font-semibold">Resolved Issues</span>
              <span className="text-2xl font-bold text-green-600 dark:text-green-400">0</span>
            </div>
          </div>
        </section>
        <section className="mb-8">
          <h2 className="text-2xl font-bold mb-2 text-red-700 dark:text-red-300">Live Security Events</h2>
          <div className="card bg-white dark:bg-gray-900 min-h-[120px] flex items-center justify-center text-gray-500 dark:text-gray-400">
            <span>No live events. (WebSocket integration coming soon)</span>
          </div>
        </section>
        <section>
          <h2 className="text-2xl font-bold mb-2 text-red-700 dark:text-red-300">Recent Security Reports</h2>
          <div className="card bg-white dark:bg-gray-900 min-h-[120px] flex items-center justify-center text-gray-500 dark:text-gray-400">
            <span>No recent reports.</span>
          </div>
        </section>
      </main>
    </div>
  );
};

export default SecurityDashboard;
