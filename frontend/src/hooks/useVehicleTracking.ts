/**
 * Custom hook for vehicle tracking operations
 */
import { useCallback } from 'react';
import { getApiClient } from '@/lib/api';
import { Vehicle, VehicleCreate, VehicleListResponse } from '@/types/vehicle';

export const useVehicleTracking = () => {
  const api = getApiClient();

  const listVehicles = useCallback(
    async (skip: number = 0, limit: number = 50): Promise<VehicleListResponse> => {
      const response = await api.get(`/api/v1/vehicles`, {
        params: { skip, limit },
      });
      return response.data;
    },
    [api]
  );

  const getVehicle = useCallback(
    async (vehicleId: string): Promise<Vehicle> => {
      const response = await api.get(`/api/v1/vehicles/${vehicleId}`);
      return response.data;
    },
    [api]
  );

  const createVehicle = useCallback(
    async (vehicleData: VehicleCreate): Promise<Vehicle> => {
      const response = await api.post('/api/v1/vehicles', vehicleData);
      return response.data;
    },
    [api]
  );

  const updateVehicle = useCallback(
    async (vehicleId: string, vehicleData: Partial<VehicleCreate>): Promise<Vehicle> => {
      const response = await api.put(`/api/v1/vehicles/${vehicleId}`, vehicleData);
      return response.data;
    },
    [api]
  );

  const deleteVehicle = useCallback(
    async (vehicleId: string): Promise<void> => {
      await api.delete(`/api/v1/vehicles/${vehicleId}`);
    },
    [api]
  );

  const getLatestLocation = useCallback(
    async (vehicleId: string) => {
      const response = await api.get(`/api/v1/tracking/${vehicleId}/location`);
      return response.data;
    },
    [api]
  );

  const getLocationHistory = useCallback(
    async (vehicleId: string, start?: string, end?: string, limit: number = 1000) => {
      const response = await api.get(`/api/v1/tracking/${vehicleId}/history`, {
        params: { start, end, limit },
      });
      return response.data;
    },
    [api]
  );

  return {
    listVehicles,
    getVehicle,
    createVehicle,
    updateVehicle,
    deleteVehicle,
    getLatestLocation,
    getLocationHistory,
  };
};
