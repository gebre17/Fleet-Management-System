/**
 * Geofence types
 */
export interface Geofence {
  id: string;
  owner_id: string;
  name: string;
  description?: string;
  type: 'circle' | 'polygon';
  center_lat?: number;
  center_lng?: number;
  radius_meters?: number;
  coordinates?: Array<[number, number]>;
  color: string;
  is_active: boolean;
  created_at: string;
}

export interface GeofenceCreate {
  name: string;
  description?: string;
  type: 'circle' | 'polygon';
  center_lat?: number;
  center_lng?: number;
  radius_meters?: number;
  coordinates?: Array<[number, number]>;
  color: string;
}

export interface GeofenceListResponse {
  total: number;
  items: Geofence[];
}

export interface GeofenceVehicleAssignment {
  vehicle_id: string;
  alert_on_enter: boolean;
  alert_on_exit: boolean;
}
