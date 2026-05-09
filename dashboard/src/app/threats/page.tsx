'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Globe, MapPin } from 'lucide-react';
import Sidebar from '@/components/Sidebar';

interface ThreatOrigin {
  id: string;
  country: string;
  code: string;
  lat: number;
  lng: number;
  count: number;
  severity: 'high' | 'medium' | 'low';
}

const threatOrigins: ThreatOrigin[] = [
  { id: '1', country: 'Russia', code: 'RU', lat: 55.75, lng: 37.62, count: 342, severity: 'high' },
  { id: '2', country: 'China', code: 'CN', lat: 39.90, lng: 116.40, count: 289, severity: 'high' },
  { id: '3', country: 'Nigeria', code: 'NG', lat: 9.08, lng: 7.49, count: 198, severity: 'medium' },
  { id: '4', country: 'Brazil', code: 'BR', lat: -15.79, lng: -47.88, count: 156, severity: 'medium' },
  { id: '5', country: 'India', code: 'IN', lat: 28.61, lng: 77.21, count: 134, severity: 'medium' },
  { id: '6', country: 'Vietnam', code: 'VN', lat: 21.03, lng: 105.85, count: 112, severity: 'low' },
  { id: '7', country: 'Indonesia', code: 'ID', lat: -6.21, lng: 106.85, count: 98, severity: 'low' },
  { id: '8', country: 'Turkey', code: 'TR', lat: 39.93, lng: 32.86, count: 87, severity: 'low' },
  { id: '9', country: 'Ukraine', code: 'UA', lat: 50.45, lng: 30.52, count: 76, severity: 'low' },
  { id: '10', country: 'Pakistan', code: 'PK', lat: 33.69, lng: 73.04, count: 65, severity: 'low' },
];

const topBrands = [
  { name: 'PayPal', frequency: 89 },
  { name: 'Microsoft', frequency: 76 },
  { name: 'Google', frequency: 64 },
  { name: 'Apple', frequency: 58 },
  { name: 'Netflix', frequency: 45 },
  { name: 'Amazon', frequency: 42 },
  { name: 'Chase Bank', frequency: 38 },
  { name: 'Wells Fargo', frequency: 31 },
  { name: 'Instagram', frequency: 27 },
  { name: 'LinkedIn', frequency: 22 },
];

// Mercator projection helper
function project(lat: number, lng: number, width: number, height: number): [number, number] {
  const x = (lng + 180) / 360 * width;
  const latRad = lat * Math.PI / 180;
  const y = (1 - Math.log(Math.tan(latRad) + 1 / Math.cos(latRad)) / Math.PI) / 2 * height;
  return [x, y];
}

export default function ThreatsPage() {
  const MAP_W = 900;
  const MAP_H = 450;

  return (
    <div className="dashboard-layout">
      <Sidebar activePage="threats" />
      <main className="main-content">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
          <h1 style={{ fontSize: '32px', fontWeight: 700, background: 'linear-gradient(135deg, #6366F1, #8B5CF6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '24px' }}>
            Global Threat Map
          </h1>

          <div style={{ display: 'grid', gridTemplateColumns: '2.5fr 1fr', gap: '24px' }}>
            {/* World Map */}
            <div className="glass-card" style={{ padding: '24px', overflow: 'hidden' }}>
              <div style={{ position: 'relative', width: '100%', aspectRatio: '2/1', background: 'var(--bg-surface)', borderRadius: '12px', overflow: 'hidden' }}>
                {/* SVG World outline */}
                <svg viewBox={`0 0 ${MAP_W} ${MAP_H}`} style={{ width: '100%', height: '100%' }}>
                  {/* Grid lines */}
                  {Array.from({ length: 7 }, (_, i) => (
                    <line key={`h${i}`} x1={0} y1={i * MAP_H / 6} x2={MAP_W} y2={i * MAP_H / 6} stroke="rgba(99,102,241,0.06)" strokeWidth={0.5} />
                  ))}
                  {Array.from({ length: 13 }, (_, i) => (
                    <line key={`v${i}`} x1={i * MAP_W / 12} y1={0} x2={i * MAP_W / 12} y2={MAP_H} stroke="rgba(99,102,241,0.06)" strokeWidth={0.5} />
                  ))}

                  {/* Threat dots */}
                  {threatOrigins.map((t) => {
                    const [cx, cy] = project(t.lat, t.lng, MAP_W, MAP_H);
                    const r = Math.max(4, Math.sqrt(t.count) * 0.8);
                    const color = t.severity === 'high' ? '#EF4444' : t.severity === 'medium' ? '#F59E0B' : '#6366F1';
                    return (
                      <g key={t.id}>
                        {/* Pulse ring */}
                        <circle cx={cx} cy={cy} r={r * 2.5} fill="none" stroke={color} strokeWidth={0.5} opacity={0.3}>
                          <animate attributeName="r" from={r} to={r * 3} dur="2s" repeatCount="indefinite" />
                          <animate attributeName="opacity" from={0.4} to={0} dur="2s" repeatCount="indefinite" />
                        </circle>
                        {/* Main dot */}
                        <circle cx={cx} cy={cy} r={r} fill={color} opacity={0.8} style={{ filter: `drop-shadow(0 0 ${r}px ${color}40)` }}>
                          <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" repeatCount="indefinite" />
                        </circle>
                        {/* Label */}
                        <text x={cx + r + 4} y={cy + 4} fill="var(--text-secondary)" fontSize={10} fontFamily="var(--font-mono)">
                          {t.code}
                        </text>
                      </g>
                    );
                  })}
                </svg>
              </div>
            </div>

            {/* Brand Sidebar */}
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '16px' }}>
                Top Targeted Brands
              </h3>
              {topBrands.map((brand, i) => (
                <motion.div
                  key={brand.name}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.04 }}
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '8px 0',
                    borderBottom: i < topBrands.length - 1 ? '1px solid rgba(99,102,241,0.06)' : 'none',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', width: '20px' }}>{i + 1}</span>
                    <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{brand.name}</span>
                  </div>
                  <span className="mono" style={{ fontSize: '12px', fontWeight: 600, color: 'var(--accent-primary)' }}>{brand.frequency}</span>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
