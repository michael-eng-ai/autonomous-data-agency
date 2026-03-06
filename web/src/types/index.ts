// Tipos compartilhados para Autonomous Data Agency

// Fases do projeto
export type ProjectPhase =
  | 'idle'
  | 'requirements'
  | 'planning'
  | 'architecture'
  | 'development'
  | 'testing'
  | 'deployment'
  | 'completed';

// Identificadores de times
export type TeamId =
  | 'product_owner'
  | 'project_manager'
  | 'architecture'
  | 'frontend'
  | 'backend'
  | 'mobile'
  | 'fullstack'
  | 'database'
  | 'data_engineering'
  | 'data_science'
  | 'data_analytics'
  | 'devops'
  | 'qa'
  | 'security'
  | 'ux_ui'
  | 'governance'
  | 'observability';

// Status de etapas
export type StepStatus = 'pending' | 'active' | 'completed' | 'error';

// Tipos de mensagem de atividade
export type ActivityType = 'thinking' | 'action' | 'result' | 'question' | 'info' | 'error';

// Tipos de notificação
export type NotificationType = 'success' | 'warning' | 'error' | 'info';

// Configuração de time
export interface TeamConfig {
  id: TeamId;
  name: string;
  namePtBr: string;
  icon: string;
  color: string;
  bgColor: string;
  borderColor: string;
  description: string;
}

// Mapa de configuração de times
export const TEAM_CONFIG: Record<string, TeamConfig> = {
  product_owner: {
    id: 'product_owner',
    name: 'Product Owner',
    namePtBr: 'Dono do Produto',
    icon: 'Briefcase',
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30',
    description: 'Define requisitos e prioridades do produto'
  },
  project_manager: {
    id: 'project_manager',
    name: 'Project Manager',
    namePtBr: 'Gerente de Projeto',
    icon: 'BarChart3',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    description: 'Coordena execução e entregas'
  },
  data_engineering: {
    id: 'data_engineering',
    name: 'Data Engineering',
    namePtBr: 'Engenharia de Dados',
    icon: 'Code2',
    color: 'text-green-400',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    description: 'Desenvolve pipelines e infraestrutura de dados'
  },
  data_science: {
    id: 'data_science',
    name: 'Data Science',
    namePtBr: 'Ciência de Dados',
    icon: 'Sparkles',
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/30',
    description: 'Cria modelos e análises avançadas'
  },
  governance: {
    id: 'governance',
    name: 'Governance',
    namePtBr: 'Governança',
    icon: 'Shield',
    color: 'text-red-400',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
    description: 'Garante conformidade e qualidade dos dados'
  },
  observability: {
    id: 'observability',
    name: 'Observability',
    namePtBr: 'Observabilidade',
    icon: 'Eye',
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-500/10',
    borderColor: 'border-cyan-500/30',
    description: 'Monitora e garante visibilidade do sistema'
  },
  qa: {
    id: 'qa',
    name: 'QA Team',
    namePtBr: 'Qualidade',
    icon: 'TestTube',
    color: 'text-orange-400',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/30',
    description: 'Testa e valida a qualidade das entregas'
  },
  architecture: {
    id: 'architecture',
    name: 'Architecture',
    namePtBr: 'Arquitetura',
    icon: 'Layers',
    color: 'text-indigo-400',
    bgColor: 'bg-indigo-500/10',
    borderColor: 'border-indigo-500/30',
    description: 'Define arquitetura e padrões técnicos'
  },
  devops: {
    id: 'devops',
    name: 'DevOps',
    namePtBr: 'DevOps',
    icon: 'Server',
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/10',
    borderColor: 'border-emerald-500/30',
    description: 'Automatiza deploy e infraestrutura'
  },
  security: {
    id: 'security',
    name: 'Security',
    namePtBr: 'Segurança',
    icon: 'Lock',
    color: 'text-rose-400',
    bgColor: 'bg-rose-500/10',
    borderColor: 'border-rose-500/30',
    description: 'Garante segurança e proteção de dados'
  }
};

