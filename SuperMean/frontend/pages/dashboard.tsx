import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import ProtectedRoute from '../components/ProtectedRoute';
import UserSettingsPanel from '../components/UserSettingsPanel'; // Import the settings panel
import TaskBoard, { Task } from '../components/TaskBoard';
import { useAuthStore, useMissionStore, useAgentStore } from '../store';
import { CogIcon } from '@heroicons/react/24/outline'; // Import CogIcon
import MemoryViewer from '../components/MemoryViewer';

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
      <div className="min-h-screen bg-gradient-to-br from-primary-light via-background to-accent dark:from-gray-900 dark:via-gray-800 dark:to-primary-dark transition-colors duration-500">
        <nav className="bg-white/90 dark:bg-gray-900/90 shadow-sm rounded-b-xl px-4 py-2 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-primary dark:text-primary-light tracking-tight">SuperMean</h1>
          <div className="flex space-x-4">
            <Link href="/dashboard" className="btn-primary px-4 py-2">Dashboard</Link>
            <Link href="/missions" className="btn-primary px-4 py-2">Missions</Link>
            <Link href="/agents" className="btn-primary px-4 py-2">Agents</Link>
          </div>
        </nav>
        <div className="py-10">
          <header>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <h1 className="text-3xl font-bold leading-tight text-primary dark:text-primary-light drop-shadow-lg">Dashboard</h1>
            </div>
          </header>
          <main>
            <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
              <div className="px-4 py-8 sm:px-0">
                <div className="card">
                  <h2 className="text-xl font-semibold mb-4 text-primary dark:text-primary-light">Welcome, {user?.username || 'User'}!</h2>
                  <p className="text-gray-600 dark:text-gray-300 mb-6">This is your SuperMean dashboard. From here you can manage your missions and agents.</p>
                  <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                    <div className="card bg-primary/10 dark:bg-primary-dark/20">
                      <div className="px-4 py-5 sm:p-6">
                        <h3 className="text-lg font-medium text-primary dark:text-primary-light">Active Missions</h3>
                        <div className="mt-1 text-3xl font-semibold text-primary dark:text-primary-light">{missions.length}</div>
                        <div className="mt-4">
                          <Link href="/missions" className="btn-primary px-3 py-1">View all missions</Link>
                        </div>
                      </div>
                    </div>
                    <div className="card bg-accent/10 dark:bg-accent/20">
                      <div className="px-4 py-5 sm:p-6">
                        <h3 className="text-lg font-medium text-accent">Available Agents</h3>
                        <div className="mt-1 text-3xl font-semibold text-accent">{agents.length}</div>
                        <div className="mt-4">
                          <Link href="/agents" className="btn-primary px-3 py-1">View all agents</Link>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="mt-10">
                    <h2 className="text-xl font-semibold mb-4 text-primary dark:text-primary-light">Mission Task Board (Demo)</h2>
                    <TaskBoard
                      tasks={missions.flatMap((mission) => [
                        { id: mission.id + '-plan', title: `Plan: ${mission.title}`, status: mission.status === 'completed' ? 'done' : mission.status === 'in_progress' ? 'in_progress' : 'todo' },
                        { id: mission.id + '-exec', title: `Execute: ${mission.title}`, status: mission.status === 'completed' ? 'done' : mission.status === 'in_progress' ? 'in_progress' : 'todo' },
                      ])}
                    />
                  </div>
                  <div className="mt-10">
                    <h2 className="text-xl font-semibold mb-4 text-primary dark:text-primary-light">Memory Visualization</h2>
                    <MemoryViewer />
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
        <UserSettingsPanel isOpen={isSettingsPanelOpen} onClose={closeSettingsPanel} />
      </div>
    </ProtectedRoute>
  );
};

export default Dashboard;