import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import ProtectedRoute from '../components/ProtectedRoute';
import UserSettingsPanel from '../components/UserSettingsPanel'; // Import the settings panel
import { useAuthStore, useMissionStore, useAgentStore } from '../store';
import { CogIcon } from '@heroicons/react/24/outline'; // Import CogIcon

const Dashboard = () => {
  const { user, logout } = useAuthStore();
  const { missions, fetchMissions } = useMissionStore();
  const { agents, fetchAgents } = useAgentStore();
  const router = useRouter();

  const [isSettingsPanelOpen, setIsSettingsPanelOpen] = useState(false); // State to manage panel visibility

  useEffect(() => {
    fetchMissions();
    fetchAgents();
  }, [fetchMissions, fetchAgents]);

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const openSettingsPanel = () => {
    setIsSettingsPanelOpen(true);
  };

  const closeSettingsPanel = () => {
    setIsSettingsPanelOpen(false);
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900"> {/* Added dark mode class */}
        <nav className="bg-white dark:bg-gray-800 shadow-sm"> {/* Added dark mode classes */}
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">SuperMean</h1> {/* Added dark mode class */}
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  <Link href="/dashboard" className="border-indigo-500 text-gray-900 dark:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"> {/* Added dark mode class */}
                    Dashboard
                  </Link>
                  <Link href="/missions" className="border-transparent text-gray-500 dark:text-gray-300 hover:border-gray-300 hover:text-gray-700 dark:hover:text-gray-500 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"> {/* Added dark mode classes */}
                    Missions
                  </Link>
                  <Link href="/agents" className="border-transparent text-gray-500 dark:text-gray-300 hover:border-gray-300 hover:text-gray-700 dark:hover:text-gray-500 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"> {/* Added dark mode classes */}
                    Agents
                  </Link>
                </div>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:items-center">
                <div className="ml-3 relative">
                  <div className="flex items-center space-x-4">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300"> {/* Added dark mode class */}
                      {user?.username || 'User'}
                    </span>
                    {/* Settings Button */}
                    <button
                      onClick={openSettingsPanel}
                      className="text-gray-500 dark:text-gray-300 hover:text-gray-700 dark:hover:text-gray-500"
                      aria-label="User Settings"
                      data-testid="open-settings-button" // Add data-testid for Cypress
                    >
                      <CogIcon className="h-6 w-6" />
                    </button>
                    <button
                      onClick={handleLogout}
                      className="text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300" // Added dark mode classes
                    >
                      Sign out
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </nav>

        <div className="py-10">
          <header>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <h1 className="text-3xl font-bold leading-tight text-gray-900 dark:text-white">Dashboard</h1> {/* Added dark mode class */}
            </div>
          </header>
          <main>
            <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
              <div className="px-4 py-8 sm:px-0">
                <div className="border-4 border-dashed border-gray-200 dark:border-gray-700 rounded-lg h-96 p-4"> {/* Added dark mode class */}
                  <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Welcome, {user?.username || 'User'}!</h2> {/* Added dark mode class */}
                  <p className="text-gray-600 dark:text-gray-400"> {/* Added dark mode class */}
                    This is your SuperMean dashboard. From here you can manage your missions and agents.
                  </p>
                  <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                    <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg"> {/* Added dark mode class */}
                      <div className="px-4 py-5 sm:p-6">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white">Active Missions</h3> {/* Added dark mode class */}
                        <div className="mt-1 text-3xl font-semibold text-gray-900 dark:text-white">{missions.length}</div> {/* Added dark mode class */}
                        <div className="mt-4">
                          <Link href="/missions" className="text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300"> {/* Added dark mode classes */}
                            View all missions
                          </Link>
                        </div>
                      </div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg"> {/* Added dark mode class */}
                      <div className="px-4 py-5 sm:p-6">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white">Available Agents</h3> {/* Added dark mode class */}
                        <div className="mt-1 text-3xl font-semibold text-gray-900 dark:text-white">{agents.length}</div> {/* Added dark mode class */}
                        <div className="mt-4">
                          <Link href="/agents" className="text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300"> {/* Added dark mode classes */}
                            View all agents
                          </Link>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>

        {/* Render the UserSettingsPanel */}
        <UserSettingsPanel
          isOpen={isSettingsPanelOpen}
          onClose={closeSettingsPanel}
        />
      </div>
    </ProtectedRoute>
  );
};

export default Dashboard;