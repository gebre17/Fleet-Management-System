import { logger } from './logger';

describe('logger', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('emits a structured entry with level, context, message, and timestamp', () => {
    const spy = jest.spyOn(console, 'error').mockImplementation(() => {});

    const entry = logger.error('VehicleDetailPage', 'Failed to load vehicle');

    expect(entry.level).toBe('error');
    expect(entry.context).toBe('VehicleDetailPage');
    expect(entry.message).toBe('Failed to load vehicle');
    expect(typeof entry.timestamp).toBe('string');
    expect(entry.meta).toBeUndefined();
    expect(spy).toHaveBeenCalledWith(expect.objectContaining({ level: 'error' }));
  });

  it('includes meta when provided', () => {
    jest.spyOn(console, 'warn').mockImplementation(() => {});

    const entry = logger.warn('GeofenceDetailPage', 'Assignment update failed', { vehicleId: 'v-1' });

    expect(entry.meta).toEqual({ vehicleId: 'v-1' });
  });

  it.each(['debug', 'info', 'warn', 'error'] as const)('routes %s to the matching console method', (level) => {
    const spy = jest.spyOn(console, level).mockImplementation(() => {});

    logger[level]('Context', 'message');

    expect(spy).toHaveBeenCalledTimes(1);
  });
});
