/**
 * Vehicles page
 */
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useVehicleTracking } from '@/hooks/useVehicleTracking';
import { Vehicle } from '@/types/vehicle';
import { getVehicleStatusColor, formatDate } from '@/lib/utils';

export default function VehiclesPage() {
  const { listVehicles } = useVehicleTracking();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        const result = await listVehicles(0, 100);
        setVehicles(result.items);
      } catch (error) {
        console.error('Failed to fetch vehicles:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchVehicles();
  }, [listVehicles]);

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Vehicles</h1>
        <Link
          href="/vehicles/create"
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition"
        >
          + Add Vehicle
        </Link>
      </div>

      {isLoading ? (
        <p className="text-gray-600">Loading vehicles...</p>
      ) : vehicles.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 mb-4">No vehicles yet</p>
          <Link
            href="/vehicles/create"
            className="text-blue-600 hover:underline font-medium"
          >
            Create your first vehicle
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {vehicles.map((vehicle) => (
            <div key={vehicle.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-bold">{vehicle.name}</h3>
                  <p className="text-gray-600 text-sm">{vehicle.plate_number}</p>
                </div>
                <span
                  className="px-3 py-1 text-xs font-medium text-white rounded-full"
                  style={{ backgroundColor: getVehicleStatusColor(vehicle.status) }}
                >
                  {vehicle.status}
                </span>
              </div>

              <div className="space-y-2 text-sm mb-4">
                <p>
                  <span className="text-gray-600">Type:</span> {vehicle.type}
                </p>
                {vehicle.make && (
                  <p>
                    <span className="text-gray-600">Make:</span> {vehicle.make}
                  </p>
                )}
                {vehicle.model && (
                  <p>
                    <span className="text-gray-600">Model:</span> {vehicle.model}
                  </p>
                )}
                <p className="text-gray-500 text-xs">
                  Added {formatDate(vehicle.created_at)}
                </p>
              </div>

              <div className="flex space-x-2">
                <Link
                  href={`/vehicles/${vehicle.id}`}
                  className="flex-1 text-center px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition"
                >
                  View Details
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
