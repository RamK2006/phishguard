/**
 * PhishGuard — Background Service Worker
 *
 * Intercepts webNavigation.onBeforeNavigate,
 * maintains Bloom filter, calls /scan/url API,
 * sends result to content script.
 */

const API_BASE = 'http://localhost:8000';
const EXTENSION_KEY = 'phishguard-extension-dev';
const SCAN_TIMEOUT = 2000;

// In-memory cache of recent scan results
const scanCache = new Map<string, ScanResult>();
const MAX_CACHE_SIZE = 100;

// Known malicious URL set (synced from backend Bloom filter)
let maliciousUrlSet = new Set<string>();

interface ScanResult {
  scan_id: string;
  url: string;
  risk_score: number;
  risk_level: 'safe' | 'suspicious' | 'malicious';
  explanation: {
    risk_factors: string[];
    recommended_action: string;
    confidence: number;
    summary: string;
  };
  timestamp: string;
}

// ─── Bloom Filter Sync ───
async function syncBloomFilter(): Promise<void> {
  try {
    const resp = await fetch(`${API_BASE}/bloom/sync`, {
      headers: { 'Extension-Key': EXTENSION_KEY },
    });
    if (resp.ok) {
      const data = await resp.json();
      maliciousUrlSet = new Set(data.urls || []);
      console.log(`[PhishGuard] Bloom filter synced: ${maliciousUrlSet.size} entries`);
    }
  } catch (e) {
    console.warn('[PhishGuard] Bloom filter sync failed:', e);
  }
}

// Sync on startup and every 15 minutes
syncBloomFilter();
setInterval(syncBloomFilter, 15 * 60 * 1000);

// ─── Scan URL ───
async function scanUrl(url: string): Promise<ScanResult | null> {
  // Check cache first
  if (scanCache.has(url)) {
    return scanCache.get(url)!;
  }

  // Check local Bloom filter
  if (maliciousUrlSet.has(url)) {
    const blocked: ScanResult = {
      scan_id: 'bloom-filter-match',
      url,
      risk_score: 1.0,
      risk_level: 'malicious',
      explanation: {
        risk_factors: ['URL found in known malicious database'],
        recommended_action: 'Do not visit this URL. It has been identified as malicious.',
        confidence: 0.99,
        summary: 'This URL was found in the PhishGuard malicious URL database.',
      },
      timestamp: new Date().toISOString(),
    };
    return blocked;
  }

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), SCAN_TIMEOUT);

    const resp = await fetch(`${API_BASE}/api/v1/scan/url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Extension-Key': EXTENSION_KEY,
      },
      body: JSON.stringify({ url, source: 'extension' }),
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (resp.ok) {
      const result: ScanResult = await resp.json();

      // Cache result
      if (scanCache.size >= MAX_CACHE_SIZE) {
        const firstKey = scanCache.keys().next().value;
        if (firstKey) scanCache.delete(firstKey);
      }
      scanCache.set(url, result);

      // Store in chrome.storage.local for popup
      await storeRecentScan(result);

      return result;
    }
  } catch (e) {
    console.warn('[PhishGuard] Scan failed:', e);
  }

  return null;
}

// ─── Store Recent Scans ───
async function storeRecentScan(result: ScanResult): Promise<void> {
  try {
    const stored = await chrome.storage.local.get('recentScans');
    const scans: ScanResult[] = stored.recentScans || [];
    scans.unshift(result);
    if (scans.length > 50) scans.length = 50;
    await chrome.storage.local.set({ recentScans: scans });
  } catch (e) {
    console.warn('[PhishGuard] Storage error:', e);
  }
}

// ─── Navigation Listener ───
chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
  // Only process top-level navigations
  if (details.frameId !== 0) return;

  const url = details.url;

  // Skip internal URLs
  if (url.startsWith('chrome://') || url.startsWith('chrome-extension://') ||
      url.startsWith('about:') || url.startsWith('edge://')) {
    return;
  }

  // Check if scanning is paused
  const { scanPaused } = await chrome.storage.sync.get('scanPaused');
  if (scanPaused) return;

  const result = await scanUrl(url);

  if (result) {
    // Send result to content script
    try {
      await chrome.tabs.sendMessage(details.tabId, {
        type: 'PHISHGUARD_SCAN_RESULT',
        data: result,
      });
    } catch (e) {
      // Content script may not be ready yet
      console.debug('[PhishGuard] Content script not ready:', e);
    }

    // Update badge
    const badgeColor = result.risk_level === 'malicious' ? '#EF4444' :
                       result.risk_level === 'suspicious' ? '#F59E0B' : '#22C55E';
    const badgeText = result.risk_level === 'malicious' ? '!' :
                      result.risk_level === 'suspicious' ? '?' : '✓';

    chrome.action.setBadgeBackgroundColor({ color: badgeColor, tabId: details.tabId });
    chrome.action.setBadgeText({ text: badgeText, tabId: details.tabId });
  }
});

// ─── Message Listener (from popup/content scripts) ───
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_RECENT_SCANS') {
    chrome.storage.local.get('recentScans').then((stored) => {
      sendResponse(stored.recentScans || []);
    });
    return true;
  }

  if (message.type === 'SCAN_CURRENT_TAB') {
    chrome.tabs.query({ active: true, currentWindow: true }).then(async (tabs) => {
      if (tabs[0]?.url) {
        const result = await scanUrl(tabs[0].url);
        sendResponse(result);
      }
    });
    return true;
  }
});

export {};
