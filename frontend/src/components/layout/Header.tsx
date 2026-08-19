/**
 * Header component
 */
'use client';

import { useAuth } from '@/hooks/useAuth';

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="flex items-center justify-between px-8 py-4">
        <div>
          <p className="text-gray-600 text-sm">Welcome back,</p>
          <p className="text-lg font-semibold text-gray-900">{user?.full_name}</p>
        </div>

        <button
          onClick={logout}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition"
        >
          Logou
        </button>
      </div>
    </header>
  );
}
