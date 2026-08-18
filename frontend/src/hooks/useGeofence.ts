/**
 * Custom hook for geofence operations
 */
import { useCallback } from 'react';
import { getApiClient } from '@/lib/api';
import { Geofence, GeofenceCreate, GeofenceListResponse, GeofenceVehicleAssignment } from '@/types/geofence';

export const useGeofence = () => {
  const api = getApiClient();

  const listGeofences = useCallback(
    async (skip: number = 0, limit: number = 50): Promise<GeofenceListResponse> => {
      const response = await api.get(`/api/v1/geofences`, {
        params: { skip, limit },
      });
      return response.data;
    },
    [api]
  );

  const getGeofence = useCallback(
    async (geofenceId: string): Promise<Geofence> => {
      const response = await api.get(`/api/v1/geofences/${geofenceId}`);
      return response.data;
    },
    [api]
  );

  const createGeofence = useCallback(
    async (geofenceData: GeofenceCreate): Promise<Geofence> => {
      const response = await api.post('/api/v1/geofences', geofenceData);
      return response.data;
    },
    [api]
  );

  const updateGeofence = useCallback(
    async (geofenceId: string, geofenceData: Partial<GeofenceCreate>): Promise<Geofence> => {
      const response = await api.put(`/api/v1/geofences/${geofenceId}`, geofenceData);
      return response.data;
    },
    [api]
  );

  const deleteGeofence = useCallback(
    async (geofenceId: string): Promise<void> => {
      await api.delete(`/api/v1/geofences/${geofenceId}`);
    },
    [api]
  );

  const listGeofenceVehicles = useCallback(
    async (geofenceId: string): Promise<GeofenceVehicleAssignment[]> => {
      const response = await api.get(`/api/v1/geofences/${geofenceId}/vehicles`);
      return response.data;
    },
    [api]
  );

  const assignVehicle = useCallback(
    async (
      geofenceId: string,
      vehicleId: string,
      alertOnEnter: boolean = true,
      alertOnExit: boolean = true
    ): Promise<void> => {
      await api.post(`/api/v1/geofences/${geofenceId}/vehicles`, {
        vehicle_id: vehicleId,
        alert_on_enter: alertOnEnter,
        alert_on_exit: alertOnExit,
      });
    },
    [api]
  );

  const unassignVehicle = useCallback(
    async (geofenceId: string, vehicleId: string): Promise<void> => {
      await api.delete(`/api/v1/geofences/${geofenceId}/vehicles/${vehicleId}`);
    },
    [api]
  );

  return {
    listGeofences,
    getGeofence,
    createGeofence,
    updateGeofence,
    deleteGeofence,
    listGeofenceVehicles,
    assignVehicle,
    unassignVehicle,
  };
};
