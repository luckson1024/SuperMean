import React from 'react';

const SecurityConfig = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-100 via-background to-accent dark:from-gray-900 dark:via-gray-800 dark:to-green-900 transition-colors duration-500">
      <nav className="bg-white/90 dark:bg-gray-900/90 shadow-sm rounded-b-xl px-4 py-2 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-green-700 dark:text-green-300 tracking-tight">Security Configuration</h1>
        <div className="flex space-x-4">
          <a href="/dashboard" className="btn-primary px-4 py-2">Dashboard</a>
          <a href="/agents" className="btn-primary px-4 py-2">Agents</a>
          <a href="/missions" className="btn-primary px-4 py-2">Missions</a>
          <a href="/security-dashboard" className="btn-primary px-4 py-2">Security</a>
        </div>
      </nav>
      <main className="max-w-5xl mx-auto py-10 px-4">
        <section className="mb-8">
          <h2 className="text-3xl font-bold mb-2 text-green-700 dark:text-green-300">Manage Security Rules</h2>
          <div className="card bg-white dark:bg-gray-900 min-h-[180px] flex flex-col items-center justify-center text-gray-500 dark:text-gray-400">
            <span className="text-6xl mb-2">🛠️</span>
            <span>Security rule management coming soon.</span>
          </div>
        </section>
        <section>
          <h2 className="text-2xl font-bold mb-2 text-green-700 dark:text-green-300">Thresholds & Settings</h2>
          <div className="card bg-white dark:bg-gray-900 min-h-[120px] flex items-center justify-center text-gray-500 dark:text-gray-400">
            <span>Threshold configuration coming soon.</span>
          </div>
        </section>
      </main>
    </div>
  );
};

export default SecurityConfig;
