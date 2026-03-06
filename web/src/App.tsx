import { useState, useEffect, useCallback } from 'react';
import { ClientChat } from './components/ClientChat';
import { ProcessingStatus, type ProcessStep } from './components/ProcessingStatus';
import { ResultSummary } from './components/ResultSummary';
import { EventLog } from './components/EventLog';
import { ProgressOverview } from './components/ProgressOverview';
import { ActiveTeamIndicator } from './components/ActiveTeamIndicator';
import { LiveActivityFeed } from './components/LiveActivityFeed';
import { TeamTimeline } from './components/TeamTimeline';
import { NotificationToast } from './components/NotificationToast';
import { ConversationHistory } from './components/ConversationHistory';
import { QuotaStatus } from './components/QuotaStatus';
import { useWebSocket } from './useWebSocket';
import { useNotifications, createNotificationFromEvent } from './hooks/useNotifications';
import { Cpu, Wifi, WifiOff, Github, Sparkles, LayoutGrid, Clock, PanelLeftClose, PanelLeft } from 'lucide-react';

interface WebSocketEventData {
  team?: string;
  result?: string;
  summary?: string;
  [key: string]: unknown;
}

interface WebSocketEvent {
  type: string;
  data: WebSocketEventData;
  timestamp: string;
}

type ViewMode = 'steps' | 'timeline';

