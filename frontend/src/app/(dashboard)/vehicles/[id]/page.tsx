/**
 * Vehicle detail page
 */
'use client';

import { useCallback, useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { useVehicleTracking } from '@/hooks/useVehicleTracking';
import { getApiClient } from '@/lib/api';
import { Vehicle } from '@/types/vehicle';
import { Location } from '@/types/location';
import { Alert, AlertListResponse } from '@/types/alert';
import { getVehicleStatusColor, getVehicleTypeIcon, formatSpeed, formatDate } from '@/lib/utils';

const LiveMap = dynamic(() => import('@/components/map/LiveMap'), { ssr: false });

export default function VehicleDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { getVehicle, getLatestLocation, deleteVehicle } = useVehicleTracking();

  const [vehicle, setVehicle] = useState<Vehicle | null>(null);
  const [location, setLocation] = useState<Location | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const api = getApiClient();
      const [vehicleData, alertsRes] = await Promise.all([
        getVehicle(params.id),
        api.get<AlertListResponse>('/api/v1/alerts', { params: { vehicle_id: params.id, limit: 20 } }),
      ]);
      setVehicle(vehicleData);
      setAlerts(alertsRes.data.items);

      try {
        const loc = await getLatestLocation(params.id);
        setLocation(loc ?? null);
      } catch {
        setLocation(null);
      }
    } catch (err) {
      console.error('Failed to load vehicle:', err);
      setError('Vehicle not found');
    } finally {
      setIsLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id]);

  useEffect(() => {
    load();
  }, [load]);

  const handleDelete = async () => {
    if (!confirm('Delete this vehicle? This also removes its location history and alerts.')) return;
    setIsDeleting(true);
    try {
      await deleteVehicle(params.id);
      router.push('/vehicles');
    } catch (err) {
      console.error('Failed to delete vehicle:', err);
      setError('Failed to delete vehicle');
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return <div className="p-8 text-gray-600">Loading...</div>;
  }

  if (error || !vehicle) {
    return (
      <div className="p-8">
        <p className="text-red-600 mb-4">{error ?? 'Vehicle not found'}</p>
        <Link href="/vehicles" className="text-blue-600 hover:underline">
          ← Back to Vehicles
        </Link>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <Link href="/vehicles" className="text-blue-600 hover:underline text-sm">
        ← Back to Vehicles
      </Link>

      <div className="flex justify-between items-start mt-2 mb-8">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <span>{getVehicleTypeIcon(vehicle.type)}</span>
            {vehicle.name}
          </h1>
          <p className="text-gray-600">{vehicle.plate_number}</p>
        </div>
        <span
          className="px-3 py-1 text-xs font-medium text-white rounded-full"
          style={{ backgroundColor: getVehicleStatusColor(vehicle.status) }}
        >
          {vehicle.status}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6 lg:col-span-1 space-y-3 text-sm">
          <h2 className="font-bold text-lg mb-2">Details</h2>
          <p><span className="text-gray-600">Type:</span> {vehicle.type}</p>
          {vehicle.make && <p><span className="text-gray-600">Make:</span> {vehicle.make}</p>}
          {vehicle.model && <p><span className="text-gray-600">Model:</span> {vehicle.model}</p>}
          {vehicle.year && <p><span className="text-gray-600">Year:</span> {vehicle.year}</p>}
          {vehicle.color && <p><span className="text-gray-600">Color:</span> {vehicle.color}</p>}
          {vehicle.device_id && <p><span className="text-gray-600">Device ID:</span> {vehicle.device_id}</p>}
          <p className="text-gray-500 text-xs pt-2">Added {formatDate(vehicle.created_at)}</p>

          <div className="pt-4 border-t space-y-2">
            {location && (
              <>
                <p><span className="text-gray-600">Speed:</span> {formatSpeed(location.speed)}</p>
                {location.battery_level != null && (
                  <p><span className="text-gray-600">Battery:</span> {location.battery_level}%</p>
                )}
                <p className="text-gray-500 text-xs">
                  Last seen {new Date(location.timestamp).toLocaleString()}
                </p>
              </>
            )}
            {!location && <p className="text-gray-500 text-xs">No location data yet</p>}
          </div>

          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="w-full mt-4 px-3 py-2 border border-red-300 text-red-600 hover:bg-red-50 disabled:opacity-50 text-sm rounded transition"
          >
            {isDeleting ? 'Deleting...' : 'Delete Vehicle'}
          </button>
        </div>

        <div className="lg:col-span-2 h-80 rounded-lg overflow-hidden border border-gray-200">
          {location ? (
            <LiveMap
              vehicles={[vehicle]}
              locations={{
                [vehicle.id]: {
                  type: 'location_update',
                  vehicle_id: vehicle.id,
                  latitude: location.latitude,
                  longitude: location.longitude,
                  speed: location.speed,
                  heading: location.heading,
                  battery_level: location.battery_level,
                  status: vehicle.status,
                  timestamp: location.timestamp,
                },
              }}
            />
          ) : (
            <div className="h-full w-full flex items-center justify-center bg-gray-100 text-gray-500 text-sm">
              No location data to show on the map yet
            </div>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="font-bold text-lg mb-4">Recent Alerts</h2>
        {alerts.length === 0 ? (
          <p className="text-gray-500 text-sm">No alerts for this vehicle yet.</p>
        ) : (
          <ul className="space-y-2">
            {alerts.map((alert) => (
              <li key={alert.id} className="text-sm border-b pb-2">
                <span className="font-medium">{alert.type}</span> — {alert.message}
                <span className="text-gray-500 text-xs ml-2">
                  {new Date(alert.triggered_at).toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
