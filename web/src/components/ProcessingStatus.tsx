import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare,
  Brain,
  CheckCircle2,
  Loader2,
  AlertCircle,
  Users,
  FileText,
  Sparkles,
  Code2,
  Shield,
  Eye,
  TestTube,
  BarChart3,
  ChevronDown,
  ChevronUp,
  Clock,
  Star
} from 'lucide-react';
import { formatDuration } from '../types';

export interface ProcessStep {
  id: string;
  label: string;
  status: 'pending' | 'active' | 'completed' | 'error';
  detail?: string;
  startTime?: Date;
  endTime?: Date;
  qualityScore?: number;
  progress?: number;
}

interface ProcessingStatusProps {
  isActive?: boolean;
  steps: ProcessStep[];
}

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  isActive = false,
  steps
}) => {
  const [expandedStep, setExpandedStep] = useState<string | null>(null);

  const getIcon = (stepId: string, status: string) => {
    if (status === 'active') {
      return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />;
    }
    if (status === 'completed') {
      return <CheckCircle2 className="w-5 h-5 text-green-400" />;
    }
    if (status === 'error') {
      return <AlertCircle className="w-5 h-5 text-red-400" />;
    }

    // Ícones por tipo de step
    const iconMap: Record<string, React.ReactNode> = {
      'received': <MessageSquare className="w-5 h-5 text-gray-500" />,
      'analyzing': <Brain className="w-5 h-5 text-gray-500" />,
      'product_owner': <FileText className="w-5 h-5 text-purple-400" />,
      'project_manager': <BarChart3 className="w-5 h-5 text-blue-400" />,
      'data_engineering': <Code2 className="w-5 h-5 text-green-400" />,
      'data_science': <Sparkles className="w-5 h-5 text-yellow-400" />,
      'governance': <Shield className="w-5 h-5 text-red-400" />,
      'observability': <Eye className="w-5 h-5 text-cyan-400" />,
      'qa': <TestTube className="w-5 h-5 text-orange-400" />,
      'planning': <Users className="w-5 h-5 text-gray-500" />,
    };

    return iconMap[stepId] || <CheckCircle2 className="w-5 h-5 text-gray-500" />;
  };

  const getStepColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'border-blue-500 bg-blue-500/10';
      case 'completed':
        return 'border-green-500/50 bg-green-500/5';
      case 'error':
        return 'border-red-500 bg-red-500/10';
      default:
        return 'border-gray-700 bg-gray-800/30';
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 70) return 'text-yellow-400';
    if (score >= 50) return 'text-orange-400';
    return 'text-red-400';
  };

  const completedCount = steps.filter(s => s.status === 'completed').length;
  const totalCount = steps.length;

  return (
    <div className="bg-gray-800/50 rounded-xl p-4 backdrop-blur-sm border border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          {isActive ? (
            <>
              <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
              <span className="text-blue-400 font-medium">Processando...</span>
            </>
          ) : (
            <>
              <CheckCircle2 className="w-5 h-5 text-green-400" />
              <span className="text-green-400 font-medium">Completo</span>
            </>
          )}
        </div>

        {/* Contador de steps */}
        <div className="text-xs text-gray-400">
          {completedCount}/{totalCount} etapas
        </div>
      </div>

      {/* Lista de steps */}
      <div className="space-y-2">
        <AnimatePresence initial={false}>
          {steps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ delay: index * 0.05 }}
            >
              <div
                className={`rounded-lg border transition-all duration-300 ${getStepColor(step.status)} ${
                  step.detail ? 'cursor-pointer' : ''
                }`}
                onClick={() => step.detail && setExpandedStep(expandedStep === step.id ? null : step.id)}
              >
                {/* Step header */}
                <div className="flex items-center gap-3 p-3">
                  <div className="shrink-0">
                    {getIcon(step.id, step.status)}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className={`font-medium text-sm ${
                      step.status === 'active' ? 'text-blue-300' :
                        step.status === 'completed' ? 'text-green-300' :
                          step.status === 'error' ? 'text-red-300' :
                            'text-gray-400'
                    }`}>
                      {step.label}
                    </div>

                    {/* Barra de progresso para steps ativos */}
                    {step.status === 'active' && step.progress !== undefined && (
                      <div className="mt-2">
                        <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${step.progress}%` }}
                            className="h-full bg-blue-400 rounded-full"
                          />
                        </div>
                        <span className="text-[10px] text-gray-500 mt-1">
                          {step.progress}%
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Indicadores à direita */}
                  <div className="flex items-center gap-2">
                    {/* Duração */}
                    {step.status === 'completed' && step.startTime && (
                      <div className="flex items-center gap-1 text-xs text-gray-500">
                        <Clock className="w-3 h-3" />
                        <span>{formatDuration(step.startTime, step.endTime)}</span>
                      </div>
                    )}

                    {/* Indicador de qualidade */}
                    {step.status === 'completed' && step.qualityScore !== undefined && (
                      <div className={`flex items-center gap-1 text-xs ${getQualityColor(step.qualityScore)}`}>
                        <Star className="w-3 h-3" />
                        <span>{step.qualityScore}</span>
                      </div>
                    )}

                    {/* Checkmark */}
                    {step.status === 'completed' && (
                      <span className="text-xs text-green-500">✓</span>
                    )}

                    {/* Expand indicator */}
                    {step.detail && (
                      <div className="text-gray-500">
                        {expandedStep === step.id ? (
                          <ChevronUp className="w-4 h-4" />
                        ) : (
                          <ChevronDown className="w-4 h-4" />
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Detalhes expandidos */}
                <AnimatePresence>
                  {expandedStep === step.id && step.detail && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      <div className="px-3 pb-3 pt-0">
                        <div className="text-xs text-gray-400 bg-gray-900/50 rounded-lg p-2 border border-gray-700">
                          {step.detail}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};
