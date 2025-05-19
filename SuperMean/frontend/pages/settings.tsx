import React from 'react';

const SystemSettings = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-200 via-background to-accent dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-500">
      <div className="max-w-3xl mx-auto py-10 px-4">
        <h1 className="text-4xl font-bold text-primary dark:text-primary-light mb-6">System Settings</h1>
        <div className="card mb-6">
          <h2 className="text-xl font-semibold mb-2">Agent Configuration</h2>
          <div className="bg-gray-100 dark:bg-gray-800 rounded p-4 mb-2">Agent configuration management coming soon.</div>
        </div>
        <div className="card mb-6">
          <h2 className="text-xl font-semibold mb-2">System Preferences</h2>
          <div className="bg-gray-100 dark:bg-gray-800 rounded p-4 mb-2">System preferences management coming soon.</div>
        </div>
        <div className="card mb-6">
          <h2 className="text-xl font-semibold mb-2">Integrations</h2>
          <div className="bg-gray-100 dark:bg-gray-800 rounded p-4 mb-2">Integration settings coming soon.</div>
        </div>
        <div className="card">
          <h2 className="text-xl font-semibold mb-2">Backup & Restore</h2>
          <div className="bg-gray-100 dark:bg-gray-800 rounded p-4 mb-2">Backup and restore options coming soon.</div>
        </div>
      </div>
    </div>
  );
};

export default SystemSettings;
