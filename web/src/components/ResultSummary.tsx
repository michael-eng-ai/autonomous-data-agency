import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bot,
  Briefcase,
  Code2,
  BarChart3,
  Shield,
  Eye,
  TestTube,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Star
} from 'lucide-react';

interface ResultSummaryProps {
  results: {
    agent: string;
    output: string;
    timestamp?: string;
    qualityScore?: number;
    isStreaming?: boolean;
  }[];
}

const agentConfig: Record<string, { icon: React.ReactNode; color: string; label: string; labelPtBr: string }> = {
  product_owner: {
    icon: <Briefcase className="w-5 h-5" />,
    color: 'bg-purple-500',
    label: 'Product Owner',
    labelPtBr: 'Dono do Produto'
  },
  project_manager: {
    icon: <BarChart3 className="w-5 h-5" />,
    color: 'bg-blue-500',
    label: 'Project Manager',
    labelPtBr: 'Gerente de Projeto'
  },
  data_engineering: {
    icon: <Code2 className="w-5 h-5" />,
    color: 'bg-green-500',
    label: 'Data Engineering',
    labelPtBr: 'Engenharia de Dados'
  },
  data_science: {
    icon: <Sparkles className="w-5 h-5" />,
    color: 'bg-yellow-500',
    label: 'Data Science',
    labelPtBr: 'Ciência de Dados'
  },
  governance: {
    icon: <Shield className="w-5 h-5" />,
    color: 'bg-red-500',
    label: 'Governance',
    labelPtBr: 'Governança'
  },
  observability: {
    icon: <Eye className="w-5 h-5" />,
    color: 'bg-cyan-500',
    label: 'Observability',
    labelPtBr: 'Observabilidade'
  },
  qa: {
    icon: <TestTube className="w-5 h-5" />,
    color: 'bg-orange-500',
    label: 'QA',
    labelPtBr: 'Qualidade'
  },
  default: {
    icon: <Bot className="w-5 h-5" />,
    color: 'bg-gray-500',
    label: 'Agent',
    labelPtBr: 'Agente'
  }
};

// Componente de card individual
const ResultCard: React.FC<{
  result: ResultSummaryProps['results'][0];
  index: number;
}> = ({ result, index }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [copied, setCopied] = useState(false);
  const [displayedText, setDisplayedText] = useState('');

  const getAgentConfig = (agent: string) => {
    const key = agent.toLowerCase().replace(/\s+/g, '_');
    return agentConfig[key] || agentConfig.default;
  };

  const config = getAgentConfig(result.agent);

  // Efeito typewriter para streaming
  useEffect(() => {
    if (!result.isStreaming) {
      return;
    }

    let currentIndex = 0;
    const text = result.output;

    const interval = setInterval(() => {
      if (currentIndex <= text.length) {
        setDisplayedText(text.slice(0, currentIndex));
        currentIndex += 3; // 3 caracteres por vez para ser mais rápido
      } else {
        clearInterval(interval);
      }
    }, 10);

    return () => clearInterval(interval);
  }, [result.output, result.isStreaming]);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(result.output);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getQualityColor = (score: number) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 70) return 'text-yellow-400';
    if (score >= 50) return 'text-orange-400';
    return 'text-red-400';
  };

  const formatOutput = (output: string) => {
    const lines = output.split('\n');
    return lines.map((line, idx) => {
      // Headers
      if (line.startsWith('##')) {
        return (
          <h4 key={idx} className="text-sm font-semibold text-white mt-3 mb-1">
            {line.replace(/^#+\s*/, '')}
          </h4>
        );
      }

      // Code blocks
      if (line.startsWith('```')) {
        return (
          <div key={idx} className="my-2 p-2 bg-gray-950 rounded border border-gray-700 font-mono text-xs">
            {line.replace(/```\w*/g, '')}
          </div>
        );
      }

      // Lists
      if (line.startsWith('- ') || line.startsWith('* ')) {
        return (
          <li key={idx} className="text-sm text-gray-300 ml-4 list-disc">
            {line.replace(/^[-*]\s*/, '')}
          </li>
        );
      }

      // Bold text
      if (line.startsWith('**') && line.endsWith('**')) {
        return (
          <p key={idx} className="text-sm font-medium text-blue-300 mt-2">
            {line.replace(/\*\*/g, '')}
          </p>
        );
      }

      // Regular text
      if (line.trim()) {
        return (
          <p key={idx} className="text-sm text-gray-300">
            {line}
          </p>
        );
      }

      return null;
    });
  };

  // Preview para card colapsado
  const getPreview = (text: string) => {
    const firstLine = text.split('\n').find(l => l.trim()) || '';
    return firstLine.slice(0, 100) + (firstLine.length > 100 ? '...' : '');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-gray-800/50 rounded-xl border border-gray-700 overflow-hidden"
    >
      {/* Header do agente */}
      <div
        className={`${config.color} p-3 flex items-center justify-between cursor-pointer`}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/20 rounded-lg text-white">
            {config.icon}
          </div>
          <div>
            <h3 className="font-semibold text-white">{config.labelPtBr}</h3>
            <div className="flex items-center gap-2">
              {result.timestamp && (
                <p className="text-xs text-white/70">
                  {new Date(result.timestamp).toLocaleTimeString('pt-BR')}
                </p>
              )}
              {result.qualityScore !== undefined && (
                <div className={`flex items-center gap-1 text-xs ${getQualityColor(result.qualityScore)}`}>
                  <Star className="w-3 h-3" />
                  <span>{result.qualityScore}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Botão copiar */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleCopy();
            }}
            className="p-1.5 rounded-lg bg-white/10 text-white/70 hover:text-white hover:bg-white/20 transition-colors"
            title="Copiar resultado"
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
          </button>

          {/* Botão expandir */}
          <div className="text-white/70">
            {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </div>
        </div>
      </div>

      {/* Conteúdo */}
      <AnimatePresence initial={false}>
        {isExpanded ? (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="p-4 max-h-72 overflow-y-auto custom-scrollbar">
              <div className="prose prose-invert prose-sm max-w-none">
                {formatOutput(result.isStreaming ? displayedText : result.output)}
                {result.isStreaming && (
                  <span className="inline-block w-2 h-4 bg-blue-400 animate-pulse ml-0.5" />
                )}
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
          >
            <div className="px-4 py-2 text-xs text-gray-500 truncate border-t border-gray-700/50">
              {getPreview(result.output)}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export const ResultSummary: React.FC<ResultSummaryProps> = ({ results }) => {
  if (results.length === 0) {
    return (
      <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6 text-center">
        <Bot className="w-12 h-12 text-gray-600 mx-auto mb-3" />
        <p className="text-gray-500 text-sm">
          Aguardando resultados dos agentes...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <AnimatePresence>
        {results.map((result, idx) => (
          <ResultCard key={`${result.agent}-${idx}`} result={result} index={idx} />
        ))}
      </AnimatePresence>
    </div>
  );
};
