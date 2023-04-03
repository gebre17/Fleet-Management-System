/**
 * Live Map page (stub)
 */
'use client';

export default function LiveMapPage() {
  return (
    <div className="w-full h-screen bg-gray-100 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-4">Live Map</h1>
        <p className="text-gray-600 mb-6">
          Leaflet-based map component would be integrated here
        </p>
        <div className="bg-white rounded-lg shadow p-12 inline-block">
          <div className="w-96 h-96 bg-gray-200 rounded flex items-center justify-center">
            <p className="text-gray-500">
              🗺️ Interactive Map with Vehicle Markers & Geofences
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
