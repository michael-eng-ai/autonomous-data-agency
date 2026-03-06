import React, { useRef, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain,
  Zap,
  CheckCircle2,
  HelpCircle,
  Info,
  AlertCircle,
  Pause,
  Play,
  ChevronDown
} from 'lucide-react';
import type { ActivityMessage } from '../types';
import { getTeamConfig } from '../types';

interface LiveActivityFeedProps {
  activities: ActivityMessage[];
  maxVisible?: number;
  filterTeam?: string | null;
}

const activityIcons: Record<string, { icon: React.ElementType; color: string }> = {
  thinking: { icon: Brain, color: 'text-purple-400' },
  action: { icon: Zap, color: 'text-yellow-400' },
  result: { icon: CheckCircle2, color: 'text-green-400' },
  question: { icon: HelpCircle, color: 'text-blue-400' },
  info: { icon: Info, color: 'text-gray-400' },
  error: { icon: AlertCircle, color: 'text-red-400' }
};

export const LiveActivityFeed: React.FC<LiveActivityFeedProps> = ({
  activities,
  maxVisible = 50,
  filterTeam
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [newCount, setNewCount] = useState(0);
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Filtra atividades
  const filteredActivities = React.useMemo(() => {
    let filtered = activities;
    if (filterTeam) {
      filtered = filtered.filter(a => a.team === filterTeam);
    }
    return filtered.slice(0, maxVisible);
  }, [activities, filterTeam, maxVisible]);

  // Auto-scroll quando não pausado
  useEffect(() => {
    if (!isPaused && scrollRef.current && filteredActivities.length > 0) {
      scrollRef.current.scrollTop = 0;
      setNewCount(0);
    } else if (isPaused) {
      setNewCount(prev => prev + 1);
    }
  }, [filteredActivities, isPaused]);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  if (filteredActivities.length === 0) {
    return (
      <div className="bg-gray-800/50 rounded-xl p-4 backdrop-blur-sm border border-gray-700">
        <div className="flex items-center gap-2 mb-3">
          <Zap className="w-4 h-4 text-yellow-400" />
          <span className="text-sm font-medium text-gray-300">Atividade em Tempo Real</span>
        </div>
        <div className="text-center py-6 text-gray-500 text-sm">
          Aguardando atividades...
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800/50 rounded-xl backdrop-blur-sm border border-gray-700 overflow-hidden">
      {/* Header */}
      <div
        className="flex items-center justify-between p-3 border-b border-gray-700 cursor-pointer hover:bg-gray-700/30 transition-colors"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-400" />
          <span className="text-sm font-medium text-gray-300">Atividade em Tempo Real</span>
          <span className="text-xs text-gray-500">({filteredActivities.length})</span>
        </div>

        <div className="flex items-center gap-2">
          {/* Controle de pausa */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsPaused(!isPaused);
              if (isPaused) setNewCount(0);
            }}
            className={`p-1.5 rounded-lg transition-colors ${
              isPaused
                ? 'bg-yellow-500/20 text-yellow-400'
                : 'bg-gray-700/50 text-gray-400 hover:text-white'
            }`}
            title={isPaused ? 'Retomar auto-scroll' : 'Pausar auto-scroll'}
          >
            {isPaused ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
          </button>

          {/* Badge de novas mensagens */}
          {isPaused && newCount > 0 && (
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="px-2 py-0.5 bg-blue-500 text-white text-xs rounded-full"
            >
              +{newCount}
            </motion.span>
          )}

          <ChevronDown
            className={`w-4 h-4 text-gray-500 transition-transform ${isCollapsed ? '' : 'rotate-180'}`}
          />
        </div>
      </div>

      {/* Feed */}
      <AnimatePresence>
        {!isCollapsed && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: 'auto' }}
            exit={{ height: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div
              ref={scrollRef}
              className="max-h-48 overflow-y-auto custom-scrollbar"
            >
              <AnimatePresence initial={false}>
                {filteredActivities.map((activity) => {
                  const teamConfig = getTeamConfig(activity.team);
                  const activityConfig = activityIcons[activity.type] || activityIcons.info;
                  const IconComponent = activityConfig.icon;

                  return (
                    <motion.div
                      key={activity.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ duration: 0.2 }}
                      className={`flex items-start gap-2 p-2 border-l-2 ${teamConfig.borderColor} hover:bg-gray-700/20 transition-colors`}
                    >
                      {/* Ícone do tipo */}
                      <div className={`shrink-0 mt-0.5 ${activityConfig.color}`}>
                        <IconComponent className="w-3.5 h-3.5" />
                      </div>

                      {/* Conteúdo */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-0.5">
                          <span className={`text-xs font-medium ${teamConfig.color}`}>
                            {teamConfig.namePtBr}
                          </span>
                          <span className="text-[10px] text-gray-600">
                            {formatTime(activity.timestamp)}
                          </span>
                        </div>
                        <p className="text-xs text-gray-400 leading-relaxed">
                          {activity.message}
                        </p>
                      </div>
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
