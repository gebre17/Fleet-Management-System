/**
 * Create Vehicle page
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useVehicleTracking } from '@/hooks/useVehicleTracking';
import { VehicleCreate } from '@/types/vehicle';

export default function CreateVehiclePage() {
  const router = useRouter();
  const { createVehicle } = useVehicleTracking();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<VehicleCreate>({
    name: '',
    plate_number: '',
    type: 'car',
    make: '',
    model: '',
    year: undefined,
    device_id: '',
    color: '',
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'year' ? (value ? parseInt(value, 10) : undefined) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      // Remove empty optional fields
      const payload: Record<string, any> = { ...formData };
      Object.keys(payload).forEach((key) => {
        if (payload[key] === '' || payload[key] === undefined) {
          delete payload[key];
        }
      });

      await createVehicle(payload as VehicleCreate);
      router.push('/vehicles');
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'string') {
        setError(detail);
      } else if (Array.isArray(detail)) {
        setError(detail.map((d: any) => d.msg).join(', '));
      } else {
        setError('Failed to create vehicle');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <div className="mb-8">
        <Link
          href="/vehicles"
          className="text-blue-600 hover:underline text-sm"
        >
          ← Back to Vehicles
        </Link>
        <h1 className="text-3xl font-bold mt-2">Add Vehicle</h1>
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
            Vehicle Name *
          </label>
          <input
            id="name"
            name="name"
            type="text"
            required
            value={formData.name}
            onChange={handleChange}
            placeholder="e.g. Delivery Truck 1"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Plate Number */}
        <div>
          <label htmlFor="plate_number" className="block text-sm font-medium text-gray-700 mb-1">
            Plate Number *
          </label>
          <input
            id="plate_number"
            name="plate_number"
            type="text"
            required
            value={formData.plate_number}
            onChange={handleChange}
            placeholder="e.g. ABC-1234"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Type */}
        <div>
          <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-1">
            Vehicle Type *
          </label>
          <select
            id="type"
            name="type"
            required
            value={formData.type}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="car">Car</option>
            <option value="truck">Truck</option>
            <option value="motorcycle">Motorcycle</option>
            <option value="van">Van</option>
          </select>
        </div>

        {/* Make & Model - side by side */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="make" className="block text-sm font-medium text-gray-700 mb-1">
              Make
            </label>
            <input
              id="make"
              name="make"
              type="text"
              value={formData.make}
              onChange={handleChange}
              placeholder="e.g. Toyota"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-1">
              Model
            </label>
            <input
              id="model"
              name="model"
              type="text"
              value={formData.model}
              onChange={handleChange}
              placeholder="e.g. Hilux"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Year & Color - side by side */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="year" className="block text-sm font-medium text-gray-700 mb-1">
              Year
            </label>
            <input
              id="year"
              name="year"
              type="number"
              min="1900"
              max="2030"
              value={formData.year ?? ''}
              onChange={handleChange}
              placeholder="e.g. 2023"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label htmlFor="color" className="block text-sm font-medium text-gray-700 mb-1">
              Color
            </label>
            <input
              id="color"
              name="color"
              type="text"
              value={formData.color}
              onChange={handleChange}
              placeholder="e.g. White"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Device ID */}
        <div>
          <label htmlFor="device_id" className="block text-sm font-medium text-gray-700 mb-1">
            Tracker Device ID
          </label>
          <input
            id="device_id"
            name="device_id"
            type="text"
            value={formData.device_id}
            onChange={handleChange}
            placeholder="e.g. TRACK-001"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Submit */}
        <div className="flex space-x-4 pt-4">
          <button
            type="submit"
            disabled={isSubmitting}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 rounded-lg transition"
          >
            {isSubmitting ? 'Creating...' : 'Create Vehicle'}
          </button>
          <Link
            href="/vehicles"
            className="flex-1 text-center border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium py-2 rounded-lg transition"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
