'use client';

import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';

const targetData = [
  { brand: 'PayPal', count: 342, color: '#6366F1' },
  { brand: 'Microsoft', count: 289, color: '#8B5CF6' },
  { brand: 'Google', count: 234, color: '#A78BFA' },
  { brand: 'Apple', count: 198, color: '#C4B5FD' },
  { brand: 'Netflix', count: 156, color: '#DDD6FE' },
  { brand: 'Amazon', count: 134, color: '#EDE9FE' },
];

export default function TopTargets() {
  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '20px' }}>
        Top Spoofed Brands
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {targetData.map((item, i) => {
          const maxCount = targetData[0].count;
          const widthPercent = (item.count / maxCount) * 100;

          return (
            <motion.div
              key={item.brand}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05, duration: 0.3 }}
              style={{ display: 'flex', alignItems: 'center', gap: '12px' }}
            >
              <span style={{
                width: '80px',
                fontSize: '13px',
                color: 'var(--text-secondary)',
                fontWeight: 500,
                flexShrink: 0,
              }}>
                {item.brand}
              </span>

              <div style={{
                flex: 1,
                height: '24px',
                background: 'rgba(15, 23, 42, 0.6)',
                borderRadius: '6px',
                overflow: 'hidden',
                position: 'relative',
              }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${widthPercent}%` }}
                  transition={{ duration: 0.8, delay: i * 0.05, ease: 'easeOut' }}
                  style={{
                    height: '100%',
                    background: `linear-gradient(90deg, ${item.color}40, ${item.color}80)`,
                    borderRadius: '6px',
                  }}
                />
              </div>

              <span className="mono" style={{
                fontSize: '13px',
                fontWeight: 600,
                color: item.color,
                width: '40px',
                textAlign: 'right',
                flexShrink: 0,
              }}>
                {item.count}
              </span>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
