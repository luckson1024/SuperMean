import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useMissionStore } from '../store';
import { MessageType } from '../services/websocketService';
import { motion } from 'framer-motion';
import websocketService from '../services/websocketService';

const MissionDetails = () => {
  const router = useRouter();
  const { id } = router.query;
  const { missions, fetchMissions } = useMissionStore();

  interface Agent {
    id: string;
    name: string;
  }

  interface Mission {
    id: string;
    title: string;
    description: string;
    agents?: Agent[];
    progress?: number;
  }

  const [mission, setMission] = useState<Mission | null>(null);
  const [progress, setProgress] = useState(0);
  const [liveStatus, setLiveStatus] = useState<'pending' | 'in_progress' | 'completed'>('pending');

  useEffect(() => {
    fetchMissions();
  }, [fetchMissions]);

  useEffect(() => {
    if (id && missions.length > 0) {
      const found = missions.find((m: any) => m.id === id) as Mission;
      setMission(found || null);
      setProgress(found?.progress !== undefined ? found.progress : 0);
    }
  }, [id, missions]);

  useEffect(() => {
    if (!id) return;

    const handleMissionUpdate = (data: any) => {
      if (data.missionId === id) {
        setProgress(data.progress);
        setLiveStatus(data.status);
      }
    };

    websocketService.onMessage(MessageType.MISSION_UPDATE, handleMissionUpdate);

    return () => {
      websocketService.offMessage(MessageType.MISSION_UPDATE, handleMissionUpdate);
    };
  }, [id]);

  if (!mission) {
    return <div className="flex justify-center items-center min-h-screen text-lg">Loading mission...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-light via-background to-accent dark:from-gray-900 dark:via-gray-800 dark:to-primary-dark transition-colors duration-500">
      <div className="max-w-3xl mx-auto py-10 px-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <h1 className="text-4xl font-bold text-primary dark:text-primary-light mb-4">Mission: {mission?.title}</h1>
          <div className="mb-4 flex items-center space-x-4">
            <span className={`inline-block w-3 h-3 rounded-full ${liveStatus === 'completed' ? 'bg-green-500' : liveStatus === 'in_progress' ? 'bg-yellow-500' : 'bg-gray-400'} mr-2`} />
            <span className="text-lg font-semibold">Status: {liveStatus}</span>
            <span className="ml-4 text-lg">Progress: {progress || 0}%</span>
          </div>
          <div className="card mb-6">
            <h2 className="text-xl font-semibold mb-2">Description</h2>
            <p className="text-gray-700 dark:text-gray-200">{mission?.description}</p>
          </div>
          <div className="card mb-6">
            <h2 className="text-xl font-semibold mb-2">Assigned Agents</h2>
            <ul className="list-disc pl-6">
              {mission?.agents?.map((agent) => (
                <li key={agent.id} className="mb-1">{agent.name}</li>
              )) || null}
            </ul>
          </div>
          <div className="card">
            <h2 className="text-xl font-semibold mb-2">Action History</h2>
            <div className="bg-gray-50 dark:bg-gray-900 rounded p-4 min-h-[80px] text-gray-600 dark:text-gray-300">
              {/* Placeholder for action history, can be replaced with real-time log feed */}
              No recent actions.
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default MissionDetails;