// Configuração de fases
export const PHASE_CONFIG: Record<ProjectPhase, {
  label: string;
  labelPtBr: string;
  color: string;
  bgColor: string;
  order: number;
}> = {
  idle: {
    label: 'Idle',
    labelPtBr: 'Aguardando',
    color: 'text-gray-400',
    bgColor: 'bg-gray-500/10',
    order: 0
  },
  requirements: {
    label: 'Requirements',
    labelPtBr: 'Requisitos',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    order: 1
  },
  planning: {
    label: 'Planning',
    labelPtBr: 'Planejamento',
    color: 'text-indigo-400',
    bgColor: 'bg-indigo-500/10',
    order: 2
  },
  architecture: {
    label: 'Architecture',
    labelPtBr: 'Arquitetura',
    color: 'text-violet-400',
    bgColor: 'bg-violet-500/10',
    order: 3
  },
  development: {
    label: 'Development',
    labelPtBr: 'Desenvolvimento',
    color: 'text-green-400',
    bgColor: 'bg-green-500/10',
    order: 4
  },
  testing: {
    label: 'Testing',
    labelPtBr: 'Testes',
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/10',
    order: 5
  },
  deployment: {
    label: 'Deployment',
    labelPtBr: 'Deploy',
    color: 'text-orange-400',
    bgColor: 'bg-orange-500/10',
    order: 6
  },
  completed: {
    label: 'Completed',
    labelPtBr: 'Concluído',
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/10',
    order: 7
  },
};

// Interface de etapa de processamento
export interface ProcessStep {
  id: string;
  label: string;
  status: StepStatus;
  detail?: string;
  startTime?: Date;
  endTime?: Date;
  qualityScore?: number;
  progress?: number;
}

// Interface de entrada da timeline
export interface TeamTimelineEntry {
  teamId: string;
  teamName: string;
  status: StepStatus;
  startTime?: Date;
  endTime?: Date;
  color: string;
}

// Interface de mensagem de atividade
export interface ActivityMessage {
  id: string;
  team: string;
  type: ActivityType;
  message: string;
  timestamp: Date;
  metadata?: Record<string, unknown>;
}

// Interface de notificação
export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: Date;
  autoDismiss?: boolean;
  duration?: number;
  action?: { label: string; onClick: () => void };
}

// Interface de resultado de agente
export interface AgentResult {
  agent: string;
  output: string;
  timestamp?: string;
  qualityScore?: number;
  isStreaming?: boolean;
}

// Interface de evento WebSocket
export interface WebSocketEvent {
  type: string;
  data: WebSocketEventData;
  timestamp: string;
}

export interface WebSocketEventData {
  team?: string;
  result?: string;
  summary?: string;
  phase?: string;
  message?: string;
  [key: string]: unknown;
}

// Helper para obter config do time
export function getTeamConfig(teamId: string): TeamConfig {
  return TEAM_CONFIG[teamId] || {
    id: teamId as TeamId,
    name: teamId.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
    namePtBr: teamId.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
    icon: 'Bot',
    color: 'text-gray-400',
    bgColor: 'bg-gray-500/10',
    borderColor: 'border-gray-500/30',
    description: 'Agente de processamento'
  };
}

// Helper para formatar duração
export function formatDuration(startTime: Date, endTime?: Date): string {
  const end = endTime || new Date();
  const diffMs = end.getTime() - startTime.getTime();
  const diffSec = Math.floor(diffMs / 1000);

  if (diffSec < 60) {
    return `${diffSec}s`;
  }

  const minutes = Math.floor(diffSec / 60);
  const seconds = diffSec % 60;

  if (minutes < 60) {
    return `${minutes}m ${seconds}s`;
  }

  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
}

// Helper para calcular progresso
export function calculateProgress(teamsCompleted: number, totalTeams: number): number {
  if (totalTeams === 0) return 0;
  return Math.round((teamsCompleted / totalTeams) * 100);
}
