/**
 * Live fleet map (Leaflet). Must be loaded via next/dynamic with
 * ssr: false — Leaflet touches `window` at import time.
 */
'use client';

import { useEffect, useMemo, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polygon, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { formatDistanceToNow } from 'date-fns';
import { Vehicle } from '@/types/vehicle';
import { LocationUpdate } from '@/types/location';
import { Geofence } from '@/types/geofence';
import { vehicleIcon, pickerIcon } from './icons';

const DEFAULT_CENTER: [number, number] = [9.03, 38.74]; // Addis Ababa — sane fallback with no data
const TILE_URL = process.env.NEXT_PUBLIC_MAP_TILE_URL || 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

interface LiveMapProps {
  vehicles: Vehicle[];
  locations: Record<string, LocationUpdate>;
  geofences?: Geofence[];
  selectedVehicleId?: string | null;
  onSelectVehicle?: (vehicleId: string) => void;
  pickMode?: boolean;
  pickedPosition?: [number, number] | null;
  onPick?: (lat: number, lng: number) => void;
  previewCircle?: { center: [number, number]; radiusMeters: number; color: string } | null;
  height?: string;
}

function FitToMarkers({ positions }: { positions: [number, number][] }) {
  const map = useMap();
  const didFit = useRef(false);

  useEffect(() => {
    if (didFit.current || positions.length === 0) return;
    didFit.current = true;

    if (positions.length === 1) {
      map.setView(positions[0], 14);
    } else {
      map.fitBounds(L.latLngBounds(positions), { padding: [40, 40] });
    }
  }, [positions, map]);

  return null;
}

function FlyToSelected({ position }: { position: [number, number] | null }) {
  const map = useMap();
  useEffect(() => {
    if (position) {
      map.flyTo(position, Math.max(map.getZoom(), 15), { duration: 0.75 });
    }
  }, [position, map]);
  return null;
}

function ClickPicker({ onPick }: { onPick: (lat: number, lng: number) => void }) {
  useMapEvents({
    click(e) {
      onPick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export default function LiveMap({
  vehicles,
  locations,
  geofences = [],
  selectedVehicleId = null,
  onSelectVehicle,
  pickMode = false,
  pickedPosition = null,
  onPick,
  previewCircle = null,
  height = '100%',
}: LiveMapProps) {
  const positions = useMemo(
    () =>
      vehicles
        .map((v) => locations[v.id])
        .filter((loc): loc is LocationUpdate => !!loc)
        .map((loc): [number, number] => [loc.latitude, loc.longitude]),
    [vehicles, locations]
  );

  const selectedLocation = selectedVehicleId ? locations[selectedVehicleId] : undefined;
  const selectedPosition: [number, number] | null = selectedLocation
    ? [selectedLocation.latitude, selectedLocation.longitude]
    : null;

  return (
    <MapContainer
      center={positions[0] ?? DEFAULT_CENTER}
      zoom={12}
      style={{ height, width: '100%' }}
      scrollWheelZoom
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url={TILE_URL}
      />

      <FitToMarkers positions={positions} />
      <FlyToSelected position={selectedPosition} />
      {pickMode && onPick && <ClickPicker onPick={onPick} />}

      {geofences
        .filter((g) => g.is_active)
        .map((g) =>
          g.type === 'circle' && g.center_lat != null && g.center_lng != null ? (
            <Circle
              key={g.id}
              center={[g.center_lat, g.center_lng]}
              radius={g.radius_meters ?? 0}
              pathOptions={{ color: g.color, fillColor: g.color, fillOpacity: 0.15 }}
            >
              <Popup>{g.name}</Popup>
            </Circle>
          ) : g.type === 'polygon' && g.coordinates ? (
            <Polygon
              key={g.id}
              positions={g.coordinates}
              pathOptions={{ color: g.color, fillColor: g.color, fillOpacity: 0.15 }}
            >
              <Popup>{g.name}</Popup>
            </Polygon>
          ) : null
        )}

      {vehicles.map((vehicle) => {
        const location = locations[vehicle.id];
        if (!location) return null;

        return (
          <Marker
            key={vehicle.id}
            position={[location.latitude, location.longitude]}
            icon={vehicleIcon(location.status ?? vehicle.status, location.heading, vehicle.id === selectedVehicleId)}
            eventHandlers={{
              click: () => onSelectVehicle?.(vehicle.id),
            }}
          >
            <Popup>
              <div className="text-sm space-y-1">
                <p className="font-semibold">{vehicle.name}</p>
                <p className="text-gray-600">{vehicle.plate_number}</p>
                <p>Speed: {location.speed != null ? `${Math.round(location.speed)} km/h` : '—'}</p>
                {location.battery_level != null && <p>Battery: {location.battery_level}%</p>}
                <p className="text-gray-500">
                  Updated {formatDistanceToNow(new Date(location.timestamp), { addSuffix: true })}
                </p>
              </div>
            </Popup>
          </Marker>
        );
      })}

      {pickedPosition && <Marker position={pickedPosition} icon={pickerIcon()} />}

      {previewCircle && previewCircle.radiusMeters > 0 && (
        <Circle
          center={previewCircle.center}
          radius={previewCircle.radiusMeters}
          pathOptions={{ color: previewCircle.color, fillColor: previewCircle.color, fillOpacity: 0.15, dashArray: '6' }}
        />
      )}
    </MapContainer>
  );
}
