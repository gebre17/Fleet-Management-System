/**
 * Alerts page
 */
'use client';

import { useEffect, useState } from 'react';
import { getApiClient } from '@/lib/api';
import { AlertListResponse } from '@/types/alert';
import { useAlertStore } from '@/store/alertStore';
import { formatDate, formatTime } from '@/lib/utils';

export default function AlertsPage() {
  const api = getApiClient();
  const { alerts, unreadCount, setAlerts, markAsRead } = useAlertStore();
  const [isLoading, setIsLoading] = useState(true);
  const [isMarkingAll, setIsMarkingAll] = useState(false);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await api.get<AlertListResponse>('/api/v1/alerts', {
          params: { limit: 100 },
        });
        setAlerts(response.data.items);
      } catch (error) {
        console.error('Failed to fetch alerts:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAlerts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleMarkAsRead = async (alertId: string) => {
    markAsRead(alertId);
    try {
      await api.put(`/api/v1/alerts/${alertId}/read`);
    } catch (error) {
      console.error('Failed to mark alert as read:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    setIsMarkingAll(true);
    try {
      await api.put('/api/v1/alerts/read-all');
      setAlerts(alerts.map((a) => ({ ...a, is_read: true })));
    } catch (error) {
      console.error('Failed to mark all alerts as read:', error);
    } finally {
      setIsMarkingAll(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'info':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Alerts</h1>
        {unreadCount > 0 && (
          <button
            onClick={handleMarkAllAsRead}
            disabled={isMarkingAll}
            className="text-sm text-blue-600 hover:underline disabled:opacity-50"
          >
            {isMarkingAll ? 'Marking...' : `Mark all ${unreadCount} as read`}
          </button>
        )}
      </div>

      {isLoading ? (
        <p className="text-gray-600">Loading alerts...</p>
      ) : alerts.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600">No alerts</p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 border rounded-lg ${getSeverityColor(alert.severity)}`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="font-bold text-sm uppercase">{alert.type}</h3>
                  <p className="mt-1">{alert.message}</p>
                  <p className="text-xs mt-2 opacity-75">
                    {formatTime(alert.triggered_at)} • {formatDate(alert.triggered_at)}
                  </p>
                </div>
                {!alert.is_read && (
                  <button
                    onClick={() => handleMarkAsRead(alert.id)}
                    className="ml-4 flex items-center gap-1.5 text-xs font-medium opacity-75 hover:opacity-100"
                    title="Mark as read"
                  >
                    <span className="inline-block w-2 h-2 bg-current rounded-full"></span>
                    Mark read
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
