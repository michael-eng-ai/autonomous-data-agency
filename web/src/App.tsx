import { useState, useEffect } from 'react';
import { ClientChat } from './components/ClientChat';
import { ProjectFeed } from './components/ProjectFeed';
import { TeamComms } from './components/TeamComms';
import { useWebSocket } from './useWebSocket';
import { Layout } from 'lucide-react';

function App() {
  const { messages, isConnected } = useWebSocket();
  const [projectEvents, setProjectEvents] = useState<any[]>([]);
  const [teamDialogs, setTeamDialogs] = useState<any[]>([]);

  useEffect(() => {
    // Check the last message and route it
    if (messages.length > 0) {
      const lastMsg = messages[messages.length - 1];

      // Add timestamp if missing
      const eventWithTime = { ...lastMsg, timestamp: new Date().toISOString() };

      if (lastMsg.type.startsWith('project_')) {
        setProjectEvents(prev => [eventWithTime, ...prev]);
      } else if (lastMsg.type.startsWith('team_')) {
        setTeamDialogs(prev => [eventWithTime.data, ...prev]);
        // Also log to project feed for detail
        setProjectEvents(prev => [eventWithTime, ...prev]);
      }
    }
  }, [messages]);

  return (
    <div className="h-screen flex flex-col bg-gray-900 text-white overflow-hidden">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 p-4 flex justify-between items-center shrink-0">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <Layout className="text-blue-500" />
          Autonomous Data Agency
        </h1>
        <div className="flex items-center gap-2 text-sm">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </header>

      {/* Main Grid */}
      <div className="flex-1 grid grid-cols-3 divide-x divide-gray-700 overflow-hidden">
        {/* Panel 1: Client Chat (Left) */}
        <div className="h-full overflow-hidden">
          <ClientChat />
        </div>

        {/* Panel 2: Project View (Center) */}
        <div className="h-full overflow-hidden">
          <ProjectFeed events={projectEvents} />
        </div>

        {/* Panel 3: Team Comms (Right) */}
        <div className="h-full overflow-hidden">
          <TeamComms dialogs={teamDialogs} />
        </div>
      </div>
    </div>
  );
}

export default App;
