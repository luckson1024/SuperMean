import React, { useEffect, useState } from 'react';
import ProtectedRoute from '../components/ProtectedRoute';
import { useMissionStore } from '../store';
import Link from 'next/link';
import apiService from '../services/apiService';
import MissionTracker from '../components/MissionTracker';

const MissionsPage = () => {
  const { missions, isLoading, error, fetchMissions, createMission } = useMissionStore();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newMissionData, setNewMissionData] = useState({ title: '', description: '' });
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const handleCreateMission = async () => {
    if (!newMissionData.title || !newMissionData.description) {
      setCreateError('Title and description are required.');
      return;
    }
    setIsCreating(true);
    setCreateError(null);
    try {
      await createMission(newMissionData);
      setShowCreateForm(false);
      setNewMissionData({ title: '', description: '' });
    } catch (err: any) {
      setCreateError(err.message || 'Failed to create mission.');
    } finally {
      setIsCreating(false);
    }
  };

  useEffect(() => {
    fetchMissions();
  }, [fetchMissions]);

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
              <h1 className="text-3xl font-bold leading-tight text-primary dark:text-primary-light drop-shadow-lg">Missions</h1>
            </div>
          </header>
          <main>
            <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
              <div className="px-4 py-8 sm:px-0">
                <div className="card">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-semibold text-primary dark:text-primary-light">All Missions</h2>
                    <button
                      className="btn-primary px-4 py-2"
                      onClick={() => setShowCreateForm(true)}
                    >
                      Create New Mission
                    </button>
                  </div>
                  {isLoading && <p>Loading missions...</p>}
                  {error && <p className="text-red-500">Error: {error}</p>}
                  {showCreateForm && (
                    <div className="mt-4 p-4 border rounded-xl bg-background dark:bg-gray-800 shadow-soft">
                      <h3 className="text-lg font-semibold mb-2 text-primary dark:text-primary-light">Create New Mission</h3>
                      {createError && <p className="text-red-500 mb-4">Error: {createError}</p>}
                      <div className="mb-4">
                        <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-200">Title</label>
                        <input
                          type="text"
                          name="title"
                          id="title"
                          className="input input-bordered w-full"
                          value={newMissionData.title}
                          onChange={(e) => setNewMissionData({ ...newMissionData, title: e.target.value })}
                        />
                      </div>
                      <div className="mb-4">
                        <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-200">Description</label>
                        <textarea
                          name="description"
                          id="description"
                          rows={3}
                          className="input input-bordered w-full"
                          value={newMissionData.description}
                          onChange={(e) => setNewMissionData({ ...newMissionData, description: e.target.value })}
                        ></textarea>
                      </div>
                      <div className="flex justify-end">
                        <button
                          className="btn-primary px-4 py-2 mr-2 bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
                          onClick={() => setShowCreateForm(false)}
                          disabled={isCreating}
                        >
                          Cancel
                        </button>
                        <button
                          className="btn-primary px-4 py-2"
                          onClick={handleCreateMission}
                          disabled={isCreating}
                        >
                          {isCreating ? 'Creating...' : 'Create Mission'}
                        </button>
                      </div>
                    </div>
                  )}
                  {!isLoading && !error && missions.length === 0 && !showCreateForm && (
                    <p>No missions found.</p>
                  )}
                  {!isLoading && !error && missions.length > 0 && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {missions.map((mission) => (
                        <MissionTracker
                          key={mission.id}
                          title={mission.title}
                          status={mission.status}
                          assignedAgents={mission.assigned_agents}
                          progress={mission.status === 'completed' ? 100 : mission.status === 'in_progress' ? 60 : mission.status === 'pending' ? 10 : 0}
                          description={mission.description}
                        />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default MissionsPage;