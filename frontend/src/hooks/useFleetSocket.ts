/**
 * Custom hook for the fleet-wide WebSocket feed (used by the live map).
 * Streams location updates and alerts for every vehicle the current
 * user owns over a single connection.
 */
import { useEffect, useRef, useState } from 'react';
import { TrackingWebSocket, LocationUpdate, AlertMessage } from '@/lib/websocket';
import { useVehicleStore } from '@/store/vehicleStore';
import { useAuthStore } from '@/store/authStore';
import { useAlertStore } from '@/store/alertStore';

/**
 * Opens the single, app-wide fleet WebSocket connection. Mounted once in
 * the dashboard layout — call sites that just need live data should read
 * `liveLocations` / `isFleetSocketConnected` off useVehicleStore instead
 * of calling this hook again, to avoid opening duplicate connections and
 * double-counting alerts.
 */
export const useFleetSocket = () => {
  const wsRef = useRef<TrackingWebSocket | null>(null);
  const { updateLocation, setFleetSocketConnected } = useVehicleStore();
  const addAlert = useAlertStore((state) => state.addAlert);
  const accessToken = useAuthStore((state) => state.accessToken);
  const [lastAlert, setLastAlert] = useState<AlertMessage | null>(null);

  useEffect(() => {
    if (!accessToken) return;

    const socket = new TrackingWebSocket();
    wsRef.current = socket;

    const handleMessage = (data: LocationUpdate | AlertMessage) => {
      if (data.type === 'location_update') {
        updateLocation(data.vehicle_id, data);
        setFleetSocketConnected(true);
      } else if (data.type === 'alert') {
        setLastAlert(data);
        addAlert({
          id: data.alert_id,
          vehicle_id: data.vehicle_id,
          type: data.alert_type as any,
          severity: data.severity,
          message: data.message,
          is_read: false,
          triggered_at: data.timestamp,
          created_at: data.timestamp,
        });
      }
    };

    socket.connect('/ws/fleet', accessToken, handleMessage, () => setFleetSocketConnected(false));
    setFleetSocketConnected(true);

    return () => {
      socket.disconnect();
      wsRef.current = null;
      setFleetSocketConnected(false);
    };
  }, [accessToken, updateLocation, addAlert, setFleetSocketConnected]);

  return { lastAlert };
};
