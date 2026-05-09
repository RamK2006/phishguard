'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Activity, AlertTriangle, Search, BarChart3, Globe, FileText, Settings, Zap } from 'lucide-react';
import Link from 'next/link';

import KPICards from '@/components/KPICards';
import LiveFeed from '@/components/LiveFeed';
import RiskChart from '@/components/RiskChart';
import TopTargets from '@/components/TopTargets';
import Sidebar from '@/components/Sidebar';

export default function DashboardPage() {
  return (
    <div className="dashboard-layout">
      <Sidebar activePage="overview" />

      <main className="main-content">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: 'easeOut' }}
        >
          {/* Header */}
          <div style={{ marginBottom: '32px' }}>
            <h1 style={{
              fontSize: '32px',
              fontWeight: 700,
              background: 'linear-gradient(135deg, #6366F1, #8B5CF6)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              marginBottom: '8px',
            }}>
              Dashboard Overview
            </h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              Real-time phishing detection analytics and threat monitoring
            </p>
          </div>

          {/* KPI Cards */}
          <KPICards />

          {/* Charts Row */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '2fr 1fr',
            gap: '24px',
            marginTop: '24px',
          }}>
            <RiskChart />
            <TopTargets />
          </div>

          {/* Live Feed */}
          <div style={{ marginTop: '24px' }}>
            <LiveFeed />
          </div>
        </motion.div>
      </main>
    </div>
  );
}
