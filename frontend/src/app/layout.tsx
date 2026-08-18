/**
 * Root layout
 */
'use client';

import { ReactNode, useEffect } from 'react';
import { initializeApiClient } from '@/lib/api';
import 'leaflet/dist/leaflet.css';
import './globals.css';

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  useEffect(() => {
    initializeApiClient();
  }, []);

  return (
    <html lang="en">
      <head>
        <title>TrackFleet</title>
        <meta name="description" content="Real-time vehicle tracking and fleet management" />
      </head>
      <body className="bg-white dark:bg-slate-950 text-gray-900 dark:text-white">
        {children}
      </body>
    </html>
  );
}
