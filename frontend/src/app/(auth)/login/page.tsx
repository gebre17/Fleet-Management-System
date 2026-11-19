/**
 * Login page
 */
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error, isAuthenticated } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isDemoLoading, setIsDemoLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      router.push('/');
    } catch (err) {
      // Error handled by store
    }
  };

  const handleDemoLogin = async () => {
    setIsDemoLoading(true);
    setEmail('demo@trackfleet.com');
    setPassword('password123');
    try {
      await login('demo@trackfleet.com', 'password123');
      router.push('/');
    } catch (err) {
      // Error handled by store
    } finally {
      setIsDemoLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-xl p-8">
          <h1 className="text-3xl font-bold text-center mb-2">TrackFleet</h1>
          <p className="text-gray-600 text-center mb-8">Real-time Vehicle Tracking</p>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading || isDemoLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 rounded-lg transition"
            >
              {isLoading && !isDemoLoading ? 'Logging in...' : 'Log In'}
            </button>
          </form>

          {/* 1-Click Demo Login Button */}
          <div className="mt-5 pt-5 border-t border-gray-200">
            <button
              type="button"
              onClick={handleDemoLogin}
              disabled={isLoading || isDemoLoading}
              className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg shadow-sm transition"
            >
              <span>🚀</span>
              <span>{isDemoLoading ? 'Entering Demo...' : 'Explore as Demo User (1-Click)'}</span>
            </button>
            <p className="text-center text-xs text-gray-500 mt-2">
              Instant access with pre-loaded demo credentials (`demo@trackfleet.com`)
            </p>
          </div>

          <div className="mt-6 text-center">
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600 border border-gray-200">
              🔒 Public Portfolio Mode • Registration Closed
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
