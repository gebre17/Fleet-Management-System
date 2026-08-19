/**
 * Settings page
 */
'use client';

import { useAuth } from '@/hooks/useAuth';

export default function SettingsPage() {
  const { user } = useAuth();

  return (
    <div className="p-8 max-w-2xl">
      <h1 className="text-3xl font-bold mb-8">Settings</h1>

      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        <div>
          <h2 className="text-xl font-bold mb-4">Profile</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name
              </label>
              <p className="text-gray-900">{user?.full_name}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <p className="text-gray-900">{user?.email}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Role
              </label>
              <p className="text-gray-900 capitalize">{user?.role}</p>
            </div>
          </div>
        </div>

        <hr />

        <div>
          <h2 className="text-xl font-bold mb-4">API Settings</h2>
          <p className="text-gray-600 text-sm mb-4">
            API key management for third-party integrations is coming soon.
          </p>
          <button
            disabled
            className="px-4 py-2 bg-gray-100 text-gray-400 rounded-lg font-medium cursor-not-allowed"
          >
            Manage API Keys (coming soon)
          </button>
        </div>

        <hr />

        <div>
          <h2 className="text-xl font-bold mb-4">Notifications</h2>
          <p className="text-gray-600 text-sm mb-4">
            Alerts are delivered live in the app and via the Alerts page. Email digests aren't available yet.
          </p>
          <div className="space-y-3 opacity-50">
            <label className="flex items-center">
              <input type="checkbox" disabled className="rounded" />
              <span className="ml-3 text-gray-900">Email alerts for critical events (coming soon)</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" disabled className="rounded" />
              <span className="ml-3 text-gray-900">Daily activity summary (coming soon)</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}
