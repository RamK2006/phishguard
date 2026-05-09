'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X, ExternalLink } from 'lucide-react';
import Sidebar from '@/components/Sidebar';

interface ScanRecord {
  id: string;
  url: string;
  domain: string;
  risk_score: number;
  risk_level: 'safe' | 'suspicious' | 'malicious';
  source: string;
  latency_ms: number;
  created_at: string;
  explanation?: { risk_factors: string[]; summary: string };
}

const demoScans: ScanRecord[] = Array.from({ length: 25 }, (_, i) => {
  const domains = ['paypal-secure.tk', 'google.com', 'netflix-login.xyz', 'github.com', 'bank0famerica.ml', 'stackoverflow.com', 'amaz0n-verify.gq', 'linkedin.com', 'micros0ft-update.cf', 'reddit.com'];
  const levels: ('safe' | 'suspicious' | 'malicious')[] = ['malicious', 'safe', 'malicious', 'safe', 'malicious', 'safe', 'malicious', 'safe', 'suspicious', 'safe'];
  const idx = i % domains.length;
  return {
    id: `scan-${i}`,
    url: `https://${domains[idx]}/path/${Math.random().toString(36).substr(2, 6)}`,
    domain: domains[idx],
    risk_score: levels[idx] === 'safe' ? Math.random() * 0.25 : levels[idx] === 'suspicious' ? 0.4 + Math.random() * 0.3 : 0.78 + Math.random() * 0.2,
    risk_level: levels[idx],
    source: i % 3 === 0 ? 'extension' : 'api',
    latency_ms: 50 + Math.floor(Math.random() * 400),
    created_at: new Date(Date.now() - i * 300000).toISOString(),
    explanation: levels[idx] !== 'safe' ? {
      risk_factors: ['Suspicious TLD', 'Brand impersonation', 'New domain'],
      summary: 'This URL shows signs of phishing activity.',
    } : undefined,
  };
});

export default function ScansPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedScan, setSelectedScan] = useState<ScanRecord | null>(null);
  const [filterLevel, setFilterLevel] = useState<string>('all');

  const filtered = demoScans.filter(s => {
    if (filterLevel !== 'all' && s.risk_level !== filterLevel) return false;
    if (searchQuery && !s.url.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="dashboard-layout">
      <Sidebar activePage="scans" />
      <main className="main-content">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
          <h1 style={{ fontSize: '32px', fontWeight: 700, background: 'linear-gradient(135deg, #6366F1, #8B5CF6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '24px' }}>
            Scan History
          </h1>

          {/* Search & Filters */}
          <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <Search size={16} color="var(--text-dim)" style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }} />
              <input className="input" placeholder="Search URLs..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)} style={{ paddingLeft: '40px' }} />
            </div>
            {['all', 'safe', 'suspicious', 'malicious'].map(level => (
              <button key={level} onClick={() => setFilterLevel(level)} className={`btn ${filterLevel === level ? 'btn-primary' : 'btn-secondary'}`} style={{ textTransform: 'capitalize', fontSize: '13px' }}>
                {level}
              </button>
            ))}
          </div>

          {/* Table */}
          <div className="glass-card" style={{ overflow: 'hidden' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>URL</th>
                  <th>Risk Level</th>
                  <th>Score</th>
                  <th>Source</th>
                  <th>Latency</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(scan => (
                  <tr key={scan.id} onClick={() => setSelectedScan(scan)} style={{ cursor: 'pointer' }}>
                    <td>
                      <span className="mono" style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        {scan.url.length > 50 ? scan.url.slice(0, 50) + '...' : scan.url}
                      </span>
                    </td>
                    <td><span className={`badge badge-${scan.risk_level}`}>{scan.risk_level}</span></td>
                    <td><span className="mono" style={{ fontWeight: 600, color: scan.risk_level === 'safe' ? '#22C55E' : scan.risk_level === 'suspicious' ? '#F59E0B' : '#EF4444' }}>{(scan.risk_score * 100).toFixed(1)}%</span></td>
                    <td><span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{scan.source}</span></td>
                    <td><span className="mono" style={{ fontSize: '12px', color: scan.latency_ms < 200 ? '#22C55E' : '#F59E0B' }}>{scan.latency_ms}ms</span></td>
                    <td><span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>{new Date(scan.created_at).toLocaleString()}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* Detail Modal */}
        <AnimatePresence>
          {selectedScan && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              style={{ position: 'fixed', inset: 0, zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(8px)' }}
              onClick={() => setSelectedScan(null)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={e => e.stopPropagation()}
                className="glass-card"
                style={{ width: '560px', maxHeight: '80vh', overflow: 'auto', padding: '32px' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
                  <h3>Scan Details</h3>
                  <button onClick={() => setSelectedScan(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}><X size={20} /></button>
                </div>
                <div className="mono" style={{ fontSize: '13px', color: 'var(--text-secondary)', wordBreak: 'break-all', marginBottom: '16px', padding: '12px', background: 'var(--bg-surface)', borderRadius: '8px' }}>
                  {selectedScan.url}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
                  <div style={{ padding: '12px', background: 'var(--bg-surface)', borderRadius: '8px' }}>
                    <div className="micro-label" style={{ marginBottom: '4px' }}>Risk Score</div>
                    <div className="mono" style={{ fontSize: '24px', fontWeight: 700, color: selectedScan.risk_level === 'safe' ? '#22C55E' : '#EF4444' }}>{(selectedScan.risk_score * 100).toFixed(1)}%</div>
                  </div>
                  <div style={{ padding: '12px', background: 'var(--bg-surface)', borderRadius: '8px' }}>
                    <div className="micro-label" style={{ marginBottom: '4px' }}>Risk Level</div>
                    <span className={`badge badge-${selectedScan.risk_level}`}>{selectedScan.risk_level}</span>
                  </div>
                </div>
                {selectedScan.explanation && (
                  <div>
                    <div className="micro-label" style={{ marginBottom: '8px' }}>Risk Factors</div>
                    {selectedScan.explanation.risk_factors.map((f, i) => (
                      <div key={i} style={{ padding: '8px 12px', background: 'rgba(239,68,68,0.06)', borderRadius: '6px', marginBottom: '6px', fontSize: '13px', color: 'var(--text-secondary)' }}>• {f}</div>
                    ))}
                  </div>
                )}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
