'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Radio } from 'lucide-react';

interface ScanEvent {
  id: string;
  url: string;
  risk_level: 'safe' | 'suspicious' | 'malicious';
  risk_score: number;
  timestamp: string;
}

const riskColors: Record<string, string> = {
  safe: '#22C55E',
  suspicious: '#F59E0B',
  malicious: '#EF4444',
};

// Demo data generator
function generateDemoScan(): ScanEvent {
  const domains = [
    'https://login-secure-paypa1.com/verify',
    'https://www.google.com/search?q=test',
    'https://amaz0n-security.net/account',
    'https://github.com/user/repo',
    'https://microsoft-update.xyz/download',
    'https://stackoverflow.com/questions/12345',
    'https://dropbox-files.tk/share',
    'https://linkedin.com/in/user',
    'https://bankofamerica-login.ml/signin',
    'https://netflix.com/browse',
  ];
  const levels: ('safe' | 'suspicious' | 'malicious')[] = ['safe', 'safe', 'safe', 'suspicious', 'malicious', 'safe', 'malicious', 'safe', 'malicious', 'safe'];
  const idx = Math.floor(Math.random() * domains.length);

  return {
    id: Math.random().toString(36).substr(2, 9),
    url: domains[idx],
    risk_level: levels[idx],
    risk_score: levels[idx] === 'safe' ? Math.random() * 0.25 :
                levels[idx] === 'suspicious' ? 0.3 + Math.random() * 0.4 :
                0.75 + Math.random() * 0.25,
    timestamp: new Date().toISOString(),
  };
}

export default function LiveFeed() {
  const [events, setEvents] = useState<ScanEvent[]>([]);

  useEffect(() => {
    // Generate initial events
    const initial = Array.from({ length: 5 }, generateDemoScan);
    setEvents(initial);

    // Add new events periodically
    const interval = setInterval(() => {
      setEvents(prev => {
        const newEvent = generateDemoScan();
        return [newEvent, ...prev].slice(0, 20);
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '20px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Radio size={16} color="#EF4444" style={{ animation: 'pulse 2s infinite' }} />
          <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Live Scan Feed</h3>
        </div>
        <span className="micro-label">{events.length} events</span>
      </div>

      <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
        <AnimatePresence mode="popLayout">
          {events.map((event) => (
            <motion.div
              key={event.id}
              layout
              initial={{ scale: 0.95, opacity: 0, y: -10 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.25 }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 14px',
                borderRadius: '10px',
                marginBottom: '6px',
                background: 'rgba(15, 23, 42, 0.4)',
                border: `1px solid ${riskColors[event.risk_level]}20`,
                cursor: 'pointer',
                transition: 'border-color 0.15s',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1, minWidth: 0 }}>
                <div style={{
                  width: '8px', height: '8px',
                  borderRadius: '50%',
                  background: riskColors[event.risk_level],
                  flexShrink: 0,
                  boxShadow: `0 0 8px ${riskColors[event.risk_level]}40`,
                }} />
                <span className="mono" style={{
                  fontSize: '12px',
                  color: 'var(--text-secondary)',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}>
                  {event.url}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexShrink: 0 }}>
                <span className="mono" style={{
                  fontSize: '12px',
                  fontWeight: 600,
                  color: riskColors[event.risk_level],
                }}>
                  {(event.risk_score * 100).toFixed(1)}%
                </span>
                <span className={`badge badge-${event.risk_level}`} style={{ fontSize: '10px', padding: '2px 8px' }}>
                  {event.risk_level}
                </span>
                <span style={{ fontSize: '10px', color: 'var(--text-dim)' }}>
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      <style jsx global>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </div>
  );
}
