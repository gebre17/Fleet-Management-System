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
            View your API keys and manage access tokens for integrations.
          </p>
          <button className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-900 rounded-lg font-medium transition">
            Manage API Keys
          </button>
        </div>

        <hr />

        <div>
          <h2 className="text-xl font-bold mb-4">Notifications</h2>
          <div className="space-y-3">
            <label className="flex items-center">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="ml-3 text-gray-900">Email alerts for critical events</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="ml-3 text-gray-900">Daily activity summary</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}
