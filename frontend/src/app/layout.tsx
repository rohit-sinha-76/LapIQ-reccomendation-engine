import React from 'react';
import type { Metadata } from 'next';
import { Geist, Inter } from 'next/font/google';
import './globals.css';

const geist = Geist({
  subsets: ['latin'],
  variable: '--font-geist',
  display: 'swap',
});

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'LapIQ — Laptop Purchase Intelligence Platform',
  description:
    'Deterministic laptop recommendations built from benchmarks, prices, and real reviews. Trusted by Students, Professionals, Gamers, and Creators across India.',
  keywords: 'laptop recommendations India, best laptop 2026, LapIQ',
  openGraph: {
    title: 'LapIQ — Laptop Purchase Intelligence',
    description: 'Stop comparing specs. Start making better decisions.',
    locale: 'en_IN',
    type: 'website',
  },
};

import { InteractiveMeshBackground } from '@/components/ui/InteractiveMeshBackground';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${geist.variable} ${inter.variable}`}>
      <body>
        <InteractiveMeshBackground />
        {children}
      </body>
    </html>
  );
}
