import { useState, useEffect, useCallback } from 'react';
import { ClientChat } from './components/ClientChat';
import { ProcessingStatus, type ProcessStep } from './components/ProcessingStatus';
import { ResultSummary } from './components/ResultSummary';
import { EventLog } from './components/EventLog';
import { useWebSocket } from './useWebSocket';
import { Cpu, Wifi, WifiOff, Github, Sparkles } from 'lucide-react';

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

function App() {
  const { messages, isConnected } = useWebSocket();
  const [allEvents, setAllEvents] = useState<WebSocketEvent[]>([]);
  const [processingSteps, setProcessingSteps] = useState<ProcessStep[]>([]);
  const [agentResults, setAgentResults] = useState<{ agent: string; output: string; timestamp?: string }[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const formatTeamName = useCallback((name: string) => {
    const names: Record<string, string> = {
      'product_owner': 'Product Owner',
      'project_manager': 'Project Manager',
      'data_engineering': 'Data Engineering',
      'data_science': 'Data Science',
      'governance': 'Governance',
      'observability': 'Observability',
      'qa': 'QA Team'
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

      // Atualizar steps de processamento baseado no tipo de evento
      if (lastMsg.type === 'team_execution_started') {
        const teamName = lastMsg.data?.team || 'agent';
        setProcessingSteps(prev => {
          const existing = prev.find(s => s.id === teamName);
          if (existing) {
            return prev.map(s => s.id === teamName ? { ...s, status: 'active' } : s);
          }
          return [...prev, { 
            id: teamName, 
            label: formatTeamName(teamName), 
            status: 'active',
            detail: 'Executando...'
          }];
        });
      }
      
      if (lastMsg.type === 'team_execution_completed') {
        const teamName = lastMsg.data?.team || 'agent';
        setProcessingSteps(prev => 
          prev.map(s => s.id === teamName ? { ...s, status: 'completed', detail: 'Concluído' } : s)
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

      if (lastMsg.type === 'project_phase_completed') {
        // Não limpar, manter o histórico
      }
    }
  }, [messages, formatTeamName]);

  const handleProcessingStart = () => {
    setIsProcessing(true);
    setProcessingSteps([{ id: 'received', label: 'Mensagem Recebida', status: 'active' }]);
    setAgentResults([]);
  };

  const handleProcessingEnd = () => {
    setProcessingSteps(prev => 
      prev.map(s => s.id === 'received' ? { ...s, status: 'completed' } : s)
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white">
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

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Chat */}
          <div className="h-[calc(100vh-140px)] min-h-[500px]">
            <ClientChat 
              onProcessingStart={handleProcessingStart}
              onProcessingEnd={handleProcessingEnd}
            />
          </div>

          {/* Right Column: Status & Results */}
          <div className="space-y-6 h-[calc(100vh-140px)] overflow-y-auto custom-scrollbar pr-2">
            {/* Processing Status */}
            {(isProcessing || processingSteps.length > 0) && (
              <ProcessingStatus 
                steps={processingSteps} 
                isActive={isProcessing} 
              />
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
