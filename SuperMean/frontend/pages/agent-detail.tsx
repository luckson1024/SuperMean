import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useAgentStore } from '../store';
import { motion } from 'framer-motion';
import apiService from '../services/apiService';
import websocketService, { MessageType } from '../services/websocketService';
import { Agent } from '../types'; // Assuming you have an Agent type defined

const AgentDetail = () => {
  const router = useRouter();
  const { id } = router.query;
  const { agents, fetchAgents } = useAgentStore();
  const [agent, setAgent] = useState<Agent | null>(null);
  const [liveStatus, setLiveStatus] = useState('offline');

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  useEffect(() => {
    if (id && agents.length > 0) {
      const found = agents.find((a: any) => a.id === id);
      setAgent(found || null);
    }
  }, [id, agents]);

  useEffect(() => {
    if (!id) return;

    // Handler for agent status updates
    const agentStatusHandler = (data: any) => {
      if (data.agentId === id && data.status) {
        setLiveStatus(data.status);
      }
    };
    // Subscribe to WebSocket updates using MessageType enum
    websocketService.onMessage(MessageType.AGENT_UPDATE, agentStatusHandler);
    // Cleanup on unmount
    return () => {
      websocketService.offMessage(MessageType.AGENT_UPDATE, agentStatusHandler);
    };
  }, [id]);

  if (!agent) {
    return <div className="flex justify-center items-center min-h-screen text-lg">Loading agent...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-light via-background to-accent dark:from-gray-900 dark:via-gray-800 dark:to-primary-dark transition-colors duration-500">
      <div className="max-w-3xl mx-auto py-10 px-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <h1 className="text-4xl font-bold text-primary dark:text-primary-light mb-4">Agent: {agent.name}</h1>
          <div className="mb-4 flex items-center space-x-4">
            <span className={`inline-block w-3 h-3 rounded-full ${liveStatus === 'online' ? 'bg-green-500' : 'bg-gray-400'} mr-2`} />
            <span className="text-lg font-semibold">Status: {liveStatus}</span>
:start_line:57
-------
          </div>
          <div className="card mb-6">
            <h2 className="text-xl font-semibold mb-2">Activity Log</h2>
            <div className="bg-gray-50 dark:bg-gray-900 rounded p-4 min-h-[80px] text-gray-600 dark:text-gray-300">
              {/* Placeholder for activity log, can be replaced with real-time log feed */}
              No recent activity.
            </div>
          </div>
          <div className="card">
            <h2 className="text-xl font-semibold mb-2">Associated Missions</h2>
            <ul className="list-disc pl-6">
              {(agent.missions || []).map((mission: any) => (
                <li key={mission.id} className="mb-1">{mission.title}</li>
              ))}
            </ul>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default AgentDetail;
