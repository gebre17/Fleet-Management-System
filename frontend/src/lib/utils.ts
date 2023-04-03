/**
 * Utility functions
 */
import { Vehicle } from '@/types/vehicle';

export const getVehicleStatusColor = (status: string): string => {
  switch (status) {
    case 'active':
      return '#22c55e'; // green
    case 'idle':
      return '#eab308'; // yellow
    case 'offline':
      return '#6b7280'; // gray
    case 'maintenance':
      return '#ef4444'; // red
    default:
      return '#6b7280';
  }
};

export const getVehicleTypeIcon = (type: string): string => {
  switch (type) {
    case 'car':
      return '🚗';
    case 'truck':
      return '🚚';
    case 'motorcycle':
      return '🏍️';
    case 'van':
      return '🚐';
    default:
      return '🚗';
  }
};

export const formatDistance = (meters: number): string => {
  if (meters >= 1000) {
    return `${(meters / 1000).toFixed(2)} km`;
  }
  return `${meters.toFixed(0)} m`;
};

export const formatSpeed = (kmh: number | undefined): string => {
  if (kmh === undefined || kmh === null) {
    return 'N/A';
  }
  return `${kmh.toFixed(1)} km/h`;
};

export const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString();
};

export const formatDate = (timestamp: string): string => {
  const date = new Date(timestamp);
  return date.toLocaleDateString();
};

export const calculateBearing = (
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number => {
  const dLon = lon2 - lon1;
  const y = Math.sin(dLon) * Math.cos(lat2);
  const x =
    Math.cos(lat1) * Math.sin(lat2) -
    Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
  const bearing = Math.atan2(y, x);
  return (bearing * 180) / Math.PI + 360;
};
