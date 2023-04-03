/**
 * Alert types
 */
export interface Alert {
  id: string;
  vehicle_id: string;
  geofence_id?: string;
  type: 'geofence_enter' | 'geofence_exit' | 'speeding' | 'offline' | 'low_battery';
  severity: 'info' | 'warning' | 'critical';
  message: string;
  is_read: boolean;
  metadata?: Record<string, any>;
  triggered_at: string;
  created_at: string;
}

export interface AlertListResponse {
  total: number;
  items: Alert[];
}
