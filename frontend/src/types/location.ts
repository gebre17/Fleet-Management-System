/**
 * Location types
 */
export interface Location {
  id: string;
  vehicle_id: string;
  latitude: number;
  longitude: number;
  altitude?: number;
  speed?: number;
  heading?: number;
  accuracy?: number;
  battery_level?: number;
  timestamp: string;
  created_at: string;
}

export interface LocationCreate {
  latitude: number;
  longitude: number;
  altitude?: number;
  speed?: number;
  heading?: number;
  accuracy?: number;
  battery_level?: number;
  timestamp?: string;
}

export interface LocationUpdate {
  type: 'location_update';
  vehicle_id: string;
  latitude: number;
  longitude: number;
  speed?: number;
  heading?: number;
  battery_level?: number;
  status?: 'active' | 'idle' | 'offline' | 'maintenance';
  timestamp: string;
}

export interface AlertMessage {
  type: 'alert';
  alert_id: string;
  vehicle_id: string;
  alert_type: string;
  severity: 'info' | 'warning' | 'critical';
  message: string;
  timestamp: string;
}

export interface LocationHistoryResponse {
  total: number;
  items: Location[];
}
