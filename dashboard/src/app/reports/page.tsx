'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Download, Calendar, FileText, BarChart3, Database } from 'lucide-react';
import Sidebar from '@/components/Sidebar';

export default function ReportsPage() {
  const [dateRange, setDateRange] = useState({ start: '2026-05-02', end: '2026-05-09' });

  const metrics = [
    { label: 'Model Accuracy', value: '97.2%', icon: BarChart3, color: '#22C55E' },
    { label: 'F1 Score', value: '0.968', icon: BarChart3, color: '#6366F1' },
    { label: 'False Positive Rate', value: '1.4%', icon: BarChart3, color: '#F59E0B' },
    { label: 'Total Predictions', value: '142,891', icon: Database, color: '#8B5CF6' },
  ];

  return (
    <div className="dashboard-layout">
      <Sidebar activePage="reports" />
      <main className="main-content">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
          <h1 style={{ fontSize: '32px', fontWeight: 700, background: 'linear-gradient(135deg, #6366F1, #8B5CF6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '24px' }}>
            Reports & Export
          </h1>

          {/* Date Range */}
          <div className="glass-card" style={{ padding: '20px', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
            <Calendar size={18} color="var(--text-muted)" />
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input type="date" className="input" value={dateRange.start} onChange={e => setDateRange(p => ({ ...p, start: e.target.value }))} style={{ width: '160px' }} />
              <span style={{ color: 'var(--text-dim)' }}>to</span>
              <input type="date" className="input" value={dateRange.end} onChange={e => setDateRange(p => ({ ...p, end: e.target.value }))} style={{ width: '160px' }} />
            </div>
          </div>

          {/* Model Metrics */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
            {metrics.map((m, i) => {
              const Icon = m.icon;
              return (
                <motion.div
                  key={m.label}
                  className="glass-card"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  style={{ padding: '20px' }}
                >
                  <div className="micro-label" style={{ marginBottom: '8px' }}>{m.label}</div>
                  <div className="mono" style={{ fontSize: '24px', fontWeight: 700, color: m.color }}>{m.value}</div>
                </motion.div>
              );
            })}
          </div>

          {/* Export Options */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
            <motion.div className="glass-card" style={{ padding: '24px', cursor: 'pointer' }} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <div style={{ width: '40px', height: '40px', background: 'rgba(99,102,241,0.1)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <FileText size={20} color="#6366F1" />
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '15px' }}>STIX 2.1 Bundle</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Structured threat intelligence</div>
                </div>
              </div>
              <button className="btn btn-primary" style={{ width: '100%' }}>
                <Download size={14} /> Download STIX
              </button>
            </motion.div>

            <motion.div className="glass-card" style={{ padding: '24px', cursor: 'pointer' }} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <div style={{ width: '40px', height: '40px', background: 'rgba(34,197,94,0.1)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Database size={20} color="#22C55E" />
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '15px' }}>CSV Export</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Raw scan data export</div>
                </div>
              </div>
              <button className="btn btn-secondary" style={{ width: '100%' }}>
                <Download size={14} /> Export CSV
              </button>
            </motion.div>

            <motion.div className="glass-card" style={{ padding: '24px', cursor: 'pointer' }} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <div style={{ width: '40px', height: '40px', background: 'rgba(245,158,11,0.1)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <BarChart3 size={20} color="#F59E0B" />
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '15px' }}>Model Report</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Accuracy & evaluation</div>
                </div>
              </div>
              <button className="btn btn-secondary" style={{ width: '100%' }}>
                <Download size={14} /> Download PDF
              </button>
            </motion.div>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
