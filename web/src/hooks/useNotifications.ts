import { useState, useCallback } from 'react';
import type { Notification } from '../types';

interface UseNotificationsReturn {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearAll: () => void;
}

export function useNotifications(): UseNotificationsReturn {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = useCallback((
    notification: Omit<Notification, 'id' | 'timestamp'>
  ) => {
    const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newNotification: Notification = {
      ...notification,
      id,
      timestamp: new Date(),
      autoDismiss: notification.autoDismiss ?? true,
      duration: notification.duration ?? 5000
    };

    setNotifications(prev => [newNotification, ...prev]);

    // Auto-dismiss
    if (newNotification.autoDismiss && newNotification.duration) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll
  };
}

// Helper para criar notificações de eventos WebSocket
export function createNotificationFromEvent(
  eventType: string,
  eventData: Record<string, unknown>
): Omit<Notification, 'id' | 'timestamp'> | null {
  switch (eventType) {
    case 'team_execution_completed':
      return {
        type: 'success',
        title: 'Time Concluiu',
        message: `${formatTeamName(eventData.team as string)} finalizou o trabalho.`,
        autoDismiss: true,
        duration: 4000
      };

    case 'project_completed':
      return {
        type: 'success',
        title: 'Projeto Concluído!',
        message: 'Todos os times finalizaram suas tarefas.',
        autoDismiss: false
      };

    case 'project_error':
      return {
        type: 'error',
        title: 'Erro Detectado',
        message: (eventData.message as string) || 'Ocorreu um erro durante o processamento.',
        autoDismiss: false
      };

    case 'team_execution_started':
      return {
        type: 'info',
        title: 'Time Iniciou',
        message: `${formatTeamName(eventData.team as string)} começou a trabalhar.`,
        autoDismiss: true,
        duration: 3000
      };

    default:
      return null;
  }
}

function formatTeamName(teamId: string): string {
  const names: Record<string, string> = {
    'product_owner': 'Product Owner',
    'project_manager': 'Project Manager',
    'data_engineering': 'Engenharia de Dados',
    'data_science': 'Ciência de Dados',
    'governance': 'Governança',
    'observability': 'Observabilidade',
    'qa': 'Time de QA'
  };
  return names[teamId] || teamId.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}
