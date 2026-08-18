/**
 * Dashboard overview page
 */
'use client';

import { useEffect, useState } from 'react';
import { useVehicleTracking } from '@/hooks/useVehicleTracking';
import { getApiClient } from '@/lib/api';
import { Vehicle } from '@/types/vehicle';
import { Alert } from '@/types/alert';

export default function DashboardPage() {
  const { listVehicles } = useVehicleTracking();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [alertsToday, setAlertsToday] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const api = getApiClient();
        const [vehicleResult, alertResult] = await Promise.all([
          listVehicles(0, 100),
          api.get('/api/v1/alerts', { params: { limit: 100 } }),
        ]);
        setVehicles(vehicleResult.items);

        const startOfToday = new Date();
        startOfToday.setHours(0, 0, 0, 0);
        const todaysAlerts = (alertResult.data.items as Alert[]).filter(
          (alert) => new Date(alert.triggered_at) >= startOfToday
        );
        setAlertsToday(todaysAlerts.length);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [listVehicles]);

  const activeCount = vehicles.filter((v) => v.status === 'active').length;
  const offlineCount = vehicles.filter((v) => v.status === 'offline').length;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Total Vehicles</h3>
          <p className="text-3xl font-bold text-gray-900">{vehicles.length}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Active Now</h3>
          <p className="text-3xl font-bold text-green-600">{activeCount}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Offline</h3>
          <p className="text-3xl font-bold text-red-600">{offlineCount}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Alerts Today</h3>
          <p className="text-3xl font-bold text-orange-600">{isLoading ? '—' : alertsToday}</p>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Recent Vehicles</h2>
        
        {isLoading ? (
          <p className="text-gray-600">Loading...</p>
        ) : vehicles.length === 0 ? (
          <p className="text-gray-600">No vehicles yet. Create one to get started.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b">
                <tr>
                  <th className="text-left py-2 px-4">Name</th>
                  <th className="text-left py-2 px-4">Plate</th>
                  <th className="text-left py-2 px-4">Type</th>
                  <th className="text-left py-2 px-4">Status</th>
                </tr>
              </thead>
              <tbody>
                {vehicles.slice(0, 5).map((vehicle) => (
                  <tr key={vehicle.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">{vehicle.name}</td>
                    <td className="py-3 px-4">{vehicle.plate_number}</td>
                    <td className="py-3 px-4">{vehicle.type}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${
                          vehicle.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {vehicle.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
