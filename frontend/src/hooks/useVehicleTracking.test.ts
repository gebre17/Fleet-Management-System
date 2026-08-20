import { renderHook } from '@testing-library/react';
import { useVehicleTracking } from './useVehicleTracking';

const mockApi = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
};

jest.mock('@/lib/api', () => ({
  getApiClient: () => mockApi,
}));

describe('useVehicleTracking', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('listVehicles calls GET /api/v1/vehicles with pagination params', async () => {
    mockApi.get.mockResolvedValue({ data: { total: 0, items: [] } });
    const { result } = renderHook(() => useVehicleTracking());

    await result.current.listVehicles(10, 25);

    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/vehicles', {
      params: { skip: 10, limit: 25 },
    });
  });

  it('createVehicle POSTs the payload to /api/v1/vehicles', async () => {
    const payload = { name: 'Van', plate_number: 'AA-1', type: 'van' as const };
    mockApi.post.mockResolvedValue({ data: { id: '1', ...payload } });
    const { result } = renderHook(() => useVehicleTracking());

    await result.current.createVehicle(payload);

    expect(mockApi.post).toHaveBeenCalledWith('/api/v1/vehicles', payload);
  });

  it('deleteVehicle DELETEs the vehicle by id', async () => {
    mockApi.delete.mockResolvedValue({ data: undefined });
    const { result } = renderHook(() => useVehicleTracking());

    await result.current.deleteVehicle('vehicle-123');

    expect(mockApi.delete).toHaveBeenCalledWith('/api/v1/vehicles/vehicle-123');
  });

  it('getLocationHistory forwards start/end/limit as query params', async () => {
    mockApi.get.mockResolvedValue({ data: { total: 0, items: [] } });
    const { result } = renderHook(() => useVehicleTracking());

    await result.current.getLocationHistory('vehicle-123', '2026-01-01', '2026-01-02', 50);

    expect(mockApi.get).toHaveBeenCalledWith('/api/v1/tracking/vehicle-123/history', {
      params: { start: '2026-01-01', end: '2026-01-02', limit: 50 },
    });
  });
});
