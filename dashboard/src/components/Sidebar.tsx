'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Shield, BarChart3, Search, Globe, FileText, Settings, Zap } from 'lucide-react';

const navItems = [
  { href: '/', label: 'Overview', icon: BarChart3 },
  { href: '/scans', label: 'Scan History', icon: Search },
  { href: '/threats', label: 'Threat Map', icon: Globe },
  { href: '/reports', label: 'Reports', icon: FileText },
];

export default function Sidebar({ activePage }: { activePage?: string }) {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        marginBottom: '40px',
        padding: '0 8px',
      }}>
        <div style={{
          width: '36px', height: '36px',
          background: 'linear-gradient(135deg, #6366F1, #8B5CF6)',
          borderRadius: '10px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Shield size={20} color="white" />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: '16px', color: 'var(--text-primary)' }}>
            PhishGuard
          </div>
          <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
            Security Dashboard
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1 }}>
        <div style={{
          fontSize: '10px', color: 'var(--text-dim)', textTransform: 'uppercase',
          letterSpacing: '0.15em', fontWeight: 600, padding: '0 12px', marginBottom: '12px',
        }}>
          Navigation
        </div>

        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '10px 12px',
                borderRadius: '10px',
                marginBottom: '4px',
                color: isActive ? 'var(--accent-primary)' : 'var(--text-secondary)',
                background: isActive ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
                fontSize: '14px',
                fontWeight: isActive ? 600 : 400,
                transition: 'all 0.15s ease',
                textDecoration: 'none',
              }}
            >
              <Icon size={18} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Status */}
      <div style={{
        padding: '12px',
        background: 'rgba(34, 197, 94, 0.08)',
        border: '1px solid rgba(34, 197, 94, 0.2)',
        borderRadius: '10px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
      }}>
        <Zap size={14} color="#22C55E" />
        <span style={{ fontSize: '12px', color: '#22C55E', fontWeight: 600 }}>
          System Active
        </span>
      </div>
    </aside>
  );
}
