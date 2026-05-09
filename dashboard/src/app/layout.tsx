import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'PhishGuard — AI-Powered Phishing Detection Dashboard',
  description: 'Real-time phishing detection and browser protection analytics dashboard. Monitor threats, analyze scans, and protect your organization.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
