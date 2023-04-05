/**
 * Custom hook for WebSocket tracking
 */
import { useEffect, useRef } from 'react';
import { TrackingWebSocket, LocationUpdate } from '@/lib/websocket';
import { useVehicleStore } from '@/store/vehicleStore';

export const useWebSocket = (vehicleId: string) => {
  const wsRef = useRef<TrackingWebSocket | null>(null);
  const { updateLocation } = useVehicleStore();

  useEffect(() => {
    if (!vehicleId) return;

    wsRef.current = new TrackingWebSocket();

    const handleMessage = (data: LocationUpdate) => {
      updateLocation(vehicleId, data);
    };

    wsRef.current.connect(vehicleId, handleMessage);

    return () => {
      wsRef.current?.disconnect();
    };
  }, [vehicleId, updateLocation]);

  return wsRef.current;
};
