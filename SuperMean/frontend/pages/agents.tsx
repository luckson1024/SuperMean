import React, { useEffect } from 'react';
import ProtectedRoute from '../components/ProtectedRoute';
import { useAgentStore } from '../store';
import Link from 'next/link';

const AgentsPage = () => {
  const { agents, isLoading, error, fetchAgents } = useAgentStore();

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

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
                  <Link href="/missions" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    Missions
                  </Link>
                  <Link href="/agents" className="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
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
              <h1 className="text-3xl font-bold leading-tight text-gray-900">Agents</h1>
            </div>
          </header>
          <main>
            <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
              <div className="px-4 py-8 sm:px-0">
                <div className="bg-white shadow overflow-hidden sm:rounded-md p-4">
                  <h2 className="text-xl font-semibold mb-4">All Agents</h2>
                  
                  {isLoading && <p>Loading agents...</p>}
                  {error && <p className="text-red-500">Error: {error}</p>}

                  {!isLoading && !error && agents.length === 0 && (
                    <p>No agents found.</p>
                  )}

                  {!isLoading && !error && agents.length > 0 && (
                    <ul role="list" className="divide-y divide-gray-200">
                      {agents.map((agent) => (
                        <li key={agent.id} className="px-4 py-4 sm:px-6">
                          <div className="flex items-center justify-between">
                            <div className="text-sm font-medium text-indigo-600 truncate">
                              <Link href={`/agents/${agent.id}`}>
                                {agent.name} ({agent.type})
                              </Link>
                            </div>
                            <div className="ml-2 flex-shrink-0 flex">
                              <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                agent.status === 'idle' ? 'bg-green-100 text-green-800' :
                                agent.status === 'busy' ? 'bg-blue-100 text-blue-800' :
                                agent.status === 'error' ? 'bg-red-100 text-red-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {agent.status}
                              </p>
                            </div>
                          </div>
                          <div className="mt-2 sm:flex sm:justify-between">
                            <div className="sm:flex">
                              <p className="flex items-center text-sm text-gray-500">
                                {agent.description}
                              </p>
                            </div>
                            <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                              Skills: {agent.skills.join(', ')}
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

export default AgentsPage;