/**
 * Reports page
 */
'use client';

import { useEffect, useState } from 'react';
import { getApiClient } from '@/lib/api';

export default function ReportsPage() {
  const api = getApiClient();
  const [distanceReport, setDistanceReport] = useState<any[]>([]);
  const [activityReport, setActivityReport] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const [distance, activity] = await Promise.all([
          api.get('/api/v1/reports/distance'),
          api.get('/api/v1/reports/activity'),
        ]);
        
        setDistanceReport(distance.data);
        setActivityReport(activity.data);
      } catch (error) {
        console.error('Failed to fetch reports:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchReports();
  }, [api]);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Reports</h1>

      {isLoading ? (
        <p className="text-gray-600">Loading reports...</p>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Distance Report */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Distance Report</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b">
                  <tr>
                    <th className="text-left py-2">Vehicle</th>
                    <th className="text-right py-2">Distance</th>
                  </tr>
                </thead>
                <tbody>
                  {distanceReport.map((item) => (
                    <tr key={item.vehicle_id} className="border-b">
                      <td className="py-2">{item.vehicle_id}</td>
                      <td className="text-right">{item.total_km} km</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Activity Report */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Activity Report</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b">
                  <tr>
                    <th className="text-left py-2">Vehicle</th>
                    <th className="text-right py-2">Online Hours</th>
                  </tr>
                </thead>
                <tbody>
                  {activityReport.map((item) => (
                    <tr key={item.vehicle_id} className="border-b">
                      <td className="py-2">{item.vehicle_name}</td>
                      <td className="text-right">{item.online_hours} hrs</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
