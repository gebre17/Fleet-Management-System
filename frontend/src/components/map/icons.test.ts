import { vehicleIcon, pickerIcon } from './icons';

describe('vehicleIcon', () => {
  it('colors the marker green for an active vehicle', () => {
    const icon = vehicleIcon('active', 0, false);
    expect(icon.options.html).toContain('#22c55e');
  });

  it('colors the marker gray for an offline vehicle', () => {
    const icon = vehicleIcon('offline', 0, false);
    expect(icon.options.html).toContain('#9ca3af');
  });

  it('falls back to the offline color for an unknown/missing status', () => {
    const icon = vehicleIcon(undefined, 0, false);
    expect(icon.options.html).toContain('#9ca3af');
  });

  it('rotates the marker to match heading', () => {
    const icon = vehicleIcon('active', 90, false);
    expect(icon.options.html).toContain('rotate(90deg)');
  });

  it('draws a selection ring only when selected', () => {
    const selected = vehicleIcon('active', 0, true);
    const unselected = vehicleIcon('active', 0, false);
    expect(selected.options.html).toContain('<circle');
    expect((unselected.options.html as string).match(/<circle/g)?.length).toBe(1);
    expect((selected.options.html as string).match(/<circle/g)?.length).toBe(2);
  });

  it('sets a centered 32x32 icon anchor', () => {
    const icon = vehicleIcon('active', 0, false);
    expect(icon.options.iconSize).toEqual([32, 32]);
    expect(icon.options.iconAnchor).toEqual([16, 16]);
  });
});

describe('pickerIcon', () => {
  it('anchors the pin at its bottom tip', () => {
    const icon = pickerIcon();
    expect(icon.options.iconAnchor).toEqual([16, 32]);
  });
});
