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
  type: string;
  vehicle_id: string;
  latitude: number;
  longitude: number;
  speed?: number;
  heading?: number;
  timestamp: string;
}

export interface LocationHistoryResponse {
  total: number;
  items: Location[];
}
