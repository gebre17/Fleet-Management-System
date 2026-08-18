/**
 * Header component
 */
'use client';

import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { useAlertStore } from '@/store/alertStore';

export default function Header() {
  const { user, logout } = useAuth();
  const unreadCount = useAlertStore((state) => state.unreadCount);

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="flex items-center justify-between px-8 py-4">
        <div>
          <p className="text-gray-600 text-sm">Welcome back,</p>
          <p className="text-lg font-semibold text-gray-900">{user?.full_name}</p>
        </div>

        <div className="flex items-center gap-4">
          <Link href="/alerts" className="relative text-2xl" title="Alerts">
            🔔
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </Link>

          <button
            onClick={logout}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
