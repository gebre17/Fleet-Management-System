/**
 * Create Geofence page
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useGeofence } from '@/hooks/useGeofence';
import { GeofenceCreate } from '@/types/geofence';

export default function CreateGeofencePage() {
  const router = useRouter();
  const { createGeofence } = useGeofence();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [geofenceType, setGeofenceType] = useState<'circle' | 'polygon'>('circle');
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    color: '#3B82F6',
    center_lat: '',
    center_lng: '',
    radius_meters: '',
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const payload: GeofenceCreate = {
        name: formData.name,
        type: geofenceType,
        color: formData.color,
      };

      if (formData.description) {
        payload.description = formData.description;
      }

      if (geofenceType === 'circle') {
        if (!formData.center_lat || !formData.center_lng || !formData.radius_meters) {
          setError('Center latitude, longitude and radius are required for circle geofences.');
          setIsSubmitting(false);
          return;
        }
        payload.center_lat = parseFloat(formData.center_lat);
        payload.center_lng = parseFloat(formData.center_lng);
        payload.radius_meters = parseFloat(formData.radius_meters);
      }

      await createGeofence(payload);
      router.push('/geofences');
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'string') {
        setError(detail);
      } else if (Array.isArray(detail)) {
        setError(detail.map((d: any) => d.msg).join(', '));
      } else {
        setError('Failed to create geofence');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <div className="mb-8">
        <Link
          href="/geofences"
          className="text-blue-600 hover:underline text-sm"
        >
          ← Back to Geofences
        </Link>
        <h1 className="text-3xl font-bold mt-2">Create Geofence</h1>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-6">
        {/* Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Geofence Name *
          </label>
          <input
            id="name"
            name="name"
            type="text"
            required
            value={formData.name}
            onChange={handleChange}
            placeholder="e.g. Warehouse Zone"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={3}
            placeholder="Optional description..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Geofence Type *
          </label>
          <div className="flex space-x-4">
            <button
              type="button"
              onClick={() => setGeofenceType('circle')}
              className={`flex-1 py-2 px-4 rounded-lg border-2 font-medium transition ${
                geofenceType === 'circle'
                  ? 'border-blue-600 bg-blue-50 text-blue-700'
                  : 'border-gray-300 text-gray-600 hover:border-gray-400'
              }`}
            >
              ⭕ Circle
            </button>
            <button
              type="button"
              onClick={() => setGeofenceType('polygon')}
              className={`flex-1 py-2 px-4 rounded-lg border-2 font-medium transition ${
                geofenceType === 'polygon'
                  ? 'border-blue-600 bg-blue-50 text-blue-700'
                  : 'border-gray-300 text-gray-600 hover:border-gray-400'
              }`}
            >
              🔷 Polygon
            </button>
          </div>
        </div>

        {/* Circle fields */}
        {geofenceType === 'circle' && (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="center_lat" className="block text-sm font-medium text-gray-700 mb-1">
                  Center Latitude *
                </label>
                <input
                  id="center_lat"
                  name="center_lat"
                  type="number"
                  step="any"
                  value={formData.center_lat}
                  onChange={handleChange}
                  placeholder="e.g. 9.0192"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label htmlFor="center_lng" className="block text-sm font-medium text-gray-700 mb-1">
                  Center Longitude *
                </label>
                <input
                  id="center_lng"
                  name="center_lng"
                  type="number"
                  step="any"
                  value={formData.center_lng}
                  onChange={handleChange}
                  placeholder="e.g. 38.7525"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div>
              <label htmlFor="radius_meters" className="block text-sm font-medium text-gray-700 mb-1">
                Radius (meters) *
              </label>
              <input
                id="radius_meters"
                name="radius_meters"
                type="number"
                step="any"
                min="1"
                value={formData.radius_meters}
                onChange={handleChange}
                placeholder="e.g. 500"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </>
        )}

        {/* Polygon note */}
        {geofenceType === 'polygon' && (
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 text-sm">
            Polygon geofences can be created visually on the Live Map. For now, please use the circle type or the API directly.
          </div>
        )}

        {/* Color */}
        <div>
          <label htmlFor="color" className="block text-sm font-medium text-gray-700 mb-1">
            Color
          </label>
          <div className="flex items-center space-x-3">
            <input
              id="color"
              name="color"
              type="color"
              value={formData.color}
              onChange={handleChange}
              className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
            />
            <span className="text-sm text-gray-500">{formData.color}</span>
          </div>
        </div>

        {/* Submit */}
        <div className="flex space-x-4 pt-4">
          <button
            type="submit"
            disabled={isSubmitting || geofenceType === 'polygon'}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 rounded-lg transition"
          >
            {isSubmitting ? 'Creating...' : 'Create Geofence'}
          </button>
          <Link
            href="/geofences"
            className="flex-1 text-center border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium py-2 rounded-lg transition"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
