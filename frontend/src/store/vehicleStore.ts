/**
 * Vehicle tracking store
 */
import { create } from 'zustand';
import { Vehicle } from '@/types/vehicle';
import { LocationUpdate } from '@/types/location';

interface VehicleStore {
  vehicles: Vehicle[];
  liveLocations: Record<string, LocationUpdate>;
  isFleetSocketConnected: boolean;
  setVehicles: (vehicles: Vehicle[]) => void;
  updateLocation: (vehicleId: string, location: LocationUpdate) => void;
  setFleetSocketConnected: (connected: boolean) => void;
  addVehicle: (vehicle: Vehicle) => void;
  removeVehicle: (vehicleId: string) => void;
}

export const useVehicleStore = create<VehicleStore>((set) => ({
  vehicles: [],
  liveLocations: {},
  isFleetSocketConnected: false,

  setVehicles: (vehicles) => set({ vehicles }),

  setFleetSocketConnected: (connected) => set({ isFleetSocketConnected: connected }),

  updateLocation: (vehicleId, location) =>
    set((state) => ({
      liveLocations: {
        ...state.liveLocations,
        [vehicleId]: location,
      },
    })),

  addVehicle: (vehicle) =>
    set((state) => ({
      vehicles: [...state.vehicles, vehicle],
    })),

  removeVehicle: (vehicleId) =>
    set((state) => ({
      vehicles: state.vehicles.filter((v) => v.id !== vehicleId),
    })),
}));
