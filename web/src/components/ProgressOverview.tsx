import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Clock, CheckCircle2, Loader2, Target } from 'lucide-react';
import type { ProjectPhase } from '../types';
import { PHASE_CONFIG, formatDuration, calculateProgress } from '../types';

interface ProgressOverviewProps {
  currentPhase: ProjectPhase;
  teamsCompleted: number;
  totalTeams: number;
  startTime: Date | null;
  isActive: boolean;
}

export const ProgressOverview: React.FC<ProgressOverviewProps> = ({
  currentPhase,
  teamsCompleted,
  totalTeams,
  startTime,
  isActive
}) => {
  const [elapsed, setElapsed] = useState<string>('0s');
  const progress = calculateProgress(teamsCompleted, totalTeams);
  const phaseConfig = PHASE_CONFIG[currentPhase];

  // Atualiza tempo decorrido
  useEffect(() => {
    if (!startTime || !isActive) return;

    const interval = setInterval(() => {
      setElapsed(formatDuration(startTime));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime, isActive]);

  // Estima tempo restante baseado no progresso
  const estimatedRemaining = React.useMemo(() => {
    if (!startTime || progress === 0) return null;

    const elapsedMs = Date.now() - startTime.getTime();
    const estimatedTotalMs = (elapsedMs / progress) * 100;
    const remainingMs = estimatedTotalMs - elapsedMs;

    if (remainingMs <= 0) return 'finalizando...';

    const remainingSec = Math.floor(remainingMs / 1000);
    if (remainingSec < 60) return `~${remainingSec}s`;

    const minutes = Math.floor(remainingSec / 60);
    return `~${minutes}min`;
  }, [startTime, progress]);

  if (!isActive && currentPhase === 'idle') return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gray-800/50 rounded-xl p-4 backdrop-blur-sm border border-gray-700"
    >
      {/* Header com fase atual */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          {isActive ? (
            <div className="relative">
              <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
              <div className="absolute inset-0 bg-blue-400/20 rounded-full animate-ping" />
            </div>
          ) : (
            <CheckCircle2 className="w-5 h-5 text-green-400" />
          )}
          <div>
            <span className={`text-sm font-medium ${isActive ? 'text-blue-400' : 'text-green-400'}`}>
              {isActive ? 'Processando Projeto' : 'Projeto Concluído'}
            </span>
          </div>
        </div>

        {/* Badge da fase */}
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${phaseConfig.bgColor} ${phaseConfig.color}`}>
          {phaseConfig.labelPtBr}
        </div>
      </div>

      {/* Barra de progresso */}
      <div className="mb-4">
        <div className="flex justify-between text-xs mb-2">
          <span className="text-gray-400">Progresso Geral</span>
          <span className="text-white font-medium">{progress}%</span>
        </div>
        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className={`h-full rounded-full ${
              progress === 100
                ? 'bg-gradient-to-r from-green-500 to-emerald-400'
                : 'bg-gradient-to-r from-blue-500 to-purple-500'
            }`}
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        {/* Times completados */}
        <div className="bg-gray-900/50 rounded-lg p-3 text-center">
          <div className="flex items-center justify-center gap-1 text-gray-400 mb-1">
            <Target className="w-3 h-3" />
            <span className="text-xs">Times</span>
          </div>
          <div className="text-lg font-bold text-white">
            {teamsCompleted}/{totalTeams}
          </div>
        </div>

        {/* Tempo decorrido */}
        <div className="bg-gray-900/50 rounded-lg p-3 text-center">
          <div className="flex items-center justify-center gap-1 text-gray-400 mb-1">
            <Clock className="w-3 h-3" />
            <span className="text-xs">Decorrido</span>
          </div>
          <div className="text-lg font-bold text-white">
            {elapsed}
          </div>
        </div>

        {/* Tempo restante estimado */}
        <div className="bg-gray-900/50 rounded-lg p-3 text-center">
          <div className="flex items-center justify-center gap-1 text-gray-400 mb-1">
            <Clock className="w-3 h-3" />
            <span className="text-xs">Restante</span>
          </div>
          <div className="text-lg font-bold text-white">
            {estimatedRemaining || '--'}
          </div>
        </div>
      </div>

      {/* Indicador de fases */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="flex justify-between items-center">
          {Object.entries(PHASE_CONFIG)
            .filter(([key]) => key !== 'idle')
            .sort((a, b) => a[1].order - b[1].order)
            .map(([key, config], index, arr) => {
              const isCurrent = key === currentPhase;
              const isPast = config.order < phaseConfig.order;
              const isCompleted = key === 'completed' && currentPhase === 'completed';

              return (
                <React.Fragment key={key}>
                  <div className="flex flex-col items-center">
                    <div
                      className={`w-2 h-2 rounded-full transition-all ${
                        isCurrent
                          ? 'w-3 h-3 bg-blue-400 ring-4 ring-blue-400/20'
                          : isPast || isCompleted
                            ? 'bg-green-400'
                            : 'bg-gray-600'
                      }`}
                    />
                    <span
                      className={`text-[10px] mt-1 ${
                        isCurrent ? 'text-blue-400 font-medium' : isPast ? 'text-green-400' : 'text-gray-500'
                      }`}
                    >
                      {config.labelPtBr.slice(0, 3)}
                    </span>
                  </div>
                  {index < arr.length - 1 && (
                    <div
                      className={`flex-1 h-0.5 mx-1 ${
                        isPast ? 'bg-green-400' : 'bg-gray-700'
                      }`}
                    />
                  )}
                </React.Fragment>
              );
            })}
        </div>
      </div>
    </motion.div>
  );
};
