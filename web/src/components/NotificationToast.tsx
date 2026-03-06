import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Info,
  X
} from 'lucide-react';
import type { Notification, NotificationType } from '../types';

interface NotificationToastProps {
  notifications: Notification[];
  onDismiss: (id: string) => void;
  maxVisible?: number;
}

const iconMap: Record<NotificationType, { icon: React.ElementType; color: string; bgColor: string; borderColor: string }> = {
  success: {
    icon: CheckCircle2,
    color: 'text-green-400',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30'
  },
  warning: {
    icon: AlertTriangle,
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/30'
  },
  error: {
    icon: XCircle,
    color: 'text-red-400',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30'
  },
  info: {
    icon: Info,
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30'
  }
};

export const NotificationToast: React.FC<NotificationToastProps> = ({
  notifications,
  onDismiss,
  maxVisible = 5
}) => {
  const visibleNotifications = notifications.slice(0, maxVisible);

  return (
    <div className="fixed top-20 right-4 z-50 flex flex-col gap-2 max-w-sm">
      <AnimatePresence initial={false}>
        {visibleNotifications.map((notification) => {
          const config = iconMap[notification.type];
          const IconComponent = config.icon;

          return (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, x: 50, scale: 0.9 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 50, scale: 0.9 }}
              transition={{ type: 'spring', stiffness: 500, damping: 30 }}
              className={`relative overflow-hidden rounded-lg border backdrop-blur-xl shadow-lg ${config.bgColor} ${config.borderColor}`}
            >
              <div className="flex items-start gap-3 p-3">
                {/* Ícone */}
                <div className={`shrink-0 ${config.color}`}>
                  <IconComponent className="w-5 h-5" />
                </div>

                {/* Conteúdo */}
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-white">
                    {notification.title}
                  </h4>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {notification.message}
                  </p>

                  {/* Ação customizada */}
                  {notification.action && (
                    <button
                      onClick={notification.action.onClick}
                      className={`mt-2 text-xs font-medium ${config.color} hover:underline`}
                    >
                      {notification.action.label}
                    </button>
                  )}
                </div>

                {/* Botão de fechar */}
                <button
                  onClick={() => onDismiss(notification.id)}
                  className="shrink-0 text-gray-500 hover:text-white transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Barra de progresso de auto-dismiss */}
              {notification.autoDismiss && notification.duration && (
                <motion.div
                  initial={{ scaleX: 1 }}
                  animate={{ scaleX: 0 }}
                  transition={{
                    duration: notification.duration / 1000,
                    ease: 'linear'
                  }}
                  className={`absolute bottom-0 left-0 right-0 h-0.5 origin-left ${
                    notification.type === 'success' ? 'bg-green-400' :
                      notification.type === 'warning' ? 'bg-yellow-400' :
                        notification.type === 'error' ? 'bg-red-400' :
                          'bg-blue-400'
                  }`}
                />
              )}
            </motion.div>
          );
        })}
      </AnimatePresence>

      {/* Indicador de mais notificações */}
      {notifications.length > maxVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center text-xs text-gray-500"
        >
          +{notifications.length - maxVisible} mais
        </motion.div>
      )}
    </div>
  );
};
