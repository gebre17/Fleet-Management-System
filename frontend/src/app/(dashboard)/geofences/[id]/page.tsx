/**
 * Geofence detail / edit page
 */
'use client';

import { useCallback, useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { useGeofence } from '@/hooks/useGeofence';
import { useVehicleTracking } from '@/hooks/useVehicleTracking';
import { logger } from '@/lib/logger';
import { Geofence, GeofenceVehicleAssignment } from '@/types/geofence';
import { Vehicle } from '@/types/vehicle';

const LiveMap = dynamic(() => import('@/components/map/LiveMap'), { ssr: false });

export default function GeofenceDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const {
    getGeofence,
    updateGeofence,
    deleteGeofence,
    listGeofenceVehicles,
    assignVehicle,
    unassignVehicle,
  } = useGeofence();
  const { listVehicles } = useVehicleTracking();

  const [geofence, setGeofence] = useState<Geofence | null>(null);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [assignments, setAssignments] = useState<GeofenceVehicleAssignment[]>([]);
  const [form, setForm] = useState({ name: '', description: '', color: '#3B82F6', is_active: true });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [assignmentBusy, setAssignmentBusy] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [geofenceData, vehiclesRes, assignedVehicles] = await Promise.all([
        getGeofence(params.id),
        listVehicles(0, 100),
        listGeofenceVehicles(params.id),
      ]);
      setGeofence(geofenceData);
      setVehicles(vehiclesRes.items);
      setAssignments(assignedVehicles);
      setForm({
        name: geofenceData.name,
        description: geofenceData.description ?? '',
        color: geofenceData.color,
        is_active: geofenceData.is_active,
      });
    } catch (err) {
      logger.error('GeofenceDetailPage', 'Failed to load geofence', { geofenceId: params.id, error: err });
      setError('Geofence not found');
    } finally {
      setIsLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id]);

  useEffect(() => {
    load();
  }, [load]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setError(null);
    try {
      const updated = await updateGeofence(params.id, form);
      setGeofence(updated);
    } catch (err) {
      logger.error('GeofenceDetailPage', 'Failed to update geofence', { geofenceId: params.id, error: err });
      setError('Failed to save changes');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Delete this geofence? Vehicle assignments will be removed too.')) return;
    setIsDeleting(true);
    try {
      await deleteGeofence(params.id);
      router.push('/geofences');
    } catch (err) {
      logger.error('GeofenceDetailPage', 'Failed to delete geofence', { geofenceId: params.id, error: err });
      setError('Failed to delete geofence');
      setIsDeleting(false);
    }
  };

  const toggleAssignment = async (vehicleId: string, isAssigned: boolean) => {
    setAssignmentBusy(vehicleId);
    try {
      if (isAssigned) {
        await unassignVehicle(params.id, vehicleId);
        setAssignments((prev) => prev.filter((a) => a.vehicle_id !== vehicleId));
      } else {
        await assignVehicle(params.id, vehicleId, true, true);
        setAssignments((prev) => [...prev, { vehicle_id: vehicleId, alert_on_enter: true, alert_on_exit: true }]);
      }
    } catch (err) {
      logger.error('GeofenceDetailPage', 'Failed to update vehicle assignment', {
        geofenceId: params.id,
        vehicleId,
        error: err,
      });
      setError('Failed to update vehicle assignment');
    } finally {
      setAssignmentBusy(null);
    }
  };

  if (isLoading) {
    return <div className="p-8 text-gray-600">Loading...</div>;
  }

  if (error && !geofence) {
    return (
      <div className="p-8">
        <p className="text-red-600 mb-4">{error}</p>
        <Link href="/geofences" className="text-blue-600 hover:underline">
          ← Back to Geofences
        </Link>
      </div>
    );
  }

  if (!geofence) return null;

  const assignedIds = new Set(assignments.map((a) => a.vehicle_id));

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <Link href="/geofences" className="text-blue-600 hover:underline text-sm">
        ← Back to Geofences
      </Link>
      <h1 className="text-3xl font-bold mt-2 mb-8">{geofence.name}</h1>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <form onSubmit={handleSave} className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="font-bold text-lg mb-2">Details</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              required
              value={form.name}
              onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={form.description}
              onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="flex items-center gap-3">
            <input
              type="color"
              value={form.color}
              onChange={(e) => setForm((prev) => ({ ...prev, color: e.target.value }))}
              className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
            />
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(e) => setForm((prev) => ({ ...prev, is_active: e.target.checked }))}
                className="rounded"
              />
              Active
            </label>
          </div>
          {geofence.type === 'circle' && (
            <p className="text-xs text-gray-500">
              Radius: {geofence.radius_meters} m — center/radius editing isn&apos;t supported yet; recreate the
              geofence to change them.
            </p>
          )}
          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={isSaving}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 rounded-lg transition"
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
            <button
              type="button"
              onClick={handleDelete}
              disabled={isDeleting}
              className="px-4 border border-red-300 text-red-600 hover:bg-red-50 disabled:opacity-50 rounded-lg transition"
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </form>

        <div className="h-80 lg:h-auto rounded-lg overflow-hidden border border-gray-200">
          <LiveMap
            vehicles={[]}
            locations={{}}
            geofences={[geofence]}
            previewCircle={
              geofence.type === 'circle' && geofence.center_lat != null && geofence.center_lng != null
                ? {
                    center: [geofence.center_lat, geofence.center_lng],
                    radiusMeters: geofence.radius_meters ?? 0,
                    color: geofence.color,
                  }
                : null
            }
          />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="font-bold text-lg mb-4">Assigned Vehicles</h2>
        {vehicles.length === 0 ? (
          <p className="text-gray-500 text-sm">No vehicles yet. Create one first.</p>
        ) : (
          <ul className="divide-y">
            {vehicles.map((vehicle) => {
              const isAssigned = assignedIds.has(vehicle.id);
              return (
                <li key={vehicle.id} className="py-3 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-sm">{vehicle.name}</p>
                    <p className="text-xs text-gray-500">{vehicle.plate_number}</p>
                  </div>
                  <button
                    onClick={() => toggleAssignment(vehicle.id, isAssigned)}
                    disabled={assignmentBusy === vehicle.id}
                    className={`px-3 py-1.5 text-sm rounded-lg font-medium transition disabled:opacity-50 ${
                      isAssigned
                        ? 'bg-red-50 text-red-600 hover:bg-red-100'
                        : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
                    }`}
                  >
                    {assignmentBusy === vehicle.id ? '...' : isAssigned ? 'Unassign' : 'Assign'}
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