function App() {
  const {
    messages,
    isConnected,
    currentPhase,
    activeTeam,
    activeTeamAction,
    projectStartTime,
    teamTimeline,
    activities
  } = useWebSocket();

  const { notifications, addNotification, removeNotification } = useNotifications();

  const [allEvents, setAllEvents] = useState<WebSocketEvent[]>([]);
  const [processingSteps, setProcessingSteps] = useState<ProcessStep[]>([]);
  const [agentResults, setAgentResults] = useState<{ agent: string; output: string; timestamp?: string }[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('steps');

  // Conversation history state
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const formatTeamName = useCallback((name: string) => {
    const names: Record<string, string> = {
      'product_owner': 'Product Owner',
      'project_manager': 'Project Manager',
      'data_engineering': 'Engenharia de Dados',
      'data_science': 'Ciência de Dados',
      'governance': 'Governança',
      'observability': 'Observabilidade',
      'qa': 'Time de QA'
    };
    return names[name] || name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }, []);

  // Processar mensagens WebSocket
  useEffect(() => {
    if (messages.length > 0) {
      const lastMsg = messages[messages.length - 1];
      const eventWithTime: WebSocketEvent = {
        type: lastMsg.type ?? 'unknown',
        data: lastMsg.data ?? {},
        timestamp: new Date().toISOString()
      };

      setAllEvents(prev => [eventWithTime, ...prev]);

      // Criar notificação para eventos importantes
      const notification = createNotificationFromEvent(lastMsg.type, lastMsg.data as Record<string, unknown>);
      if (notification) {
        addNotification(notification);
      }

      // Atualizar steps de processamento baseado no tipo de evento
      if (lastMsg.type === 'team_execution_started') {
        const teamName = lastMsg.data?.team || 'agent';
        setProcessingSteps(prev => {
          const existing = prev.find(s => s.id === teamName);
          if (existing) {
            return prev.map(s => s.id === teamName
              ? { ...s, status: 'active' as const, startTime: new Date() }
              : s
            );
          }
          return [...prev, {
            id: teamName,
            label: formatTeamName(teamName),
            status: 'active' as const,
            detail: 'Executando...',
            startTime: new Date()
          }];
        });
      }

      if (lastMsg.type === 'team_execution_completed') {
        const teamName = lastMsg.data?.team || 'agent';
        setProcessingSteps(prev =>
          prev.map(s => s.id === teamName
            ? { ...s, status: 'completed' as const, detail: 'Concluído', endTime: new Date() }
            : s
          )
        );

        // Extrair resultado do agente
        if (lastMsg.data?.result) {
          setAgentResults(prev => [...prev, {
            agent: teamName,
            output: lastMsg.data?.result ?? '',
            timestamp: new Date().toISOString()
          }]);
        }
      }

      if (lastMsg.type === 'project_phase_started') {
        setIsProcessing(true);
        setProcessingSteps([{ id: 'received', label: 'Solicitação Recebida', status: 'completed' }]);
      }

      if (lastMsg.type === 'project_phase_completed' || lastMsg.type === 'project_completed') {
        setIsProcessing(false);
      }
    }
  }, [messages, formatTeamName, addNotification]);

  const handleProcessingStart = () => {
    setIsProcessing(true);
    setProcessingSteps([{ id: 'received', label: 'Mensagem Recebida', status: 'active', startTime: new Date() }]);
    setAgentResults([]);
  };

  const handleProcessingEnd = () => {
    setProcessingSteps(prev =>
      prev.map(s => s.id === 'received' ? { ...s, status: 'completed' as const } : s)
    );
  };

  // Conversation handlers
  const handleSelectConversation = (sessionId: string) => {
    setSelectedSessionId(sessionId);
  };

  const handleNewConversation = () => {
    setSelectedSessionId(null);
    setCurrentSessionId(null);
    // Reset processing state for new conversation
    setProcessingSteps([]);
    setAgentResults([]);
    setIsProcessing(false);
  };

  const handleSessionChange = (sessionId: string) => {
    setCurrentSessionId(sessionId);
  };

  const teamsCompleted = processingSteps.filter(s => s.status === 'completed').length;
  const totalTeams = Math.max(processingSteps.length, 1);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white">
      {/* Notifications */}
      <NotificationToast
        notifications={notifications}
        onDismiss={removeNotification}
      />

      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/20">
                <Cpu className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                  Autonomous Data Agency
                </h1>
                <p className="text-xs text-gray-500">Agentes de IA trabalhando para você</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs ${
                isConnected
                  ? 'bg-green-500/10 text-green-400 border border-green-500/30'
                  : 'bg-red-500/10 text-red-400 border border-red-500/30'
              }`}>
                {isConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
                {isConnected ? 'Conectado' : 'Desconectado'}
              </div>
              <a
                href="https://github.com"
                target="_blank"
                className="p-2 text-gray-400 hover:text-white transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Progress Overview - shown during processing */}
      {(isProcessing || currentPhase !== 'idle') && (
        <div className="max-w-7xl mx-auto px-4 pt-4">
          <ProgressOverview
            currentPhase={currentPhase}
            teamsCompleted={teamsCompleted}
            totalTeams={totalTeams}
            startTime={projectStartTime}
            isActive={isProcessing}
          />
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex gap-4">
          {/* Sidebar: Conversation History */}
          <div className={`transition-all duration-300 ${sidebarOpen ? 'w-64' : 'w-0 overflow-hidden'}`}>
            {sidebarOpen && (
              <div className="h-[calc(100vh-200px)] min-h-[500px]">
                <ConversationHistory
                  currentSessionId={currentSessionId}
                  onSelectConversation={handleSelectConversation}
                  onNewConversation={handleNewConversation}
                />
              </div>
            )}
          </div>

          {/* Toggle Sidebar Button */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="hidden lg:flex items-center justify-center w-6 h-10 bg-gray-800 hover:bg-gray-700 rounded-r-lg border border-l-0 border-gray-700 transition-colors self-center"
            title={sidebarOpen ? 'Fechar histórico' : 'Abrir histórico'}
          >
            {sidebarOpen ? (
              <PanelLeftClose className="w-4 h-4 text-gray-400" />
            ) : (
              <PanelLeft className="w-4 h-4 text-gray-400" />
            )}
          </button>

          {/* Main Grid */}
          <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column: Chat */}
            <div className="h-[calc(100vh-200px)] min-h-[500px]">
              <ClientChat
                onProcessingStart={handleProcessingStart}
                onProcessingEnd={handleProcessingEnd}
                externalSessionId={selectedSessionId}
                onSessionChange={handleSessionChange}
              />
            </div>

          {/* Right Column: Status & Results */}
          <div className="space-y-4 h-[calc(100vh-200px)] overflow-y-auto custom-scrollbar pr-2">
            {/* API Quota Status */}
            <QuotaStatus />

            {/* Active Team Indicator - shown when a team is working */}
            {activeTeam && (
              <ActiveTeamIndicator
                teamId={activeTeam}
                currentAction={activeTeamAction || undefined}
              />
            )}

            {/* View Mode Toggle */}
            {(isProcessing || processingSteps.length > 0) && (
              <div className="flex items-center justify-end gap-2">
                <button
                  onClick={() => setViewMode('steps')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-colors ${
                    viewMode === 'steps'
                      ? 'bg-blue-500/20 text-blue-400'
                      : 'text-gray-500 hover:text-gray-300'
                  }`}
                >
                  <LayoutGrid className="w-3 h-3" />
                  Etapas
                </button>
                <button
                  onClick={() => setViewMode('timeline')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-colors ${
                    viewMode === 'timeline'
                      ? 'bg-blue-500/20 text-blue-400'
                      : 'text-gray-500 hover:text-gray-300'
                  }`}
                >
                  <Clock className="w-3 h-3" />
                  Timeline
                </button>
              </div>
            )}

            {/* Processing Status or Timeline */}
            {(isProcessing || processingSteps.length > 0) && (
              viewMode === 'steps' ? (
                <ProcessingStatus
                  steps={processingSteps}
                  isActive={isProcessing}
                />
              ) : (
                <TeamTimeline
                  entries={teamTimeline}
                  projectStartTime={projectStartTime}
                />
              )
            )}

            {/* Live Activity Feed */}
            {activities.length > 0 && (
              <LiveActivityFeed activities={activities} />
            )}

            {/* Welcome Card - shown when no processing */}
            {!isProcessing && processingSteps.length === 0 && (
              <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-2xl border border-gray-700 p-8 text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  Bem-vindo à Data Agency
                </h3>
                <p className="text-gray-400 text-sm max-w-md mx-auto">
                  Descreva seu projeto de dados no chat e nossa equipe de agentes de IA irá
                  analisar, planejar e executar a solução automaticamente.
                </p>
                <div className="mt-6 flex flex-wrap justify-center gap-2">
                  {['Pipeline ETL', 'Dashboard', 'ML Model', 'Data Quality'].map(tag => (
                    <span key={tag} className="px-3 py-1 bg-gray-700/50 rounded-full text-xs text-gray-400">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Agent Results */}
            {agentResults.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Resultados dos Agentes
                </h3>
                <ResultSummary results={agentResults} />
              </div>
            )}

            {/* Event Log - Collapsible */}
            <EventLog events={allEvents} />
          </div>
          </div>
        </div>
      </main>

      {/* Styles for scrollbar */}
      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(107, 114, 128, 0.5);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(107, 114, 128, 0.7);
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}

export default App;
