/**
 * Leaflet marker icons.
 *
 * Built as inline-SVG divIcons instead of the default Leaflet marker
 * images — the default images reference a CDN path that webpack/Next.js
 * doesn't resolve out of the box, a very common "broken marker" bug.
 */
import L from 'leaflet';

const STATUS_COLORS: Record<string, string> = {
  active: '#22c55e',
  idle: '#eab308',
  offline: '#9ca3af',
  maintenance: '#f97316',
};

export function vehicleIcon(status: string | undefined, heading: number | undefined, selected: boolean): L.DivIcon {
  const color = STATUS_COLORS[status ?? 'offline'] ?? STATUS_COLORS.offline;
  const rotation = heading ?? 0;
  const ring = selected ? `<circle cx="16" cy="16" r="14" fill="none" stroke="${color}" stroke-width="2" opacity="0.4" />` : '';

  return L.divIcon({
    className: '',
    html: `
      <div style="width:32px;height:32px;transform:rotate(${rotation}deg);">
        <svg viewBox="0 0 32 32" width="32" height="32">
          ${ring}
          <circle cx="16" cy="16" r="10" fill="${color}" stroke="white" stroke-width="2" />
          <path d="M16 9 L20 18 L16 16 L12 18 Z" fill="white" />
        </svg>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16],
  });
}

export function pickerIcon(): L.DivIcon {
  return L.divIcon({
    className: '',
    html: `
      <svg viewBox="0 0 24 24" width="32" height="32">
        <path d="M12 2C7.6 2 4 5.6 4 10c0 6 8 12 8 12s8-6 8-12c0-4.4-3.6-8-8-8z" fill="#2563eb" stroke="white" stroke-width="1.5"/>
        <circle cx="12" cy="10" r="3" fill="white" />
      </svg>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  });
}
