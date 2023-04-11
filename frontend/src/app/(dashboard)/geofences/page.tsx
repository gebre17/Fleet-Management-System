/**
 * Geofences page
 */
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useGeofence } from '@/hooks/useGeofence';
import { Geofence } from '@/types/geofence';

export default function GeofencesPage() {
  const { listGeofences } = useGeofence();
  const [geofences, setGeofences] = useState<Geofence[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchGeofences = async () => {
      try {
        const result = await listGeofences(0, 100);
        setGeofences(result.items);
      } catch (error) {
        console.error('Failed to fetch geofences:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchGeofences();
  }, [listGeofences]);

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Geofences</h1>
        <Link
          href="/geofences/create"
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition"
        >
          + Create Geofence
        </Link>
      </div>

      {isLoading ? (
        <p className="text-gray-600">Loading geofences...</p>
      ) : geofences.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 mb-4">No geofences yet</p>
          <Link
            href="/geofences/create"
            className="text-blue-600 hover:underline font-medium"
          >
            Create your first geofence
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {geofences.map((geofence) => (
            <div key={geofence.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-bold">{geofence.name}</h3>
                  <p className="text-gray-600 text-sm">{geofence.type}</p>
                </div>
                <div
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: geofence.color }}
                />
              </div>

              {geofence.description && (
                <p className="text-gray-600 text-sm mb-4">{geofence.description}</p>
              )}

              {geofence.type === 'circle' && (
                <div className="text-sm mb-4">
                  <p>
                    <span className="text-gray-600">Radius:</span>{' '}
                    {((geofence.radius_meters ?? 0) / 1000).toFixed(2)} km
                  </p>
                </div>
              )}

              <div className="flex space-x-2">
                <Link
                  href={`/geofences/${geofence.id}`}
                  className="flex-1 text-center px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition"
                >
                  Edit
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
