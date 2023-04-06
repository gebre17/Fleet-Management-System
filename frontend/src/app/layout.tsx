/**
 * Root layout
 */
'use client';

import { ReactNode, useEffect } from 'react';
import { initializeApiClient } from '@/lib/api';
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
      <body className="bg-white dark:bg-slate-950 text-gray-900 dark:text-white">
        {children}
      </body>
    </html>
  );
}
