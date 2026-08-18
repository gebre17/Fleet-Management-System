/**
 * Live Map page — real-time fleet positions with geofence overlays.
 */
'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { useVehicleTracking } from '@/hooks/useVehicleTracking';
import { useGeofence } from '@/hooks/useGeofence';
import { useVehicleStore } from '@/store/vehicleStore';
import { Geofence } from '@/types/geofence';

const LiveMap = dynamic(() => import('@/components/map/LiveMap'), {
  ssr: false,
  loading: () => (
    <div className="h-full w-full flex items-center justify-center bg-gray-100 text-gray-500">
      Loading map...
    </div>
  ),
});

const STATUS_DOT: Record<string, string> = {
  active: 'bg-green-500',
  idle: 'bg-yellow-500',
  offline: 'bg-gray-400',
  maintenance: 'bg-orange-500',
};

export default function LiveMapPage() {
  const { listVehicles, getLatestLocation } = useVehicleTracking();
  const { listGeofences } = useGeofence();
  const { vehicles, liveLocations, isFleetSocketConnected, setVehicles, updateLocation } = useVehicleStore();
  const [geofences, setGeofences] = useState<Geofence[]>([]);
  const [selectedVehicleId, setSelectedVehicleId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [vehicleRes, geofenceRes] = await Promise.all([
          listVehicles(0, 100),
          listGeofences(0, 100),
        ]);
        setVehicles(vehicleRes.items);
        setGeofences(geofenceRes.items);

        await Promise.all(
          vehicleRes.items.map(async (vehicle) => {
            try {
              const location = await getLatestLocation(vehicle.id);
              if (location) {
                updateLocation(vehicle.id, {
                  type: 'location_update',
                  vehicle_id: vehicle.id,
                  latitude: location.latitude,
                  longitude: location.longitude,
                  speed: location.speed,
                  heading: location.heading,
                  battery_level: location.battery_level,
                  status: vehicle.status,
                  timestamp: location.timestamp,
                });
              }
            } catch {
              // Vehicle has no location history yet — fine, it just won't show a marker.
            }
          })
        );
      } finally {
        setIsLoading(false);
      }
    };

    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const vehiclesWithLocation = vehicles.filter((v) => liveLocations[v.id]);

  return (
    <div className="flex h-full">
      <aside className="w-80 flex-shrink-0 bg-white border-r overflow-y-auto">
        <div className="p-4 border-b flex items-center justify-between">
          <h2 className="font-bold text-lg">Fleet</h2>
          <span
            className={`flex items-center gap-1.5 text-xs font-medium ${
              isFleetSocketConnected ? 'text-green-600' : 'text-gray-400'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${isFleetSocketConnected ? 'bg-green-500' : 'bg-gray-300'}`} />
            {isFleetSocketConnected ? 'Live' : 'Connecting...'}
          </span>
        </div>

        {isLoading ? (
          <p className="p-4 text-gray-500 text-sm">Loading vehicles...</p>
        ) : vehicles.length === 0 ? (
          <p className="p-4 text-gray-500 text-sm">No vehicles yet. Add one to see it here.</p>
        ) : (
          <ul>
            {vehicles.map((vehicle) => {
              const location = liveLocations[vehicle.id];
              const status = location?.status ?? vehicle.status;
              return (
                <li key={vehicle.id}>
                  <button
                    onClick={() => setSelectedVehicleId(vehicle.id)}
                    disabled={!location}
                    className={`w-full text-left px-4 py-3 border-b hover:bg-gray-50 transition ${
                      selectedVehicleId === vehicle.id ? 'bg-blue-50' : ''
                    } ${!location ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${STATUS_DOT[status] ?? STATUS_DOT.offline}`} />
                      <span className="font-medium text-sm">{vehicle.name}</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {vehicle.plate_number}
                      {location?.speed != null ? ` · ${Math.round(location.speed)} km/h` : ''}
                      {!location ? ' · no location yet' : ''}
                    </p>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </aside>

      <div className="flex-1 relative">
        <LiveMap
          vehicles={vehiclesWithLocation}
          locations={liveLocations}
          geofences={geofences}
          selectedVehicleId={selectedVehicleId}
          onSelectVehicle={setSelectedVehicleId}
        />
      </div>
    </div>
  );
}
