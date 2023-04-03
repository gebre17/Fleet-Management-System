/**
 * Vehicle types
 */
export interface Vehicle {
  id: string;
  user_id: string;
  name: string;
  plate_number: string;
  type: 'car' | 'truck' | 'motorcycle' | 'van';
  make?: string;
  model?: string;
  year?: number;
  device_id?: string;
  status: 'active' | 'idle' | 'offline' | 'maintenance';
  color?: string;
  created_at: string;
  updated_at: string;
}

export interface VehicleCreate {
  name: string;
  plate_number: string;
  type: 'car' | 'truck' | 'motorcycle' | 'van';
  make?: string;
  model?: string;
  year?: number;
  device_id?: string;
  color?: string;
}

export interface VehicleListResponse {
  total: number;
  items: Vehicle[];
}
