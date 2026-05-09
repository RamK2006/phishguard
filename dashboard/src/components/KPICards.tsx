'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield, AlertTriangle, Activity, Clock } from 'lucide-react';

interface KPIData {
  totalScans: number;
  maliciousRate: number;
  avgLatency: number;
  activeThreats: number;
}

function useCountUp(end: number, duration: number = 1200): number {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime: number | null = null;
    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
      setCount(Math.round(eased * end));
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, [end, duration]);

  return count;
}

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
};

const item = {
  hidden: { y: 30, opacity: 0 },
  show: { y: 0, opacity: 1, transition: { duration: 0.35, ease: 'easeOut' } },
};

export default function KPICards() {
  const [data, setData] = useState<KPIData>({
    totalScans: 14892,
    maliciousRate: 12.4,
    avgLatency: 187,
    activeThreats: 34,
  });

  const totalScans = useCountUp(data.totalScans);
  const maliciousRate = useCountUp(data.maliciousRate * 10) / 10;
  const avgLatency = useCountUp(data.avgLatency);
  const activeThreats = useCountUp(data.activeThreats);

  const cards = [
    {
      title: 'Total Scans Today',
      value: totalScans.toLocaleString(),
      icon: Activity,
      color: '#6366F1',
      bgColor: 'rgba(99, 102, 241, 0.1)',
      change: '+23%',
      changeUp: true,
    },
    {
      title: 'Malicious Rate',
      value: `${maliciousRate}%`,
      icon: AlertTriangle,
      color: '#EF4444',
      bgColor: 'rgba(239, 68, 68, 0.1)',
      change: '-2.1%',
      changeUp: false,
    },
    {
      title: 'Avg Latency',
      value: `${avgLatency}ms`,
      icon: Clock,
      color: '#22C55E',
      bgColor: 'rgba(34, 197, 94, 0.1)',
      change: '-15ms',
      changeUp: false,
    },
    {
      title: 'Active Threats',
      value: activeThreats.toString(),
      icon: Shield,
      color: '#F59E0B',
      bgColor: 'rgba(245, 158, 11, 0.1)',
      change: '+5',
      changeUp: true,
    },
  ];

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '20px',
      }}
    >
      {cards.map((card, i) => {
        const Icon = card.icon;
        return (
          <motion.div
            key={i}
            variants={item}
            className="glass-card"
            style={{ padding: '24px', cursor: 'pointer' }}
          >
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '16px',
            }}>
              <span className="micro-label">{card.title}</span>
              <div style={{
                width: '36px', height: '36px',
                background: card.bgColor,
                borderRadius: '10px',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Icon size={18} color={card.color} />
              </div>
            </div>

            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '28px',
              fontWeight: 700,
              color: 'var(--text-primary)',
              marginBottom: '8px',
            }}>
              {card.value}
            </div>

            <div style={{
              fontSize: '12px',
              color: card.changeUp ? 'var(--risk-malicious)' : 'var(--risk-safe)',
              fontWeight: 600,
            }}>
              {card.change} vs yesterday
            </div>
          </motion.div>
        );
      })}
    </motion.div>
  );
}
