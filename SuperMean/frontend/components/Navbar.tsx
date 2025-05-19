import React from 'react';

const Navbar = () => {
  return (
    <nav className="w-full bg-white/90 dark:bg-gray-900/90 shadow-sm rounded-b-xl px-4 py-2 flex justify-between items-center sticky top-0 z-40 transition-colors duration-300">
      <div className="flex items-center space-x-4">
        <a href="/dashboard" className="text-xl font-bold text-primary dark:text-primary-light tracking-tight hover:underline">SuperMean</a>
        <a href="/analytics" className="btn-primary px-3 py-1 text-sm">Analytics</a>
        <a href="/agents" className="btn-primary px-3 py-1 text-sm">Agents</a>
        <a href="/missions" className="btn-primary px-3 py-1 text-sm">Missions</a>
        <a href="/security-dashboard" className="btn-primary px-3 py-1 text-sm">Security</a>
      </div>
      <div className="flex items-center space-x-2">
        <a href="/settings" className="btn-primary px-3 py-1 text-sm">Settings</a>
      </div>
    </nav>
  );
};

export default Navbar;
