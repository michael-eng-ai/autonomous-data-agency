import React from 'react';
import { motion } from 'framer-motion';
import { Clock, CheckCircle2, Loader2, AlertCircle } from 'lucide-react';
import type { TeamTimelineEntry } from '../types';
import { getTeamConfig, formatDuration } from '../types';

interface TeamTimelineProps {
  entries: TeamTimelineEntry[];
  projectStartTime: Date | null;
}

export const TeamTimeline: React.FC<TeamTimelineProps> = ({
  entries,
  projectStartTime
}) => {
  if (!projectStartTime || entries.length === 0) return null;

  // Calcula a duração total do projeto até agora
  const now = new Date();
  const totalDurationMs = now.getTime() - projectStartTime.getTime();

  // Função para calcular a posição e largura de cada barra
  const getBarStyle = (entry: TeamTimelineEntry) => {
    if (!entry.startTime) {
      return { left: '0%', width: '0%' };
    }

    const startOffset = entry.startTime.getTime() - projectStartTime.getTime();
    const endTime = entry.endTime || now;
    const duration = endTime.getTime() - entry.startTime.getTime();

    const left = (startOffset / totalDurationMs) * 100;
    const width = (duration / totalDurationMs) * 100;

    return {
      left: `${Math.max(0, left)}%`,
      width: `${Math.min(100 - left, Math.max(5, width))}%`
    };
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <Loader2 className="w-3 h-3 animate-spin" />;
      case 'completed':
        return <CheckCircle2 className="w-3 h-3" />;
      case 'error':
        return <AlertCircle className="w-3 h-3" />;
      default:
        return <Clock className="w-3 h-3" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'from-blue-500 to-cyan-500';
      case 'completed':
        return 'from-green-500 to-emerald-500';
      case 'error':
        return 'from-red-500 to-orange-500';
      default:
        return 'from-gray-500 to-gray-400';
    }
  };

  return (
    <div className="bg-gray-800/50 rounded-xl p-4 backdrop-blur-sm border border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-cyan-400" />
          <span className="text-sm font-medium text-gray-300">Timeline de Execução</span>
        </div>
        <span className="text-xs text-gray-500">
          Duração: {formatDuration(projectStartTime)}
        </span>
      </div>

      {/* Timeline */}
      <div className="space-y-3">
        {entries.map((entry) => {
          const teamConfig = getTeamConfig(entry.teamId);
          const barStyle = getBarStyle(entry);

          return (
            <div key={entry.teamId} className="group">
              {/* Label do time */}
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-medium ${teamConfig.color}`}>
                    {teamConfig.namePtBr}
                  </span>
                  <span className={`${
                    entry.status === 'active' ? 'text-blue-400' :
                      entry.status === 'completed' ? 'text-green-400' :
                        entry.status === 'error' ? 'text-red-400' :
                          'text-gray-500'
                  }`}>
                    {getStatusIcon(entry.status)}
                  </span>
                </div>

                {/* Duração */}
                {entry.startTime && (
                  <span className="text-[10px] text-gray-500">
                    {formatDuration(entry.startTime, entry.endTime)}
                  </span>
                )}
              </div>

              {/* Barra de timeline */}
              <div className="relative h-6 bg-gray-900/50 rounded-lg overflow-hidden">
                {entry.startTime ? (
                  <motion.div
                    initial={{ width: 0, opacity: 0 }}
                    animate={{
                      width: barStyle.width,
                      opacity: 1,
                      left: barStyle.left
                    }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                    className={`absolute top-0 h-full rounded-lg bg-gradient-to-r ${getStatusColor(entry.status)} ${
                      entry.status === 'active' ? 'animate-pulse' : ''
                    }`}
                    style={{ left: barStyle.left }}
                  >
                    {/* Shimmer effect for active */}
                    {entry.status === 'active' && (
                      <motion.div
                        animate={{ x: ['-100%', '200%'] }}
                        transition={{
                          duration: 1.5,
                          repeat: Infinity,
                          ease: 'linear'
                        }}
                        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                      />
                    )}
                  </motion.div>
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center text-[10px] text-gray-600">
                    Aguardando...
                  </div>
                )}

                {/* Tooltip on hover */}
                {entry.startTime && (
                  <div className="absolute inset-0 flex items-center px-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-[10px] text-white/80 truncate">
                      {entry.status === 'active' ? 'Em execução...' :
                        entry.status === 'completed' ? 'Concluído' :
                          entry.status === 'error' ? 'Erro' : 'Pendente'}
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Legenda */}
      <div className="mt-4 pt-3 border-t border-gray-700 flex items-center justify-center gap-4">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm bg-gradient-to-r from-blue-500 to-cyan-500" />
          <span className="text-[10px] text-gray-500">Em execução</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm bg-gradient-to-r from-green-500 to-emerald-500" />
          <span className="text-[10px] text-gray-500">Concluído</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm bg-gradient-to-r from-red-500 to-orange-500" />
          <span className="text-[10px] text-gray-500">Erro</span>
        </div>
      </div>
    </div>
  );
};
