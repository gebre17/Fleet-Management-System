/**
 * Register page — Public registration closed for portfolio mode.
 */
'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function RegisterPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-xl p-8 text-center">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl">
            🔒
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Registration Closed</h1>
          <p className="text-gray-600 mb-6 text-sm">
            Public user registration is disabled for this portfolio showcase to prevent unauthorized data modifications.
          </p>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-left mb-6">
            <h3 className="font-semibold text-blue-900 text-sm mb-1">Want to explore the app?</h3>
            <p className="text-xs text-blue-800">
              You can test all dashboard features, the live interactive map, and telematics using the pre-configured Demo Account.
            </p>
          </div>

          <Link
            href="/login"
            className="w-full inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg transition text-sm"
          >
            Go to Login & Explore Demo
          </Link>
        </div>
      </div>
    </div>
  );
}
