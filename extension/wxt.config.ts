import { defineConfig } from 'wxt';

export default defineConfig({
  manifest: {
    name: 'PhishGuard',
    description: 'AI-Powered Phishing Detection & Real-Time Browser Protection',
    version: '1.0.0',
    permissions: [
      'webNavigation',
      'storage',
      'activeTab',
      'tabs',
    ],
    host_permissions: ['<all_urls>'],
  },
});
