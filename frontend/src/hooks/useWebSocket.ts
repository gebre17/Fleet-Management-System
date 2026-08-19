/**
 * Custom hook for WebSocket tracking of a single vehicle
 */
import { useEffect, useRef } from 'react';
import { TrackingWebSocket, LocationUpdate } from '@/lib/websocket';
import { useVehicleStore } from '@/store/vehicleStore';
import { useAuthStore } from '@/store/authStore';

export const useWebSocket = (vehicleId: string) => {
  const wsRef = useRef<TrackingWebSocket | null>(null);
  const { updateLocation } = useVehicleStore();
  const accessToken = useAuthStore((state) => state.accessToken);

  useEffect(() => {
    if (!vehicleId || !accessToken) return;

    wsRef.current = new TrackingWebSocket();

    const handleMessage = (data: any) => {
      if (data.type === 'location_update') {
        updateLocation(vehicleId, data as LocationUpdate);
      }
    };

    wsRef.current.connect(`/ws/${vehicleId}`, accessToken, handleMessage);

    return () => {
      wsRef.current?.disconnect();
    };
  }, [vehicleId, accessToken, updateLocation]);

  return wsRef.current;
};
