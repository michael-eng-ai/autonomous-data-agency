import { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import type {
  ProjectPhase,
  ActivityMessage,
  WebSocketEventData,
  TeamTimelineEntry
} from './types';

const SOCKET_URL = 'ws://localhost:8000/ws';
const RECONNECT_DELAY = 3000; // 3 seconds
const MAX_RECONNECT_ATTEMPTS = 10;

interface WebSocketMessage {
  type: string;
  data: WebSocketEventData;
}

interface UseWebSocketReturn {
  messages: WebSocketMessage[];
  isConnected: boolean;
  sendMessage: (msg: unknown) => void;
  // Derived state
  currentPhase: ProjectPhase;
  activeTeam: string | null;
  activeTeamAction: string | null;
  projectProgress: number;
  projectStartTime: Date | null;
  teamTimeline: TeamTimelineEntry[];
  activities: ActivityMessage[];
  // Methods
  clearMessages: () => void;
  reconnect: () => void;
}

export const useWebSocket = (): UseWebSocketReturn => {
  const socket = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  // Derived state
  const [currentPhase, setCurrentPhase] = useState<ProjectPhase>('idle');
  const [activeTeam, setActiveTeam] = useState<string | null>(null);
  const [activeTeamAction, setActiveTeamAction] = useState<string | null>(null);
  const [projectStartTime, setProjectStartTime] = useState<Date | null>(null);
  const [teamTimeline, setTeamTimeline] = useState<TeamTimelineEntry[]>([]);
  const [activities, setActivities] = useState<ActivityMessage[]>([]);
  const [teamsStarted, setTeamsStarted] = useState<Set<string>>(new Set());
  const [teamsCompleted, setTeamsCompleted] = useState<Set<string>>(new Set());

  // Calculate progress
  const projectProgress = useMemo(() => {
    if (teamsStarted.size === 0) return 0;
    return Math.round((teamsCompleted.size / teamsStarted.size) * 100);
  }, [teamsStarted, teamsCompleted]);

  // Process incoming messages
  const processMessage = useCallback((message: WebSocketMessage) => {
    const { type, data } = message;
    const timestamp = new Date();

    // Project lifecycle events
    if (type === 'project_started' || type === 'project_phase_started') {
      setCurrentPhase('requirements');
      setProjectStartTime(timestamp);
      setTeamsStarted(new Set());
      setTeamsCompleted(new Set());
      setTeamTimeline([]);
      setActivities([]);

      // Add activity
      setActivities(prev => [{
        id: `${Date.now()}-start`,
        team: 'system',
        type: 'info',
        message: 'Projeto iniciado',
        timestamp
      }, ...prev]);
    }

    if (type === 'project_completed' || type === 'project_phase_completed') {
      setCurrentPhase('completed');
      setActiveTeam(null);
      setActiveTeamAction(null);

      setActivities(prev => [{
        id: `${Date.now()}-complete`,
        team: 'system',
        type: 'result',
        message: 'Projeto concluído com sucesso!',
        timestamp
      }, ...prev]);
    }

    // Team execution events
    if (type === 'team_execution_started') {
      const teamId = data.team as string;
      setActiveTeam(teamId);
      setActiveTeamAction('Iniciando análise...');

      // Update teams tracking
      setTeamsStarted(prev => new Set([...prev, teamId]));

      // Update timeline
      setTeamTimeline(prev => {
        const existing = prev.find(t => t.teamId === teamId);
        if (existing) {
          return prev.map(t =>
            t.teamId === teamId
              ? { ...t, status: 'active' as const, startTime: timestamp }
              : t
          );
        }
        return [...prev, {
          teamId,
          teamName: formatTeamName(teamId),
          status: 'active' as const,
          startTime: timestamp,
          color: getTeamColor(teamId)
        }];
      });

      // Add activity
      setActivities(prev => [{
        id: `${Date.now()}-${teamId}-start`,
        team: teamId,
        type: 'action',
        message: `${formatTeamName(teamId)} iniciou o trabalho`,
        timestamp
      }, ...prev]);
    }

    if (type === 'team_execution_completed') {
      const teamId = data.team as string;

      // Update teams tracking
      setTeamsCompleted(prev => new Set([...prev, teamId]));

      // Update timeline
      setTeamTimeline(prev =>
        prev.map(t =>
          t.teamId === teamId
            ? { ...t, status: 'completed' as const, endTime: timestamp }
            : t
        )
      );

      // Clear active team if it was this one
      if (activeTeam === teamId) {
        setActiveTeam(null);
        setActiveTeamAction(null);
      }

      // Add activity
      setActivities(prev => [{
        id: `${Date.now()}-${teamId}-complete`,
        team: teamId,
        type: 'result',
        message: `${formatTeamName(teamId)} finalizou o trabalho`,
        timestamp
      }, ...prev]);
    }

    // Team dialog/thinking events
    if (type === 'team_dialog') {
      const teamId = data.team as string || data.agent as string || 'unknown';
      const message = data.message as string || data.summary as string || '';

      if (teamId === activeTeam) {
        setActiveTeamAction(message.slice(0, 50) + (message.length > 50 ? '...' : ''));
      }

      setActivities(prev => [{
        id: `${Date.now()}-${teamId}-dialog`,
        team: teamId,
        type: 'thinking',
        message: message.slice(0, 200),
        timestamp
      }, ...prev]);
    }

    // Error events
    if (type === 'project_error' || type.includes('error')) {
      const teamId = data.team as string || 'system';
      const errorMessage = data.message as string || 'Erro desconhecido';

      // Update timeline if team related
      if (data.team) {
        setTeamTimeline(prev =>
          prev.map(t =>
            t.teamId === teamId
              ? { ...t, status: 'error' as const, endTime: timestamp }
              : t
          )
        );
      }

      setActivities(prev => [{
        id: `${Date.now()}-error`,
        team: teamId,
        type: 'error',
        message: errorMessage,
        timestamp
      }, ...prev]);
    }

    // Phase change events
    if (type === 'phase_changed' || data.phase) {
      const phase = (data.phase as string)?.toLowerCase() as ProjectPhase;
      if (phase && ['requirements', 'planning', 'architecture', 'development', 'testing', 'deployment'].includes(phase)) {
        setCurrentPhase(phase);
      }
    }
  }, [activeTeam]);

  // Connect to WebSocket with auto-reconnect
  const connect = useCallback(() => {
    if (socket.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    console.log(`[WS] Connecting to ${SOCKET_URL}...`);
    socket.current = new WebSocket(SOCKET_URL);

    socket.current.onopen = () => {
      console.log('[WS] Connected successfully');
      setIsConnected(true);
      reconnectAttempts.current = 0; // Reset reconnect attempts on successful connection
    };

    socket.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        console.log('[WS] Received message:', message.type);
        setMessages((prev) => [...prev, message]);
        processMessage(message);
      } catch (e) {
        console.error('[WS] Failed to parse message:', e);
      }
    };

    socket.current.onclose = (event) => {
      console.log(`[WS] Disconnected (code: ${event.code}, reason: ${event.reason})`);
      setIsConnected(false);

      // Auto-reconnect if not a normal close
      if (event.code !== 1000 && reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts.current++;
        console.log(`[WS] Reconnecting in ${RECONNECT_DELAY}ms (attempt ${reconnectAttempts.current}/${MAX_RECONNECT_ATTEMPTS})`);
        reconnectTimeout.current = setTimeout(() => {
          connect();
        }, RECONNECT_DELAY);
      }
    };

    socket.current.onerror = (error) => {
      console.error('[WS] Error:', error);
    };
  }, [processMessage]);

  // Initial connection
  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      socket.current?.close(1000, 'Component unmounting');
    };
  }, [connect]);

  const sendMessage = useCallback((msg: unknown) => {
    if (socket.current?.readyState === WebSocket.OPEN) {
      socket.current.send(JSON.stringify(msg));
    } else {
      console.warn('[WS] Cannot send message: not connected');
    }
  }, []);

  const reconnect = useCallback(() => {
    console.log('[WS] Manual reconnect requested');
    reconnectAttempts.current = 0;
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }
    socket.current?.close();
    setTimeout(() => connect(), 100);
  }, [connect]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setActivities([]);
    setTeamTimeline([]);
    setTeamsStarted(new Set());
    setTeamsCompleted(new Set());
    setCurrentPhase('idle');
    setActiveTeam(null);
    setActiveTeamAction(null);
    setProjectStartTime(null);
  }, []);

  return {
    messages,
    isConnected,
    sendMessage,
    currentPhase,
    activeTeam,
    activeTeamAction,
    projectProgress,
    projectStartTime,
    teamTimeline,
    activities,
    clearMessages,
    reconnect
  };
};

// Helper functions
function formatTeamName(teamId: string): string {
  const names: Record<string, string> = {
    'product_owner': 'Product Owner',
    'project_manager': 'Project Manager',
    'data_engineering': 'Engenharia de Dados',
    'data_science': 'Ciência de Dados',
    'governance': 'Governança',
    'observability': 'Observabilidade',
    'qa': 'Time de QA',
    'architecture': 'Arquitetura',
    'devops': 'DevOps',
    'security': 'Segurança'
  };
  return names[teamId] || teamId.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function getTeamColor(teamId: string): string {
  const colors: Record<string, string> = {
    'product_owner': 'purple',
    'project_manager': 'blue',
    'data_engineering': 'green',
    'data_science': 'yellow',
    'governance': 'red',
    'observability': 'cyan',
    'qa': 'orange',
    'architecture': 'indigo',
    'devops': 'emerald',
    'security': 'rose'
  };
  return colors[teamId] || 'gray';
}
