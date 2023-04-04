/**
 * Alert store
 */
import { create } from 'zustand';
import { Alert } from '@/types/alert';

interface AlertStore {
  alerts: Alert[];
  unreadCount: number;
  setAlerts: (alerts: Alert[]) => void;
  addAlert: (alert: Alert) => void;
  markAsRead: (alertId: string) => void;
  clearAlerts: () => void;
}

export const useAlertStore = create<AlertStore>((set) => ({
  alerts: [],
  unreadCount: 0,

  setAlerts: (alerts) =>
    set({
      alerts,
      unreadCount: alerts.filter((a) => !a.is_read).length,
    }),

  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts],
      unreadCount: alert.is_read ? state.unreadCount : state.unreadCount + 1,
    })),

  markAsRead: (alertId) =>
    set((state) => ({
      alerts: state.alerts.map((a) =>
        a.id === alertId ? { ...a, is_read: true } : a
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),

  clearAlerts: () =>
    set({
      alerts: [],
      unreadCount: 0,
    }),
}));
