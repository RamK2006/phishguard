'use client';

import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const chartData = [
  { day: 'Mon', safe: 2400, suspicious: 340, malicious: 120 },
  { day: 'Tue', safe: 2100, suspicious: 280, malicious: 95 },
  { day: 'Wed', safe: 2800, suspicious: 410, malicious: 150 },
  { day: 'Thu', safe: 2600, suspicious: 370, malicious: 130 },
  { day: 'Fri', safe: 3100, suspicious: 450, malicious: 180 },
  { day: 'Sat', safe: 1800, suspicious: 210, malicious: 60 },
  { day: 'Sun', safe: 1500, suspicious: 180, malicious: 45 },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: 'rgba(15, 23, 42, 0.95)',
        backdropFilter: 'blur(16px)',
        border: '1px solid rgba(99, 102, 241, 0.2)',
        borderRadius: '12px',
        padding: '12px 16px',
        boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
      }}>
        <p style={{ color: 'var(--text-primary)', fontWeight: 600, marginBottom: '8px', fontSize: '13px' }}>
          {label}
        </p>
        {payload.map((entry: any, i: number) => (
          <p key={i} style={{ color: entry.color, fontSize: '12px', fontFamily: 'var(--font-mono)', marginBottom: '2px' }}>
            {entry.name}: {entry.value.toLocaleString()}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function RiskChart() {
  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Risk Distribution — Last 7 Days</h3>
        <div style={{ display: 'flex', gap: '16px' }}>
          {[
            { label: 'Safe', color: '#22C55E' },
            { label: 'Suspicious', color: '#F59E0B' },
            { label: 'Malicious', color: '#EF4444' },
          ].map(l => (
            <div key={l.label} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: l.color }} />
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{l.label}</span>
            </div>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorSafe" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#22C55E" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#22C55E" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorSuspicious" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#F59E0B" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#F59E0B" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorMalicious" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#EF4444" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#EF4444" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.08)" />
          <XAxis dataKey="day" stroke="var(--text-dim)" fontSize={12} tickLine={false} axisLine={false} />
          <YAxis stroke="var(--text-dim)" fontSize={11} tickLine={false} axisLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Area type="monotone" dataKey="safe" stroke="#22C55E" fill="url(#colorSafe)" strokeWidth={2} animationDuration={1500} />
          <Area type="monotone" dataKey="suspicious" stroke="#F59E0B" fill="url(#colorSuspicious)" strokeWidth={2} animationDuration={1500} />
          <Area type="monotone" dataKey="malicious" stroke="#EF4444" fill="url(#colorMalicious)" strokeWidth={2} animationDuration={1500} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
