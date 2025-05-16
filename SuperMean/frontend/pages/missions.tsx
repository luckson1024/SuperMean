import React, { useEffect, useState } from 'react';
import ProtectedRoute from '../components/ProtectedRoute';
import { useMissionStore } from '../store';
import Link from 'next/link';
import apiService from '../services/apiService';

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
      <div className="min-h-screen bg-gray-100">
        {/* Navigation - Can be extracted to a separate component later */}
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <h1 className="text-xl font-bold">SuperMean</h1>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  <Link href="/dashboard" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    Dashboard
                  </Link>
                  <Link href="/missions" className="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    Missions
                  </Link>
                  <Link href="/agents" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    Agents
                  </Link>
                </div>
              </div>
              {/* User/Logout - Can be extracted later */}
              {/* Assuming user info is available via useAuthStore if needed here */}
            </div>
          </div>
        </nav>

        <div className="py-10">
          <header>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <h1 className="text-3xl font-bold leading-tight text-gray-900">Missions</h1>
            </div>
          </header>
          <main>
            <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
              <div className="px-4 py-8 sm:px-0">
                <div className="bg-white shadow overflow-hidden sm:rounded-md p-4">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-semibold">All Missions</h2>
                    <button
                      className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                      onClick={() => setShowCreateForm(true)}
                    >
                      Create New Mission
                    </button>
                  </div>
                  
                  {isLoading && <p>Loading missions...</p>}
                  {error && <p className="text-red-500">Error: {error}</p>}

                  {/* Mission Creation Form/Modal */}
                  {showCreateForm && (
                    <div className="mt-4 p-4 border rounded-md bg-gray-50">
                      <h3 className="text-lg font-semibold mb-2">Create New Mission</h3>
                      {createError && <p className="text-red-500 mb-4">Error: {createError}</p>}
                      <div className="mb-4">
                        <label htmlFor="title" className="block text-sm font-medium text-gray-700">Title</label>
                        <input
                          type="text"
                          name="title"
                          id="title"
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                          value={newMissionData.title}
                          onChange={(e) => setNewMissionData({ ...newMissionData, title: e.target.value })}
                        />
                      </div>
                      <div className="mb-4">
                        <label htmlFor="description" className="block text-sm font-medium text-gray-700">Description</label>
                        <textarea
                          name="description"
                          id="description"
                          rows={3}
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                          value={newMissionData.description}
                          onChange={(e) => setNewMissionData({ ...newMissionData, description: e.target.value })}
                        ></textarea>
                      </div>
                      <div className="flex justify-end">
                        <button
                          className="mr-2 px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                          onClick={() => setShowCreateForm(false)}
                          disabled={isCreating}
                        >
                          Cancel
                        </button>
                        <button
                          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
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
                    <ul role="list" className="divide-y divide-gray-200">
                      {missions.map((mission) => (
                        <li key={mission.id} className="px-4 py-4 sm:px-6">
                          <div className="flex items-center justify-between">
                            <div className="text-sm font-medium text-indigo-600 truncate">
                              <Link href={`/missions/${mission.id}`}>
                                {mission.title}
                              </Link>
                            </div>
                            <div className="ml-2 flex-shrink-0 flex">
                              <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                mission.status === 'completed' ? 'bg-green-100 text-green-800' :
                                mission.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                                mission.status === 'failed' ? 'bg-red-100 text-red-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {mission.status}
                              </p>
                            </div>
                          </div>
                          <div className="mt-2 sm:flex sm:justify-between">
                            <div className="sm:flex">
                              <p className="flex items-center text-sm text-gray-500">
                                {mission.description}
                              </p>
                            </div>
                            <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                              Created: {new Date(mission.created_at).toLocaleDateString()}
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
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