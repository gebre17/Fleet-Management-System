/**
 * Sidebar component
 */
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { href: '/', label: 'Dashboard', icon: '📊' },
  { href: '/live-map', label: 'Live Map', icon: '🗺️' },
  { href: '/vehicles', label: 'Vehicles', icon: '🚗' },
  { href: '/geofences', label: 'Geofences', icon: '⭕' },
  { href: '/alerts', label: 'Alerts', icon: '🔔' },
  { href: '/reports', label: 'Reports', icon: '📈' },
  { href: '/settings', label: 'Settings', icon: '⚙️' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-gray-900 text-white shadow-lg">
      <div className="p-6">
        <h1 className="text-2xl font-bold">TrackFleet</h1>
        <p className="text-gray-400 text-sm">Vehicle Tracking</p>
      </div>

      <nav className="space-y-1 px-4 py-6">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
