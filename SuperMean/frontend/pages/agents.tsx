import React, { useEffect } from 'react';
import ProtectedRoute from '../components/ProtectedRoute';
import { useAgentStore } from '../store';
import Link from 'next/link';
import AgentCard from '../components/AgentCard';

const AgentsPage = () => {
  const { agents, isLoading, error, fetchAgents } = useAgentStore();

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

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
              <h1 className="text-3xl font-bold leading-tight text-primary dark:text-primary-light drop-shadow-lg">Agents</h1>
            </div>
          </header>
          <main>
            <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
              <div className="px-4 py-8 sm:px-0">
                <div className="card">
                  <h2 className="text-xl font-semibold mb-4 text-primary dark:text-primary-light">All Agents</h2>
                  
                  {isLoading && <p>Loading agents...</p>}
                  {error && <p className="text-red-500">Error: {error}</p>}

                  {!isLoading && !error && agents.length === 0 && (
                    <p>No agents found.</p>
                  )}

                  {!isLoading && !error && agents.length > 0 && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {agents.map((agent) => (
                        <AgentCard
                          key={agent.id}
                          name={agent.name}
                          type={agent.type}
                          status={agent.status}
                          skills={agent.skills}
                          description={agent.description}
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

export default AgentsPage;