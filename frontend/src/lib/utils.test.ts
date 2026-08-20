import {
  getVehicleStatusColor,
  getVehicleTypeIcon,
  formatDistance,
  formatSpeed,
} from './utils';

describe('getVehicleStatusColor', () => {
  it('returns a distinct color per known status', () => {
    expect(getVehicleStatusColor('active')).toBe('#22c55e');
    expect(getVehicleStatusColor('idle')).toBe('#eab308');
    expect(getVehicleStatusColor('offline')).toBe('#6b7280');
    expect(getVehicleStatusColor('maintenance')).toBe('#ef4444');
  });

  it('falls back to gray for an unknown status', () => {
    expect(getVehicleStatusColor('bogus')).toBe('#6b7280');
  });
});

describe('getVehicleTypeIcon', () => {
  it('returns a fallback icon for an unknown type', () => {
    expect(getVehicleTypeIcon('spaceship')).toBe('🚗');
  });

  it('returns a distinct icon for each known type', () => {
    expect(getVehicleTypeIcon('truck')).toBe('🚚');
    expect(getVehicleTypeIcon('motorcycle')).toBe('🏍️');
  });
});

describe('formatDistance', () => {
  it('formats sub-kilometer distances in meters', () => {
    expect(formatDistance(250)).toBe('250 m');
  });

  it('formats distances >= 1km in kilometers with 2 decimals', () => {
    expect(formatDistance(1500)).toBe('1.50 km');
  });
});

describe('formatSpeed', () => {
  it('formats a numeric speed to one decimal', () => {
    expect(formatSpeed(45.678)).toBe('45.7 km/h');
  });

  it('returns N/A for missing speed', () => {
    expect(formatSpeed(undefined)).toBe('N/A');
  });
});
