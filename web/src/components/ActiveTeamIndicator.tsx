import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Briefcase,
  BarChart3,
  Code2,
  Sparkles,
  Shield,
  Eye,
  TestTube,
  Layers,
  Server,
  Lock,
  Bot
} from 'lucide-react';
import { getTeamConfig } from '../types';

interface ActiveTeamIndicatorProps {
  teamId: string | null;
  currentAction?: string;
}

// Mapa de ícones
const iconMap: Record<string, React.ElementType> = {
  Briefcase,
  BarChart3,
  Code2,
  Sparkles,
  Shield,
  Eye,
  TestTube,
  Layers,
  Server,
  Lock,
  Bot
};

export const ActiveTeamIndicator: React.FC<ActiveTeamIndicatorProps> = ({
  teamId,
  currentAction
}) => {
  if (!teamId) return null;

  const teamConfig = getTeamConfig(teamId);
  const IconComponent = iconMap[teamConfig.icon] || Bot;

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={teamId}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.3 }}
        className={`bg-gray-800/50 rounded-xl p-4 backdrop-blur-sm border ${teamConfig.borderColor}`}
      >
        <div className="flex items-center gap-4">
          {/* Ícone animado */}
          <div className="relative">
            <motion.div
              animate={{
                scale: [1, 1.1, 1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut'
              }}
              className={`w-14 h-14 rounded-xl ${teamConfig.bgColor} flex items-center justify-center`}
            >
              <IconComponent className={`w-7 h-7 ${teamConfig.color}`} />
            </motion.div>

            {/* Pulso de atividade */}
            <motion.div
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.5, 0, 0.5]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut'
              }}
              className={`absolute inset-0 rounded-xl ${teamConfig.bgColor}`}
            />

            {/* Indicador de ativo */}
            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-gray-800 flex items-center justify-center">
              <motion.div
                animate={{ scale: [1, 0.8, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
                className="w-2 h-2 bg-green-300 rounded-full"
              />
            </div>
          </div>

          {/* Informações do time */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className={`text-sm font-semibold ${teamConfig.color}`}>
                {teamConfig.namePtBr}
              </span>
              <span className="text-xs text-gray-500">
                Trabalhando agora
              </span>
            </div>
            <p className="text-xs text-gray-400 mb-2">
              {teamConfig.description}
            </p>

            {/* Ação atual */}
            {currentAction && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center gap-2"
              >
                <motion.span
                  animate={{ opacity: [1, 0.5, 1] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="w-1.5 h-1.5 rounded-full bg-blue-400"
                />
                <span className="text-xs text-blue-300 truncate">
                  {currentAction}
                </span>
              </motion.div>
            )}
          </div>
        </div>

        {/* Barra de atividade animada */}
        <div className="mt-3 h-1 bg-gray-700 rounded-full overflow-hidden">
          <motion.div
            animate={{
              x: ['-100%', '100%']
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'linear'
            }}
            className={`h-full w-1/3 rounded-full bg-gradient-to-r ${
              teamConfig.color.includes('purple')
                ? 'from-purple-500 to-pink-500'
                : teamConfig.color.includes('blue')
                  ? 'from-blue-500 to-cyan-500'
                  : teamConfig.color.includes('green')
                    ? 'from-green-500 to-emerald-500'
                    : teamConfig.color.includes('yellow')
                      ? 'from-yellow-500 to-orange-500'
                      : teamConfig.color.includes('red')
                        ? 'from-red-500 to-pink-500'
                        : teamConfig.color.includes('cyan')
                          ? 'from-cyan-500 to-blue-500'
                          : teamConfig.color.includes('orange')
                            ? 'from-orange-500 to-red-500'
                            : 'from-gray-500 to-gray-400'
            }`}
          />
        </div>
      </motion.div>
    </AnimatePresence>
  );
};
